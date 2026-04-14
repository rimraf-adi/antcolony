import numpy as np
import cv2

class AntColonyEdgeDetector:
    def __init__(self, image_path, num_iterations=20, num_ants=2048, alpha=1.0, beta=2.0, decay_rate=0.1):
        self.image_path = image_path
        self.num_iterations = num_iterations
        self.num_ants = num_ants
        self.alpha_weight = alpha
        self.beta_weight = beta
        self.pheromone_decay_rate = decay_rate
        
        self.image_data = None
        self.heuristic_matrix = None
        self.pheromone_matrix = None
        self.height = 0
        self.width = 0

    def _initialize_matrices(self):
        image = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError(f"Could not load image at {self.image_path}")
            
        self.image_data = image.astype(np.float32) / 255.0
        self.height, self.width = self.image_data.shape

        gradient_x = cv2.Sobel(self.image_data, cv2.CV_32F, 1, 0, ksize=3)
        gradient_y = cv2.Sobel(self.image_data, cv2.CV_32F, 0, 1, ksize=3)
        
        self.heuristic_matrix = np.sqrt(gradient_x**2 + gradient_y**2)
        
        self.pheromone_matrix = np.full((self.height, self.width), 0.1)

    def run_detection(self, verbose=False):
        self._initialize_matrices()

        for iteration in range(self.num_iterations):
            if verbose:
                print(f"  Iteration {iteration + 1}/{self.num_iterations} — "
                      f"pheromone range: [{self.pheromone_matrix.min():.4f}, {self.pheromone_matrix.max():.4f}]")
            ant_positions_row = np.random.randint(0, self.height, self.num_ants)
            ant_positions_col = np.random.randint(0, self.width, self.num_ants)
            
            iteration_pheromone_delta = np.zeros((self.height, self.width))

            steps_per_ant = 10
            for step in range(steps_per_ant): 
                for ant_idx in range(self.num_ants):
                    current_row, current_col = ant_positions_row[ant_idx], ant_positions_col[ant_idx]
                    
                    valid_neighbors = []
                    
                    for row_offset in [-1, 0, 1]:
                        for col_offset in [-1, 0, 1]:
                            if row_offset == 0 and col_offset == 0:
                                continue
                                
                            neighbor_row, neighbor_col = current_row + row_offset, current_col + col_offset
                            
                            if 0 <= neighbor_row < self.height and 0 <= neighbor_col < self.width:
                                valid_neighbors.append((neighbor_row, neighbor_col))
                    
                    if not valid_neighbors:
                        continue

                    move_probabilities = []
                    for n_row, n_col in valid_neighbors:
                        pheromone_level = self.pheromone_matrix[n_row, n_col]
                        heuristic_value = self.heuristic_matrix[n_row, n_col]
                        
                        prob = (pheromone_level ** self.alpha_weight) * (heuristic_value ** self.beta_weight)
                        move_probabilities.append(prob)
                    
                    move_probabilities = np.array(move_probabilities)
                    total_prob = move_probabilities.sum()
                    
                    if total_prob > 0:
                        move_probabilities /= total_prob
                        
                        chosen_idx = np.random.choice(len(valid_neighbors), p=move_probabilities)
                        next_row, next_col = valid_neighbors[chosen_idx]
                        
                        ant_positions_row[ant_idx], ant_positions_col[ant_idx] = next_row, next_col
                        
                        iteration_pheromone_delta[next_row, next_col] += self.heuristic_matrix[next_row, next_col]

            self.pheromone_matrix = (1 - self.pheromone_decay_rate) * self.pheromone_matrix + iteration_pheromone_delta

        offset = self.pheromone_matrix.min()
        scale = self.pheromone_matrix.max() - offset
        
        if scale == 0:
            scale = 1.0
            
        normalized_map = (self.pheromone_matrix - offset) / scale
        edge_map = (normalized_map * 255).astype(np.uint8)

        # Thicken edge pixels via morphological dilation (3×3 nearest-neighbor kernel)
        kernel = np.ones((3, 3), np.uint8)
        edge_map = cv2.dilate(edge_map, kernel, iterations=1)

        return edge_map


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="ACO Edge Detection — Single Image Demo")
    parser.add_argument("image", help="Path to the input image")
    parser.add_argument("-o", "--output", default=None, help="Output path (default: <image>_aco_edges.png)")
    parser.add_argument("--ants", type=int, default=2048, help="Number of ants (default: 2048)")
    parser.add_argument("--iterations", type=int, default=20, help="Number of iterations (default: 20)")
    parser.add_argument("--alpha", type=float, default=1.0, help="Pheromone weight α (default: 1.0)")
    parser.add_argument("--beta", type=float, default=2.0, help="Heuristic weight β (default: 2.0)")
    parser.add_argument("--decay", type=float, default=0.1, help="Decay rate ρ (default: 0.1)")
    parser.add_argument("--show", action="store_true", help="Display result using OpenCV window")
    args = parser.parse_args()

    print(f"ACO Edge Detection")
    print(f"  Image:      {args.image}")
    print(f"  Ants:       {args.ants}")
    print(f"  Iterations: {args.iterations}")
    print(f"  α={args.alpha}  β={args.beta}  ρ={args.decay}")
    print()

    detector = AntColonyEdgeDetector(
        args.image,
        num_iterations=args.iterations,
        num_ants=args.ants,
        alpha=args.alpha,
        beta=args.beta,
        decay_rate=args.decay,
    )
    edge_map = detector.run_detection(verbose=True)

    output_path = args.output
    if output_path is None:
        name, ext = os.path.splitext(args.image)
        output_path = f"{name}_aco_edges.png"

    cv2.imwrite(output_path, edge_map)
    print(f"\n  ✓ Edge map saved to: {output_path}")

    if args.show:
        cv2.imshow("ACO Edge Map", edge_map)
        cv2.waitKey(0)
        cv2.destroyAllWindows()