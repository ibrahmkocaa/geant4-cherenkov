#!/usr/bin/env python3
"""
Nötron termalleşmesi (suda moderasyon) tesir kesiti grafiği (log-log).
thermalization_data.csv dosyasından okur.

Anlatılan hikaye:
  - Serbest H ~20 barn'lık düz bir plato verir (klasik moderasyon).
  - Suda BAĞLI H, termal altı enerjide kimyasal bağ etkisiyle ~800 barn'a
    fırlar — suyun neden bu kadar verimli moderatör olduğunun nedeni.
  - O-16'nın katkısı küçüktür (ξ_O ~ 0.12).
"""

import numpy as np
import matplotlib.pyplot as plt

# ── Veri ──
data = np.genfromtxt("thermalization_data.csv", delimiter=",", skip_header=1)
energy   = data[:, 0]   # eV
H_free   = data[:, 1]   # barn
O_free   = data[:, 2]
H_bound  = data[:, 3]

# ── Stil ──
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 13,
    "axes.linewidth": 1.2,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.major.size": 6, "ytick.major.size": 6,
    "xtick.minor.size": 3, "ytick.minor.size": 3,
    "xtick.top": True, "ytick.right": True,
})

fig, ax = plt.subplots(figsize=(12, 8))

colors = {
    "H_bound": "#1D3557",   # Koyu lacivert — bağlı su (ana eğri)
    "H_free":  "#E63946",   # Kırmızı — serbest H
    "O_free":  "#2A9D8F",   # Teal — serbest O
}


def safe_plot(ax, x, y, **kwargs):
    mask = y > 0
    ax.plot(x[mask], y[mask], **kwargs)


safe_plot(ax, energy, H_bound, color=colors["H_bound"], linewidth=2.4,
          label=r"$^{1}$H bound in water $-$ S($\alpha,\beta$), 293.6 K  ($\sigma_{th}$ = 54.5 b)")
safe_plot(ax, energy, H_free, color=colors["H_free"], linewidth=2.0,
          linestyle="--",
          label=r"$^{1}$H free-atom elastic  ($\sigma_{th}$ = 20.4 b)")
safe_plot(ax, energy, O_free, color=colors["O_free"], linewidth=2.0,
          linestyle="-.",
          label=r"$^{16}$O free-atom elastic  ($\sigma_{th}$ = 3.85 b)")

# ── Thermal energy line ──
ax.axvline(x=0.0253, color="#333333", linestyle="--", linewidth=2.0, alpha=0.8,
           zorder=1)
ax.annotate(r"$E_{thermal}$ = 0.0253 eV",
            xy=(0.0253, 2e3), xytext=(0.3, 2e3),
            fontsize=12, fontweight="bold", color="#333333",
            arrowprops=dict(arrowstyle="->", color="#333333", lw=1.5),
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="#333333", alpha=0.9),
            va="center", ha="left")

# ── Eksenler ──
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(1e-5, 2e7)
ax.set_ylim(1e-1, 5e3)
ax.set_xlabel("Neutron Energy (eV)", fontsize=15, fontweight="bold")
ax.set_ylabel("Scattering Cross Section (barn)", fontsize=15, fontweight="bold")
ax.set_title("Neutron Thermalization — Scattering Cross Sections\n"
             "(G4NDL 4.7.1)", fontsize=16, fontweight="bold", pad=15)

legend = ax.legend(loc="upper right", fontsize=12, framealpha=0.9,
                   edgecolor="gray", fancybox=True)
legend.get_frame().set_linewidth(0.8)

ax.grid(True, which="major", linestyle="-", alpha=0.3, color="gray")
ax.grid(True, which="minor", linestyle=":", alpha=0.15, color="gray")

plt.tight_layout()

output_png = "thermalization_plot.png"
output_pdf = "thermalization_plot.pdf"
plt.savefig(output_png, dpi=300, bbox_inches="tight")
plt.savefig(output_pdf, bbox_inches="tight")
print(f"[OK] Grafik kaydedildi: {output_png}, {output_pdf}")

plt.show()
