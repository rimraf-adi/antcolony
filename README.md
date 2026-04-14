# ACO-Based Edge Detection on BSDS300

An implementation of **Ant Colony Optimization (ACO)** for image edge detection, evaluated against human-annotated ground truth from the Berkeley Segmentation Dataset (BSDS300).

---

## Table of Contents

- [Method Overview](#method-overview)
- [Project Structure](#project-structure)
- [Software Requirements](#software-requirements)
- [Hardware Requirements](#hardware-requirements)
- [Installation](#installation)
- [Execution Instructions](#execution-instructions)
- [Expected Output](#expected-output)
- [Hyperparameters](#hyperparameters)
- [Troubleshooting](#troubleshooting)
- [References](#references)

---

## Method Overview

This project applies the Ant Colony Optimization metaheuristic — inspired by the foraging behavior of real ants — to the image edge detection problem. Rather than relying on fixed filter kernels (Sobel, Canny, etc.), the approach allows a colony of artificial ants to traverse the image pixel grid, depositing pheromone on locations that correspond to strong intensity gradients. Over multiple iterations, pheromone accumulates along true edge contours, producing an emergent edge map.

### Algorithm Steps

1. **Heuristic Initialization** — Sobel gradient magnitudes are computed over the grayscale image to form a heuristic matrix η(i, j) that guides ant movement toward high-gradient regions.

2. **Pheromone Initialization** — A uniform pheromone matrix τ(i, j) is initialized across all pixels.

3. **Ant Traversal** — In each iteration, K ants are placed at random pixel locations. Each ant takes a fixed number of steps, choosing its next position from the 8-connected neighborhood with probability:

$$
P(i, j) = \frac{\tau(i,j)^{\alpha} \cdot \eta(i,j)^{\beta}}{\sum_{(m,n) \in \mathcal{N}} \tau(m,n)^{\alpha} \cdot \eta(m,n)^{\beta}}
$$

where α and β control the relative influence of pheromone vs. heuristic information.

4. **Pheromone Update** — After all ants complete their walks, pheromone is updated with evaporation and reinforcement:

$$
\tau(i,j) \leftarrow (1 - \rho) \cdot \tau(i,j) + \Delta\tau(i,j)
$$

where ρ is the decay rate and Δτ(i,j) accumulates the heuristic values deposited by ants that visited pixel (i, j).

5. **Edge Map Extraction** — After all iterations, the pheromone matrix is normalized to [0, 255] to produce the final edge map.

---

## Project Structure

```
iacv_research/
├── main.py              # AntColonyEdgeDetector class (core algorithm)
├── process_images.py    # Batch processing pipeline with CLI support
├── images/              # BSDS300 grayscale input images (300 JPGs)
├── human/               # Human segmentation annotations
│   ├── color/           #   Color segmentation maps
│   └── gray/            #   Grayscale segmentation maps (.seg files)
├── output/              # Generated dashboard visualizations (300 PNGs)
├── presentation/        # HTML presentation slides
│   ├── index.html       #   15-slide presentation
│   └── assets/          #   Sample images for slides
├── ref/                 # Reference papers (3 PDFs)
│   ├── 1-s2.0-S2666285X21000728-main.pdf
│   ├── Ant_Colonies_For_MRF_Based_Image_Segment.pdf
│   └── IJETT-V71I9P233.pdf
├── BSDS300/             # Original BSDS300 dataset
│   ├── iids_train.txt   #   Training image IDs (200)
│   ├── iids_test.txt    #   Test image IDs (100)
│   ├── images/          #   Original images
│   └── human/           #   Human annotations
├── pyproject.toml       # Project & dependency configuration
├── uv.lock              # Locked dependency versions
├── .python-version      # Python version (3.13)
└── README.md            # This file
```

---

## Software Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | ≥ 3.13 | Runtime |
| **uv** | latest | Package manager (recommended) |
| **NumPy** | ≥ 2.4.2 | Array operations |
| **OpenCV (cv2)** | ≥ 4.13.0 | Image I/O, Sobel, Canny |
| **tqdm** | ≥ 4.67.3 | Progress bars |

### Operating System

- **macOS** (tested on macOS 15+)
- **Linux** (Ubuntu 22.04+, any distro with Python 3.13)
- **Windows** (with Python 3.13 installed)

---

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 4 GB | 8+ GB |
| **Disk** | 500 MB (for dataset + outputs) | 1 GB |
| **GPU** | Not required | Not required |

> **Note:** Processing all 300 images with high settings (8192 ants, 50 iterations) takes approximately 2–4 hours on a modern laptop. Use the `--max-images` flag for faster demos.

---

## Installation

### Step 1: Install Python 3.13+

Download from [python.org](https://www.python.org/downloads/) or use your system package manager.

### Step 2: Install uv (recommended)

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via Homebrew
brew install uv
```

### Step 3: Clone or download this project

```bash
git clone <repository-url>
cd iacv_research
```

### Step 4: Install dependencies

```bash
uv sync
```

This installs all dependencies (NumPy, OpenCV, tqdm) into an isolated virtual environment.

### Alternative: Using pip

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# or .venv\Scripts\activate  # Windows
pip install numpy opencv-python tqdm
```

---

## Execution Instructions

### Quick Demo — Single Image

Run ACO edge detection on a single image:

```bash
uv run python main.py images/3096.jpg
```

This generates `images/3096_aco_edges.png`. You can customize parameters:

```bash
uv run python main.py images/3096.jpg \
    --ants 4096 \
    --iterations 30 \
    --alpha 1.0 \
    --beta 2.0 \
    --decay 0.1 \
    -o my_output.png
```

### Full Batch Processing — All 300 Images

```bash
uv run python process_images.py
```

This processes all 300 BSDS300 images and saves dashboard visualizations to `output/`.

### Batch Processing — Limited Count

Process only the first N images (useful for demos):

```bash
uv run python process_images.py -n 5
```

### Batch Processing — With Canny/Sobel Comparison

Generate 5-panel dashboards including Sobel and Canny edges alongside ACO:

```bash
uv run python process_images.py --compare
```

### Custom Output Directory

```bash
uv run python process_images.py -n 10 --compare -o results/
```

---

## Expected Output

Each dashboard image contains side-by-side panels:

| Panel | Description |
|-------|-------------|
| **Original** | Grayscale input image from BSDS300 |
| **Human Edge** | Ground truth edges derived from human segmentation annotations |
| **ACO Edge** | Edge map generated by the Ant Colony Optimization algorithm |
| **Sobel** *(optional)* | Sobel gradient magnitude (with `--compare` flag) |
| **Canny** *(optional)* | Canny edge detection output (with `--compare` flag) |

Output files are saved as PNG images in the output directory.

---

## Dataset

**BSDS300** (Berkeley Segmentation Dataset) — 300 natural images with multiple human-annotated segmentation ground truths.

- **Source:** [Berkeley Computer Vision Group](https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/bsds/)
- **Split:** 200 training + 100 test images
- **Annotations:** 5–7 human segmentations per image
- **Format:** `.seg` files containing run-length encoded segment labels

Human segmentation labels are converted to binary edge maps via Sobel gradient detection on the label boundaries.

---

## Hyperparameters

| Parameter | Symbol | Default | Batch Value | Description |
|-----------|--------|---------|-------------|-------------|
| `num_ants` | K | 2,048 | 8,192 | Number of ants per iteration |
| `num_iterations` | T | 20 | 50 | Number of ACO iterations |
| `alpha` | α | 1.0 | 1.0 | Pheromone influence weight |
| `beta` | β | 2.0 | 2.0 | Heuristic (gradient) influence weight |
| `decay_rate` | ρ | 0.1 | 0.1 | Pheromone evaporation rate |
| `steps_per_ant` | S | 10 | 10 | Steps each ant takes per iteration |

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'cv2'`

OpenCV is not installed. Run:

```bash
uv sync
# or
pip install opencv-python
```

### `ValueError: Could not load image at ...`

Ensure the image path is correct and the file exists. Check that the `images/` directory contains the BSDS300 dataset.

### Processing is very slow

- Use fewer images: `uv run python process_images.py -n 5`
- Reduce ant count: edit `process_images.py`, change `num_ants=8192` to `num_ants=2048`
- Reduce iterations: change `num_iterations=50` to `num_iterations=20`

### Python version error

This project requires Python 3.13+. Check your version:

```bash
python --version
```

### `import error: cannot import name 'AntColonyEdgeDetector'`

Make sure you are running the scripts from the project root directory (`iacv_research/`).

---

## References

1. Tian, J., Yu, W., & Xie, S. (2008). An ant colony optimization algorithm for image edge detection. *IEEE Congress on Evolutionary Computation*.
2. Nezamabadi-pour, H., et al. Ant Colonies for MRF-Based Image Segmentation.
3. Edge Detection Using Ant Colony Optimization. *International Journal of Engineering Trends and Technology*, V71I9P233.
4. Martin, D., Fowlkes, C., Tal, D., & Malik, J. (2001). A Database of Human Segmented Natural Images. *ICCV*.
5. Dorigo, M. & Stützle, T. (2004). *Ant Colony Optimization.* MIT Press.
