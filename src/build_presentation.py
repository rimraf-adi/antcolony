"""Generate a clean black-and-white landscape PDF presentation for the ACO Edge Detection mini project."""

import os
from fpdf import FPDF

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class SlidePDF(FPDF):
    def __init__(self):
        super().__init__(orientation='L', unit='mm', format='A4')  # Landscape A4
        self.set_auto_page_break(auto=False)
        self.W = 297  # A4 landscape width
        self.H = 210  # A4 landscape height

    def slide_title(self, title):
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(0, 0, 0)
        self.set_xy(15, 12)
        self.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")
        # underline
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.5)
        self.line(15, 27, 120, 27)

    def body_text(self, text, x=15, y=None, size=13, bold=False, color=(0, 0, 0), w=None):
        if y is not None:
            self.set_y(y)
        self.set_x(x)
        style = "B" if bold else ""
        self.set_font("Helvetica", style, size)
        self.set_text_color(*color)
        text_w = w if w else (self.W - x - 10)
        self.multi_cell(text_w, 7, text)

    def bullet(self, text, x=20, size=12, color=(0, 0, 0)):
        self.set_x(x)
        self.set_font("Helvetica", "", size)
        self.set_text_color(*color)
        self.multi_cell(self.W - x - 15, 6.5, f"-  {text}")
        self.ln(1)

    def add_image_safe(self, path, x, y, w=None, h=None):
        if os.path.exists(path):
            kwargs = {"x": x, "y": y}
            if w is not None:
                kwargs["w"] = w
            if h is not None:
                kwargs["h"] = h
            self.image(path, **kwargs)
        else:
            self.set_xy(x, y)
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(150, 150, 150)
            self.cell(60, 5, f"[Image: {os.path.basename(path)}]")

    def slide_number(self, num, total):
        self.set_xy(self.W - 30, self.H - 10)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(150, 150, 150)
        self.cell(20, 5, f"{num} / {total}", align="R")


