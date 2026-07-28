#!/usr/bin/env python3
"""
Nötron absorpsiyon tesir kesiti grafiği (log-log).
CSV dosyasından okur ve yayın kalitesinde grafik çıkarır.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import csv

# ── CSV dosyasını oku ──
data = np.genfromtxt("neutron_capture_cross_sections.csv",
                     delimiter=",", skip_header=1)

energy  = data[:, 0]   # eV
li6_xs  = data[:, 1]   # barn
li7_xs  = data[:, 2]
b10_xs  = data[:, 3]
gd155_xs = data[:, 4]
gd157_xs = data[:, 5]
h1_xs   = data[:, 6]   # su arka planı (H-1)
o16_xs  = data[:, 7]   # su arka planı (O-16)

# ── Grafik ayarları ──
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 13,
    "axes.linewidth": 1.2,
    "xtick.major.width": 1.0,
    "ytick.major.width": 1.0,
    "xtick.minor.width": 0.6,
    "ytick.minor.width": 0.6,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.major.size": 6,
    "ytick.major.size": 6,
    "xtick.minor.size": 3,
    "ytick.minor.size": 3,
    "xtick.top": True,
    "ytick.right": True,
})

fig, ax = plt.subplots(figsize=(12, 8))

# ── Renk paleti ──
colors = {
    "Gd157": "#E63946",   # Kırmızı
    "Gd155": "#F4A261",   # Turuncu
    "B10":   "#2A9D8F",   # Teal
    "Li6":   "#264653",   # Koyu mavi-yeşil
    "Li7":   "#A8DADC",   # Açık mavi
    "H1":    "#6A4C93",   # Mor (su arka planı)
    "O16":   "#999999",   # Gri (su arka planı)
}

# ── Eğrileri çiz ──
# Sıfır değerlerini maskele (log ölçekte sorun çıkarır)
def safe_plot(ax, x, y, **kwargs):
    mask = y > 0
    ax.plot(x[mask], y[mask], **kwargs)

safe_plot(ax, energy, gd157_xs, color=colors["Gd157"], linewidth=2.0,
          label=r"$^{157}$Gd  ($\sigma_{th}$ = 253729 b)")
safe_plot(ax, energy, gd155_xs, color=colors["Gd155"], linewidth=2.0,
          label=r"$^{155}$Gd  ($\sigma_{th}$ = 60899 b)")
safe_plot(ax, energy, b10_xs,   color=colors["B10"],   linewidth=2.0,
          label=r"$^{10}$B  ($\sigma_{th}$ = 3844 b)")
safe_plot(ax, energy, li6_xs,   color=colors["Li6"],   linewidth=2.0,
          label=r"$^{6}$Li  ($\sigma_{th}$ = 939 b)")
safe_plot(ax, energy, li7_xs,   color=colors["Li7"],   linewidth=1.5,
          linestyle="--",
          label=r"$^{7}$Li  ($\sigma_{th}$ = 0,05 b)")
safe_plot(ax, energy, h1_xs,    color=colors["H1"],    linewidth=1.8,
          linestyle="-.",
          label=r"$^{1}$H ($\sigma_{th}$ = 0.332 b)")
safe_plot(ax, energy, o16_xs,   color=colors["O16"],   linewidth=1.5,
          linestyle=":",
          label=r"$^{16}$O  ($\sigma_{th}$ = 1.9$\times10^{-4}$ b)")

# ── Termal enerji çizgisi ──
ax.axvline(x=0.0253, color="#333333", linestyle="--", linewidth=2.5, alpha=0.8,
           zorder=1)
ax.annotate(r"$E_{thermal}$ = 0.0253 eV",
            xy=(0.0253, 5e6), xytext=(0.5, 5e6),
            fontsize=12, fontweight="bold", color="#333333",
            arrowprops=dict(arrowstyle="->", color="#333333", lw=1.5),
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="#333333", alpha=0.9),
            va="center", ha="left")

# ── Eksen ayarları ──
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(1e-5, 2e7)
ax.set_ylim(1e-5, 1e8)

ax.set_xlabel("Neutron Energy (eV)", fontsize=15, fontweight="bold")
ax.set_ylabel("Cross Section (barn)", fontsize=15, fontweight="bold")
ax.set_title("Neutron Capture Cross Sections\n"
             "(G4NDL 4.7.1)",
             fontsize=16, fontweight="bold", pad=15)

# ── Legend ──
legend = ax.legend(loc="upper right", fontsize=12, framealpha=0.9,
                   edgecolor="gray", fancybox=True)
legend.get_frame().set_linewidth(0.8)

# ── Grid ──
ax.grid(True, which="major", linestyle="-", alpha=0.3, color="gray")
ax.grid(True, which="minor", linestyle=":", alpha=0.15, color="gray")

plt.tight_layout()

# ── Kaydet ──
output_png = "cross_section_plot.png"
output_pdf = "cross_section_plot.pdf"
plt.savefig(output_png, dpi=300, bbox_inches="tight")
plt.savefig(output_pdf, bbox_inches="tight")
print(f"[OK] Grafik kaydedildi: {output_png}, {output_pdf}")

plt.show()
