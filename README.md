# ACO-Based Edge Detection

Ant Colony Optimization applied to image edge detection, evaluated on the Berkeley Segmentation Dataset (BSDS300).

This project was developed as part of the **Image Analysis & Computer Vision** mini project at VNIT Nagpur, under the guidance of Dr. V. R. Satpute.

## What This Does

Instead of using fixed filter kernels like Sobel or Canny, this project uses a swarm of artificial ants to find edges in images. Each ant walks across the pixel grid, following intensity gradients and leaving behind pheromone trails. Over many iterations, pheromone builds up along genuine edge contours — the same way real ants converge on the shortest path to food.

The final pheromone map is normalized and used directly as the edge map. We ran this on all 300 images from the BSDS300 dataset and compared the results against human-annotated ground truth.

## Project Structure

```
iacv_research/
├── src/
│   ├── aco_edge.py            # Core ACO algorithm (AntColonyEdgeDetector class)
│   ├── process.py             # Batch processing pipeline with CLI
│   ├── build_presentation.py  # Generates the PDF presentation
│   ├── generate_video.py      # Creates the demo animation video
│   ├── stitch_video.py        # Stitches video frames together
│   └── math_eqn.py            # Renders equation images for slides
├── data/
│   ├── images/                # BSDS300 grayscale images (300 JPGs)
│   ├── human/                 # Human segmentation annotations (.seg files)
│   └── BSDS300/               # Original dataset files
├── output/                    # Generated 3-panel dashboard PNGs (300 files)
├── output_fresh/              # Alternate output run
├── docs/
│   └── presentation/
│       ├── index.html         # Interactive HTML slide deck
│       └── assets/            # Slide images and equations
├── submission/                # Final deliverables
│   ├── ACO_Edge_Detection_Presentation.pdf
│   ├── ACO_Edge_Detection_Demo.mp4
│   └── README.md
├── video_frames/              # Intermediate frames for video generation
├── viva_material.tex          # LaTeX reference notes for viva
├── pyproject.toml             # Dependencies and project config
├── uv.lock                    # Locked dependency versions
└── .python-version            # Python 3.13
```

## How the Algorithm Works

1. Compute **Sobel gradients** over the grayscale image to get a heuristic matrix η(i,j).
2. Initialize a **pheromone matrix** τ(i,j) uniformly across all pixels.
3. In each iteration, place K ants at random positions. Each ant takes S steps through the 8-connected pixel neighborhood, choosing its next move with probability proportional to τ^α · η^β.
4. After all ants finish walking, **evaporate** old pheromone and **deposit** new pheromone based on the paths taken.
5. Repeat for T iterations. Normalize the final pheromone matrix to [0, 255] and apply a mild dilation to thicken the edges.

## Requirements

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

Dependencies (installed automatically via `uv sync`):

| Package | Version | Purpose |
|---------|---------|---------|
| NumPy | ≥ 2.4.2 | Array operations |
| OpenCV | ≥ 4.13.0 | Image I/O, Sobel, Canny |
| tqdm | ≥ 4.67.3 | Progress bars |
| fpdf2 | latest | PDF presentation generation |

## Getting Started

```bash
# Clone the repository
git clone <repository-url>
cd iacv_research

# Install dependencies
uv sync
```

If you prefer pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install numpy opencv-python tqdm fpdf2
```

## Usage

All scripts live in `src/` and should be run from the project root.

### Single Image

```bash
uv run python src/aco_edge.py data/images/3096.jpg
```

This saves the edge map as `data/images/3096_aco_edges.png`. You can customize parameters:

```bash
uv run python src/aco_edge.py data/images/3096.jpg \
    --ants 4096 \
    --iterations 30 \
    --alpha 1.0 \
    --beta 2.0 \
    --decay 0.1 \
    -o my_edges.png
```

### Batch Processing (All 300 Images)

```bash
uv run python src/process.py
```

Processes every image in `data/images/`, generates a 3-panel dashboard (Original | Human Ground Truth | ACO Edge Map) for each, and saves them to `output/`.

### Process a Subset

```bash
uv run python src/process.py -n 10
```

### Include Sobel & Canny Comparison

```bash
uv run python src/process.py --compare
```

Generates a 5-panel dashboard with Sobel and Canny edges alongside ACO.

### Custom Output Directory

```bash
uv run python src/process.py -n 5 --compare -o results/
```

### Generate the Presentation PDF

```bash
uv run python src/build_presentation.py
```

### Generate the Demo Video

```bash
uv run python src/generate_video.py
```

## Hyperparameters

| Parameter | Symbol | Default | Batch Value | What It Controls |
|-----------|--------|---------|-------------|------------------|
| `num_ants` | K | 2,048 | 8,192 | Ants per iteration — more ants = denser coverage |
| `num_iterations` | T | 20 | 50 | Total passes — more iterations = better convergence |
| `alpha` | α | 1.0 | 1.0 | How much ants follow existing pheromone trails |
| `beta` | β | 2.0 | 2.0 | How much ants follow the raw gradient signal |
| `decay_rate` | ρ | 0.1 | 0.1 | How fast old pheromone fades per iteration |
| `steps_per_ant` | S | 10 | 10 | Steps each ant walks before stopping |

Setting β > α makes ants prioritize strong gradients over pheromone trails, which generally produces cleaner edges.

## Dataset

We used **BSDS300** (Berkeley Segmentation Dataset), a standard benchmark with 300 natural images split into 200 training and 100 test images. Each image has 5–7 independent human segmentation annotations.

Human segmentation labels (stored as `.seg` files with run-length encoded segments) are converted to binary edge maps by applying Sobel gradient detection on label boundaries.

**Source:** [Berkeley Computer Vision Group](https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/bsds/)

## Performance Notes

- Processing all 300 images at batch settings (8192 ants, 50 iterations) takes roughly 2–4 hours on a modern laptop.
- The inner loop is sequential (per-ant, per-step), so runtime scales linearly with ant count and iterations.
- Use `-n 5` for quick demos. Reducing `num_ants` to 2048 and `num_iterations` to 20 cuts processing time significantly.
- No GPU is required.

## Troubleshooting

**`ModuleNotFoundError: No module named 'cv2'`** — Run `uv sync` or `pip install opencv-python`.

**Image not loading** — Double-check the file path. Images should be in `data/images/`.

**Very slow processing** — Reduce ant count or iteration count, or limit the number of images with `-n`.

**Python version error** — This project requires Python 3.13+. Check with `python --version`.

**Import errors when running scripts** — Make sure you run from the project root directory (`iacv_research/`), not from inside `src/`.

## Reference

1. "Image Segmentation Technology Based on Ant Colony Algorithm." *Journal of Electrical Systems*, Vol. 20 No. 9s (2024). [https://journal.esrgroups.org/jes/article/view/4307](https://journal.esrgroups.org/jes/article/view/4307)
