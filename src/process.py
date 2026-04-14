import os
import cv2
import numpy as np
from aco_edge import AntColonyEdgeDetector
from tqdm import tqdm
import glob
import argparse

def parse_bsds_segmentation_file(segmentation_path, height, width):
    segmentation_map = np.zeros((height, width), dtype=np.int32)
    
    try:
        with open(segmentation_path, 'r') as file_handle:
            file_lines = file_handle.readlines()
        
        is_data_section = False
        for line in file_lines:
            line_content = line.strip()
            
            if not line_content: continue
            
            if line_content == 'data':
                is_data_section = True
                continue
            
            if not is_data_section:
                continue
            
            parts = line_content.split()
            if len(parts) != 4: continue
            
            segment_id = int(parts[0])
            row_idx = int(parts[1])
            col_start_idx = int(parts[2])
            col_end_idx = int(parts[3])
            
            if row_idx < height:
                start_col = max(0, col_start_idx)
                end_col = min(width, col_end_idx + 1)
                
                segmentation_map[row_idx, start_col:end_col] = segment_id
                
    except Exception as error:
        print(f"Error reading segmentation file {segmentation_path}: {error}")
        return np.zeros((height, width), dtype=np.int32)

    return segmentation_map

def convert_labels_to_edges(label_map):
    label_map_float = label_map.astype(np.float32)
    
    gradient_x = cv2.Sobel(label_map_float, cv2.CV_32F, 1, 0, ksize=1)
    gradient_y = cv2.Sobel(label_map_float, cv2.CV_32F, 0, 1, ksize=1)
    
    gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
    
    binary_edges = (gradient_magnitude > 0).astype(np.uint8) * 255
    return binary_edges

def find_human_annotation_path(image_name, human_annotations_base_dir):
    search_pattern = os.path.join(human_annotations_base_dir, 'gray', '*', f"{image_name}.seg")
    matching_files = glob.glob(search_pattern)
    
    if matching_files:
        return matching_files[0] 
    return None

def compute_sobel_edges(grayscale_image):
    """Compute Sobel edge detection for comparison."""
    gradient_x = cv2.Sobel(grayscale_image, cv2.CV_64F, 1, 0, ksize=3)
    gradient_y = cv2.Sobel(grayscale_image, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
    magnitude = np.clip(magnitude / magnitude.max() * 255, 0, 255).astype(np.uint8)
    return magnitude

def compute_canny_edges(grayscale_image, low_threshold=50, high_threshold=150):
    """Compute Canny edge detection for comparison."""
    blurred = cv2.GaussianBlur(grayscale_image, (5, 5), 1.4)
    return cv2.Canny(blurred, low_threshold, high_threshold)

def process_images_batch(input_directory, output_directory, human_annotations_directory,
                         max_images=None, include_comparison=False):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    image_files = sorted([f for f in os.listdir(input_directory) if f.lower().endswith(valid_extensions)])
    
    if max_images is not None:
        image_files = image_files[:max_images]
    
    print(f"Processing {len(image_files)} images from {input_directory}...")
    if include_comparison:
        print("  Including Sobel and Canny comparison panels.")

    for image_filename in tqdm(image_files):
        input_image_path = os.path.join(input_directory, image_filename)
        image_name_no_ext = os.path.splitext(image_filename)[0]
        
        output_filename = image_name_no_ext + '.png'
        output_image_path = os.path.join(output_directory, output_filename)

        try:
            original_image = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
            if original_image is None:
                print(f"Failed to load image: {image_filename}")
                continue
            
            height, width = original_image.shape
            
            segmentation_file_path = find_human_annotation_path(image_name_no_ext, human_annotations_directory)
            human_edge_map = np.zeros((height, width), dtype=np.uint8)
            
            if segmentation_file_path:
                try:
                    segmentation_labels = parse_bsds_segmentation_file(segmentation_file_path, height, width)
                    human_edge_map = convert_labels_to_edges(segmentation_labels)
                except Exception as error:
                    print(f"Error parsing segmentation file for {image_name_no_ext}: {error}")
            
            aco_detector = AntColonyEdgeDetector(input_image_path, num_iterations=50, num_ants=8192) 
            aco_generated_edge_map = aco_detector.run_detection()
            
            separator_width = 10
            separator_line = np.ones((height, separator_width), dtype=np.uint8) * 128
            
            # Build panels list
            panels = [original_image, separator_line, human_edge_map, separator_line, aco_generated_edge_map]
            labels = ["Original", "Human Edge", "ACO Edge"]
            
            if include_comparison:
                sobel_edges = compute_sobel_edges(original_image)
                canny_edges = compute_canny_edges(original_image)
                panels.extend([separator_line, sobel_edges, separator_line, canny_edges])
                labels.extend(["Sobel", "Canny"])
            
            dashboard_layout_gray = np.hstack(panels)
            dashboard_visualization = cv2.cvtColor(dashboard_layout_gray, cv2.COLOR_GRAY2BGR)
            
            font_face = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            text_color = (0, 0, 255) 
            text_thickness = 2
            
            # Draw labels dynamically
            x_offset = 0
            for label in labels:
                cv2.putText(dashboard_visualization, label, (x_offset + 10, 30), font_face, font_scale, text_color, text_thickness)
                x_offset += width + separator_width

            cv2.imwrite(output_image_path, dashboard_visualization)
            
        except Exception as error:
            print(f"Error processing image {image_filename}: {error}")

def main():
    parser = argparse.ArgumentParser(
        description="ACO Edge Detection — Batch Processing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python process_images.py                    # Process all 300 images
  uv run python process_images.py -n 10              # Process first 10 images only
  uv run python process_images.py --compare           # Include Sobel & Canny comparison
  uv run python process_images.py -n 5 --compare -o results/
        """
    )
    parser.add_argument("-n", "--max-images", type=int, default=None,
                        help="Maximum number of images to process (default: all)")
    parser.add_argument("-o", "--output-dir", type=str, default=None,
                        help="Output directory (default: ./output)")
    parser.add_argument('-i', '--images-dir', type=str, default='data/images',
                        help="Output directory (default: ./output)")
    parser.add_argument('-s', '--seg-dir', type=str, default='data/human',
                        help="Output directory (default: ./output)")
    parser.add_argument("--compare", action="store_true",
                        help="Include Sobel and Canny edge maps in dashboard")
    args = parser.parse_args()

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(current_script_dir, 'images')
    human_annotations_dir = os.path.join(current_script_dir, 'human')
    output_dir = args.output_dir or os.path.join(current_script_dir, 'output')

    if os.path.exists(images_dir):
        process_images_batch(images_dir, output_dir, human_annotations_dir,
                             max_images=args.max_images,
                             include_comparison=args.compare)
    else:
        print(f"Images directory not found: {images_dir}")

if __name__ == "__main__":
    main()
