"""Stitch video_frames/ into an MP4 video using OpenCV VideoWriter."""

import os
import cv2
import glob

frames_dir = "video_frames"
output_path = "ACO_Edge_Detection_Demo.mp4"
fps = 5

# Collect frames in order
frame_files = sorted(glob.glob(os.path.join(frames_dir, "frame_*.png")))
print(f"Found {len(frame_files)} frames in {frames_dir}/")

if not frame_files:
    print("No frames found!")
    exit(1)

# Read first frame to get dimensions
sample = cv2.imread(frame_files[0])
h, w = sample.shape[:2]

# Ensure even dimensions for h264
h_even = h if h % 2 == 0 else h + 1
w_even = w if w % 2 == 0 else w + 1

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter(output_path, fourcc, fps, (w_even, h_even))

for f in frame_files:
    frame = cv2.imread(f)
    if frame.shape[0] != h_even or frame.shape[1] != w_even:
        frame = cv2.copyMakeBorder(frame, 0, h_even - frame.shape[0],
                                    0, w_even - frame.shape[1],
                                    cv2.BORDER_CONSTANT, value=(255, 255, 255))
    writer.write(frame)

writer.release()
print(f"✓ Video saved to: {output_path}")
print(f"  Resolution: {w_even}x{h_even}, FPS: {fps}, Duration: {len(frame_files)/fps:.1f}s")
