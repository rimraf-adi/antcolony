"""Generate per-iteration frames of the ACO edge detection process and stitch into a video."""

import os
import numpy as np
import cv2
from main import AntColonyEdgeDetector


class ACOFrameRecorder(AntColonyEdgeDetector):
    """Subclass that saves a visualization frame after every iteration."""

    def run_detection_with_frames(self, frames_dir):
        os.makedirs(frames_dir, exist_ok=True)
        self._initialize_matrices()

        original = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
        height, width = original.shape

        # Frame 0: original image side-by-side with blank pheromone
        blank = np.zeros((height, width), dtype=np.uint8)
        self._save_frame(frames_dir, 0, original, blank, self.num_iterations,
                         "Initialization")

        for iteration in range(self.num_iterations):
            print(f"  Iteration {iteration + 1}/{self.num_iterations}")

            ant_positions_row = np.random.randint(0, self.height, self.num_ants)
            ant_positions_col = np.random.randint(0, self.width, self.num_ants)

            iteration_pheromone_delta = np.zeros((self.height, self.width))

            steps_per_ant = 10
            for step in range(steps_per_ant):
                for ant_idx in range(self.num_ants):
                    current_row = ant_positions_row[ant_idx]
                    current_col = ant_positions_col[ant_idx]

                    valid_neighbors = []
                    for row_offset in [-1, 0, 1]:
                        for col_offset in [-1, 0, 1]:
                            if row_offset == 0 and col_offset == 0:
                                continue
                            nr, nc = current_row + row_offset, current_col + col_offset
                            if 0 <= nr < self.height and 0 <= nc < self.width:
                                valid_neighbors.append((nr, nc))

                    if not valid_neighbors:
                        continue

                    move_probabilities = []
                    for n_row, n_col in valid_neighbors:
                        prob = (self.pheromone_matrix[n_row, n_col] ** self.alpha_weight) * \
                               (self.heuristic_matrix[n_row, n_col] ** self.beta_weight)
                        move_probabilities.append(prob)

                    move_probabilities = np.array(move_probabilities)
                    total_prob = move_probabilities.sum()

                    if total_prob > 0:
                        move_probabilities /= total_prob
                        chosen_idx = np.random.choice(len(valid_neighbors),
                                                       p=move_probabilities)
                        next_row, next_col = valid_neighbors[chosen_idx]
                        ant_positions_row[ant_idx] = next_row
                        ant_positions_col[ant_idx] = next_col
                        iteration_pheromone_delta[next_row, next_col] += \
                            self.heuristic_matrix[next_row, next_col]

            self.pheromone_matrix = ((1 - self.pheromone_decay_rate) *
                                     self.pheromone_matrix +
                                     iteration_pheromone_delta)

            # Normalize current pheromone to [0, 255] for visualization
            offset = self.pheromone_matrix.min()
            scale = self.pheromone_matrix.max() - offset
            if scale == 0:
                scale = 1.0
            normalized = ((self.pheromone_matrix - offset) / scale * 255).astype(np.uint8)

            # Dilate for visibility
            kernel = np.ones((3, 3), np.uint8)
            normalized = cv2.dilate(normalized, kernel, iterations=1)

            self._save_frame(frames_dir, iteration + 1, original, normalized,
                             self.num_iterations,
                             f"Iteration {iteration + 1}/{self.num_iterations}")

        # Hold final frame for 3 extra seconds at 5fps = 15 copies
        final_norm = normalized.copy()
        for extra in range(15):
            self._save_frame(frames_dir, self.num_iterations + 1 + extra,
                             original, final_norm, self.num_iterations,
                             f"Final Edge Map (iteration {self.num_iterations})")

        print(f"  ✓ {self.num_iterations + 16} frames saved to {frames_dir}/")
        return normalized

    def _save_frame(self, frames_dir, frame_num, original, edge_map,
                    total_iters, label):
        h, w = original.shape

        # Create dashboard: Original | Pheromone Edge Map
        sep_w = 6
        sep = np.ones((h, sep_w), dtype=np.uint8) * 180

        dashboard = np.hstack([original, sep, edge_map])
        dashboard_bgr = cv2.cvtColor(dashboard, cv2.COLOR_GRAY2BGR)

        # Title bar at top
        bar_h = 50
        title_bar = np.ones((bar_h, dashboard.shape[1], 3), dtype=np.uint8) * 255
        full = np.vstack([title_bar, dashboard_bgr])

        # Draw text on title bar
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Left label
        cv2.putText(full, "Original Image", (10, 35),
                    font, 0.7, (0, 0, 0), 2)

        # Right label
        cv2.putText(full, "ACO Pheromone Map", (w + sep_w + 10, 35),
                    font, 0.7, (0, 0, 0), 2)

        # Center status
        status = label
        text_size = cv2.getTextSize(status, font, 0.6, 1)[0]
        cx = (full.shape[1] - text_size[0]) // 2
        cv2.putText(full, status, (cx, 35),
                    font, 0.6, (80, 80, 80), 1)

        # Bottom bar with progress
        bot_h = 30
        bottom_bar = np.ones((bot_h, full.shape[1], 3), dtype=np.uint8) * 255
        full = np.vstack([full, bottom_bar])

        # Progress bar
        if total_iters > 0:
            progress = min(frame_num / total_iters, 1.0)
            bar_x = 10
            bar_y = full.shape[0] - 20
            bar_w = full.shape[1] - 20
            bar_height = 10

            # Background
            cv2.rectangle(full, (bar_x, bar_y),
                          (bar_x + bar_w, bar_y + bar_height),
                          (200, 200, 200), -1)
            # Fill
            fill_w = int(bar_w * progress)
            if fill_w > 0:
                cv2.rectangle(full, (bar_x, bar_y),
                              (bar_x + fill_w, bar_y + bar_height),
                              (0, 0, 0), -1)

        # Save
        fname = os.path.join(frames_dir, f"frame_{frame_num:04d}.png")
        cv2.imwrite(fname, full)


if __name__ == "__main__":
    import sys

    image_path = sys.argv[1] if len(sys.argv) > 1 else "images/100098.jpg"
    num_ants = int(sys.argv[2]) if len(sys.argv) > 2 else 4096
    num_iters = int(sys.argv[3]) if len(sys.argv) > 3 else 30

    print(f"ACO Frame Recorder")
    print(f"  Image: {image_path}")
    print(f"  Ants: {num_ants}, Iterations: {num_iters}")
    print()

    recorder = ACOFrameRecorder(
        image_path,
        num_iterations=num_iters,
        num_ants=num_ants,
    )

    frames_dir = "video_frames"
    recorder.run_detection_with_frames(frames_dir)

    print(f"\nStitching video with ffmpeg...")
    output_video = "ACO_Edge_Detection_Demo.mp4"
    ffmpeg_cmd = (
        f"ffmpeg -y -framerate 5 -i {frames_dir}/frame_%04d.png "
        f"-c:v libx264 -pix_fmt yuv420p -vf 'pad=ceil(iw/2)*2:ceil(ih/2)*2' "
        f"-r 30 {output_video}"
    )
    os.system(ffmpeg_cmd)
    print(f"  ✓ Video saved to: {output_video}")