def build_pdf():
    pdf = SlidePDF()
    total = 14
    assets = os.path.join(SCRIPT_DIR, "../docs/presentation", "assets")

    # ──── SLIDE 1: Title ────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 36)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(15, 30)
    pdf.cell(pdf.W - 30, 18, "ACO-Based Edge Detection", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 18)
    pdf.set_text_color(100, 100, 100)
    pdf.set_x(15)
    pdf.cell(pdf.W - 30, 10, "Ant Colony Optimization for Image Edge Detection", align="C", new_x="LMARGIN", new_y="NEXT")

    # Divider
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.4)
    pdf.line(100, 80, 197, 80)

    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(80, 80, 80)
    pdf.set_xy(15, 87)
    pdf.cell(pdf.W - 30, 8, "Mini Project: Image Analysis & Computer Vision", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)
    
    info_lines = [
        "Submitted by: Aditya Kinjawadekar (BT23ECE064)",
        "Type: Solo Project",
        "Guide: Dr. V. R. Satpute",
        "Department of Electronics and Communication, VNIT Nagpur",
    ]
    for line in info_lines:
        pdf.set_x(15)
        pdf.cell(pdf.W - 30, 8, line, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.slide_number(1, total)

    # ──── SLIDE 2: Problem Statement ────
    pdf.add_page()
    pdf.slide_title("Problem Statement")

    pdf.body_text("Edge detection is a fundamental operation in image analysis: identifying "
                  "boundaries where pixel intensity changes sharply.", y=33)
    pdf.ln(4)
    pdf.body_text("Challenges with Traditional Methods:", bold=True, size=14)
    pdf.ln(1)
    pdf.bullet("Fixed-kernel methods (Sobel, Canny) cannot adaptively respond to varying edge strengths")
    pdf.bullet("Pixel-wise operators produce fragmented, disconnected edge contours")
    pdf.bullet("Sensitive to noise without careful parameter tuning")

    pdf.ln(4)
    pdf.body_text("Our Approach:", bold=True, size=14)
    pdf.ln(1)
    pdf.bullet("Apply Ant Colony Optimization (ACO): a swarm intelligence metaheuristic")
    pdf.bullet("Artificial ants traverse the pixel grid, depositing pheromone on edge locations")
    pdf.bullet("Pheromone accumulates along true edge contours over multiple iterations")
    pdf.bullet("Evaluate against human-annotated ground truth from BSDS300 (300 images)")
    pdf.slide_number(2, total)

    # ──── SLIDE 3: Literature Survey ────
    pdf.add_page()
    pdf.slide_title("Literature Survey")

    pdf.body_text("[1]  Tian, Yu & Xie (2008): IEEE CEC", y=33, bold=True, size=13)
    pdf.bullet("Pioneered ACO for image edge detection. Ants traverse pixel grids using pheromone and gradient heuristics. Competitive with Sobel and Canny.", color=(80, 80, 80))

    pdf.ln(2)
    pdf.body_text("[2]  Nezamabadi-pour et al.: MRF-Based Image Segmentation", bold=True, size=13)
    pdf.bullet("Extended ACO to MRF-based segmentation, showing pheromone-guided traversal captures spatial context beyond local gradient information.", color=(80, 80, 80))

    pdf.ln(2)
    pdf.body_text("[3]  IJETT V71I9P233: Edge Detection Using ACO", bold=True, size=13)
    pdf.bullet("Comprehensive survey comparing ACO with classical methods. Analyzes parameter sensitivity. ACO produces smoother, more connected edges.", color=(80, 80, 80))
    pdf.slide_number(3, total)

    # ──── SLIDE 4: Biological Inspiration ────
    pdf.add_page()
    pdf.slide_title("Biological Inspiration")

    pdf.body_text("Real Ant Behavior", x=15, y=33, bold=True, size=15)
    y_start = pdf.get_y() + 2
    for b in [
        "Ants deposit pheromone on paths while foraging",
        "Shorter, better paths accumulate more pheromone",
        "Other ants prefer pheromone-rich paths",
        "Old pheromone evaporates over time",
        "Collective behavior -> emergent optimization",
    ]:
        pdf.set_y(pdf.get_y())
        pdf.bullet(b, x=18)

    pdf.body_text("Our Analogy", x=155, y=33, bold=True, size=15)
    pdf.set_y(y_start)
    for b in [
        "Image pixels = graph nodes",
        "8-connected neighbors = possible moves",
        "Gradient magnitude = heuristic desirability",
        "Pheromone matrix = collective edge memory",
        "Edge contours emerge from pheromone accumulation",
    ]:
        pdf.bullet(b, x=158)

    # Divider line
    pdf.set_draw_color(200, 200, 200)
    pdf.line(148, 33, 148, 150)
    pdf.slide_number(4, total)

    # ──── SLIDE 5: Mathematical Formulation ────
    pdf.add_page()
    pdf.slide_title("Mathematical Formulation")

    pdf.body_text("Transition Probability", y=33, bold=True, size=15)
    pdf.body_text("Each ant at pixel (i,j) chooses its next position from the 8-connected neighborhood:", size=11, color=(100, 100, 100))
    pdf.ln(2)

    img_eq1 = os.path.join(assets, "eq1.png")
    pdf.add_image_safe(img_eq1, 40, pdf.get_y(), w=200)

    pdf.ln(33)
    pdf.body_text("Pheromone Update", bold=True, size=15)
    pdf.ln(1)

    img_eq2 = os.path.join(assets, "eq2.png")
    pdf.add_image_safe(img_eq2, 40, pdf.get_y(), w=180)

    pdf.ln(30)
    pdf.body_text("Where:", bold=True, size=12)
    pdf.bullet("t(i,j) = pheromone level          n(i,j) = heuristic (Sobel gradient)", size=11, color=(80, 80, 80))
    pdf.bullet("a = pheromone weight               b = heuristic weight               rho = evaporation rate", size=11, color=(80, 80, 80))
    pdf.slide_number(5, total)

    # ──── SLIDE 6: System Architecture ────
    pdf.add_page()
    pdf.slide_title("System Architecture & Pipeline")

    pdf.body_text("The following represents the step-by-step pipeline from input image to the final edge map.", y=35)
    pdf.ln(10)
    # Flowchart
    steps = ["Input Image\n(Grayscale)", "Sobel Gradient\nn(i,j)", "Init Pheromone\nt = 0.1",
             "Ant Traversal\nK ants, S steps", "Pheromone\nUpdate", "Edge Map\n[0, 255]"]

    box_w = 40
    box_h = 22
    start_x = 12
    y_pos = 80
    gap = 7

    for i, label in enumerate(steps):
        x = start_x + i * (box_w + gap)
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.5)
        pdf.rect(x, y_pos, box_w, box_h)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(x, y_pos + 4)
        pdf.cell(box_w, 5, f"Step {i+1}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(80, 80, 80)
        lines = label.split("\n")
        pdf.ln(1)
        for ln_text in lines:
            pdf.set_x(x)
            pdf.cell(box_w, 5, ln_text, align="C", new_x="LMARGIN", new_y="NEXT")

        if i < len(steps) - 1:
            arrow_x = x + box_w
            pdf.set_xy(arrow_x, y_pos + 8)
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(gap, 6, ">", align="C")

    pdf.slide_number(6, total)

    # ──── SLIDE 7: Implementation (Pseudocode) ────
    pdf.add_page()
    pdf.slide_title("How Ants Find Edges: Pseudocode")

    code = """1. Prepare a blank map for pheromones (trails) and a gradient map of the main image.
2. For multiple turns (iterations):
3.     Place a large number of ants randomly on the image grid.
4.     For a set number of steps:
5.         Each ant looks at its 8 neighboring pixels.
6.         It calculates the chance to move across based on:
7.              - How strong the image gradient is (heuristic)
8.              - How much pheromone other ants left (trail)
9.         The ant moves and leaves a small pheromone trace on its path.
10.    After all ants finish moving, evaporate some old pheromones so bad paths fade.
11.    Add the new pheromones from this turn to the global map.
12. Once all turns are over, the areas with the most pheromone represent the true edges.
13. Thicken the edges for visibility and return the final image."""

    pdf.set_fill_color(248, 248, 248)
    pdf.set_draw_color(220, 220, 220)
    code_y = 35
    pdf.rect(15, code_y, pdf.W - 30, 110, style="DF")
    pdf.set_xy(20, code_y + 8)
    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(30, 30, 30)
    for line in code.split("\n"):
        pdf.set_x(20)
        pdf.cell(0, 7, line, new_x="LMARGIN", new_y="NEXT")
    pdf.slide_number(7, total)

    # ──── SLIDE 8: Dataset ────
    pdf.add_page()
    pdf.slide_title("Dataset: BSDS300")

    pdf.body_text("Berkeley Segmentation Dataset: 300 natural images with human-annotated ground truth", y=33, size=12, color=(100, 100, 100))

    # Stats boxes
    stats = [("300", "Natural Images"), ("200", "Training Set"),
             ("100", "Test Set"), ("5-7", "Annotators/Image")]
    for i, (val, label) in enumerate(stats):
        x = 20 + i * 65
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.4)
        pdf.rect(x, 45, 55, 25)
        pdf.set_font("Helvetica", "B", 22)
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(x, 47)
        pdf.cell(55, 10, val, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.set_x(x)
        pdf.cell(55, 6, label, align="C")

    pdf.body_text("Dataset Features", x=15, y=80, bold=True, size=14)
    pdf.bullet("Diverse scenes: animals, landscapes, people, objects, urban")
    pdf.bullet("Multiple independent human segmentations per image")
    pdf.bullet("Standard benchmark in edge detection and segmentation literature")

    pdf.body_text("Our Processing", x=155, y=80, bold=True, size=14)
    pdf.set_y(pdf.get_y() - 20)
    pdf.bullet("All images converted to grayscale", x=158)
    pdf.bullet(".seg files parsed to binary edge maps via Sobel", x=158)
    pdf.bullet("3-panel dashboard visualization per image", x=158)
    pdf.slide_number(8, total)

    # ──── SLIDE 9: Hyperparameters ────
    pdf.add_page()
    pdf.slide_title("Hyperparameters")

    headers = ["Parameter", "Symbol", "Default", "Batch", "Description"]
    data = [
        ["num_ants", "K", "2,048", "8,192", "Ants per iteration"],
        ["num_iterations", "T", "20", "50", "ACO iterations"],
        ["alpha", "a", "1.0", "1.0", "Pheromone influence weight"],
        ["beta", "b", "2.0", "2.0", "Heuristic (gradient) weight"],
        ["decay_rate", "rho", "0.1", "0.1", "Pheromone evaporation rate"],
        ["steps_per_ant", "S", "10", "10", "Steps each ant takes"],
    ]
    col_widths = [45, 20, 25, 25, 130]
    table_x = 20
    y = 35

    # Header
    pdf.set_fill_color(0, 0, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_xy(table_x, y)
    for j, h in enumerate(headers):
        pdf.cell(col_widths[j], 8, h, border=1, fill=True, align="C")
    pdf.ln()

    # Rows
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)
    for row in data:
        pdf.set_x(table_x)
        for j, val in enumerate(row):
            font = "Courier" if j == 0 else "Helvetica"
            pdf.set_font(font, "", 10)
            pdf.cell(col_widths[j], 8, val, border=1, align="C")
        pdf.ln()

    pdf.ln(6)
    pdf.body_text("Key insight: b > a favors gradient-guided exploration, producing edges aligned with true "
                  "intensity transitions. Batch uses 8192 ants and 50 iterations for production quality.",
                  size=11, color=(100, 100, 100))
    pdf.slide_number(9, total)

    # ──── SLIDE 10: Results 1 ────
    pdf.add_page()
    pdf.slide_title("Results: Sample Outputs (Set 1)")

    pdf.body_text("Each dashboard: Original | Human Ground Truth | ACO Edge Map", y=30, size=11, color=(100, 100, 100))

    img1 = os.path.join(SCRIPT_DIR, "../output_fresh/100075.png")
    pdf.add_image_safe(img1, 15, 40, w=265)

    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.set_xy(15, 100)
    pdf.cell(265, 5, "BSDS300 #100075: Bears", align="C")

    img2 = os.path.join(SCRIPT_DIR, "../output_fresh/100098.png")
    pdf.add_image_safe(img2, 15, 110, w=265)

    pdf.set_xy(15, 170)
    pdf.cell(265, 5, "BSDS300 #100098: Bear in snow", align="C")
    pdf.slide_number(10, total)

    # ──── SLIDE 11: Results 2 ────
    pdf.add_page()
    pdf.slide_title("Results: Sample Outputs (Set 2)")

    img3 = os.path.join(SCRIPT_DIR, "../output_fresh/101085.png")
    pdf.add_image_safe(img3, 15, 35, w=265)

    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.set_xy(15, 97)
    pdf.cell(265, 5, "BSDS300 #101085: Scene Outline", align="C")

    img4 = os.path.join(SCRIPT_DIR, "../output_fresh/101087.png")
    pdf.add_image_safe(img4, 15, 107, w=265)

    pdf.set_xy(15, 170)
    pdf.cell(265, 5, "BSDS300 #101087: Scene Edge Map", align="C")
    pdf.slide_number(11, total)

    # ──── SLIDE 12: Analysis ────
    pdf.add_page()
    pdf.slide_title("Strengths & Limitations")

    pdf.body_text("Strengths", x=15, y=33, bold=True, size=15)
    for s in [
        "Adaptive: pheromone reinforcement concentrates on true edges",
        "Connected edges: ant traversal produces continuous contours",
        "Noise tolerance: collective behavior averages out noise",
        "Flexible: tunable via a, b, rho, ant count parameters",
        "No training required: pure optimization approach",
    ]:
        pdf.bullet(s, x=18)

    pdf.body_text("Limitations", x=155, y=33, bold=True, size=15)
    pdf.set_y(44)
    for s in [
        "Computational cost: per-ant loops are expensive",
        "Parameter sensitivity: poor a/b produce weak edges",
        "Thinner edges: ACO edges sparser than ground truth",
        "No multi-scale: single-resolution Sobel heuristic",
        "Sequential bottleneck: hard to parallelize on CPU",
    ]:
        pdf.bullet(s, x=158)

    pdf.set_draw_color(200, 200, 200)
    pdf.line(148, 33, 148, 150)
    pdf.slide_number(12, total)

    # ──── SLIDE 13: Comparison ────
    pdf.add_page()
    pdf.slide_title("ACO vs. Traditional Methods")

    headers2 = ["Property", "Sobel", "Canny", "ACO (Ours)"]
    data2 = [
        ["Approach", "Fixed 3x3 kernels", "Multi-stage pipeline", "Swarm intelligence"],
        ["Adaptivity", "None", "Threshold-based", "Pheromone-guided"],
        ["Edge Continuity", "Low (pixel-wise)", "Medium (hysteresis)", "High (ant paths)"],
        ["Noise Handling", "Poor", "Good (Gaussian blur)", "Good (collective avg.)"],
        ["Speed", "Very fast", "Fast", "Slow (iterative)"],
        ["Parameters", "Kernel size", "2 thresholds + sigma", "a, b, rho, K, T, S"],
    ]
    col_w2 = [45, 60, 60, 60]
    tx = 25
    ty = 35

    pdf.set_fill_color(0, 0, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_xy(tx, ty)
    for j, h in enumerate(headers2):
        pdf.cell(col_w2[j], 8, h, border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    for row in data2:
        pdf.set_x(tx)
        for j, val in enumerate(row):
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(col_w2[j], 8, val, border=1, align="C")
        pdf.ln()

    pdf.ln(6)
    pdf.body_text("Key takeaway: ACO trades computational speed for adaptivity and edge continuity. "
                  "Best suited for applications where edge quality matters more than real-time performance.",
                  size=11, color=(100, 100, 100))
    pdf.slide_number(13, total)

    # ──── SLIDE 14: Conclusion ────
    pdf.add_page()
    pdf.slide_title("Conclusion")

    pdf.body_text("Final Remarks", x=15, y=33, bold=True, size=15)
    for c in [
        "Successfully implemented an Ant Colony Optimization algorithm for edge detection.",
        "Evaluated thoroughly on 300 images from the Berkeley Segmentation Dataset (BSDS300).",
        "Demonstrated the ability of artificial ants to form coherent, continuous edge contours.",
        "Proved the algorithm works in a fully unsupervised manner without external training.",
        "Created an automated dashboard to visually compare outputs with human ground truth.",
    ]:
        pdf.bullet(c, x=18)

    pdf.slide_number(14, total)

    # Save
    out = os.path.join(SCRIPT_DIR, "ACO_Edge_Detection_Presentation.pdf")
    pdf.output(out)
    print(f"Presentation saved to: {out}")
    print(f"  {total} slides, landscape A4")


if __name__ == "__main__":
    build_pdf()
