import matplotlib.pyplot as plt

def render_latex_to_png(formula, filename, fontsize=20):
    fig = plt.figure(figsize=(10, 1.5))
    fig.text(0.5, 0.5, f"${formula}$", size=fontsize, ha='center', va='center')
    plt.axis('off')
    plt.savefig(filename, bbox_inches='tight', pad_inches=0.1, dpi=300)
    plt.close()

eq1 = r"P(i,j) = \frac{\tau(i,j)^\alpha \cdot \eta(i,j)^\beta}{\sum_{(m,n) \in \mathcal{N}} \tau(m,n)^\alpha \cdot \eta(m,n)^\beta}"
eq2 = r"\tau(i,j) \leftarrow (1 - \rho) \cdot \tau(i,j) + \Delta\tau(i,j)"

render_latex_to_png(eq1, "docs/presentation/assets/eq1.png", 24)
render_latex_to_png(eq2, "docs/presentation/assets/eq2.png", 24)
print("Equations generated.")
