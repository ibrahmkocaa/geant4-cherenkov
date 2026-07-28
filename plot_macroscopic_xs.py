#!/usr/bin/env python3
"""
Makroskopik tesir kesiti (Σ) grafiği — katkılı su malzemeleri.
9 eğri: Gd, B, Li(enr.) × %1, %3, %5
"""

import numpy as np
import matplotlib.pyplot as plt

# ── CSV oku ──
data = np.genfromtxt("macroscopic_cross_sections.csv",
                     delimiter=",", skip_header=1)

energy = data[:, 0]  # eV

# Sütun düzeni: Energy, Gd1_total, Gd1_dopant, Gd3_total, Gd3_dopant, ...
# Her katkılayıcı × konsantrasyon için 2 sütun (total, dopant)
labels_order = [
    "Gd_0.1pct", "Gd_0.3pct", "Gd_0.5pct",
    "B_0.1pct",  "B_0.3pct",  "B_0.5pct",
    "Li_0.1pct", "Li_0.3pct", "Li_0.5pct",
]

# Sütun indeksleri: her label için total = 1+i*2, dopant = 2+i*2
total_cols = {label: 1 + i*2 for i, label in enumerate(labels_order)}
dopant_cols = {label: 2 + i*2 for i, label in enumerate(labels_order)}

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

fig, ax = plt.subplots(figsize=(13, 8))

# ── Renk ve stil tanımları ──
# Her element bir renk ailesi, her konsantrasyon farklı çizgi kalınlığı/stili
element_colors = {
    "Gd": "#E63946",   # kırmızı
    "B":  "#2A9D8F",   # yeşil-teal
    "Li": "#3A0CA3",   # indigo/mor
}

conc_styles = {
    "0.1pct": {"linewidth": 2.0, "linestyle": "--",  "alpha": 1.0},
    "0.3pct": {"linewidth": 2.4, "linestyle": "-.",  "alpha": 1.0},
    "0.5pct": {"linewidth": 2.8, "linestyle": "-",   "alpha": 1.0},
}

conc_labels = {"0.1pct": "0.1%", "0.3pct": "0.3%", "0.5pct": "0.5%"}

element_labels = {
    "Gd": "Gd",
    "B":  r"$^{10}$B",
    "Li": "Enriched Li",
}

# ── Eğrileri çiz ──
def safe_plot(ax, x, y, **kwargs):
    mask = y > 0
    ax.plot(x[mask], y[mask], **kwargs)

# Termal enerji indeksi
idx_th = np.argmin(np.abs(energy - 0.0253))

for element in ["Gd", "B", "Li"]:
    color = element_colors[element]
    for i, conc in enumerate(["0.1pct", "0.3pct", "0.5pct"]):
        label_key = f"{element}_{conc}"
        col_idx = total_cols[label_key]
        y = data[:, col_idx]

        # Termal Σ değerini legend'e ekle
        sigma_th = y[idx_th]
        label_text = (f"{element_labels[element]}  {conc_labels[conc]}"
                      f"  ($\\Sigma_{{th}}$ = {sigma_th:.2f} cm$^{{-1}}$)")

        safe_plot(ax, energy, y,
                  color=color,
                  linewidth=conc_styles[conc]["linewidth"],
                  linestyle=conc_styles[conc]["linestyle"],
                  alpha=conc_styles[conc]["alpha"],
                  label=label_text)

# ── Saf su arka plan çizgisi (Σ_H only) ──
# Σ_H = n_H × σ_H × 1e-24
# σ_H: gerçek G4NDL H-1 yakalama verisi (neutron_capture_cross_sections.csv),
# 1/v yaklaşımı yerine.
N_A = 6.022e23
n_H = 2 * 1.0 * N_A / 18.015          # H atom yoğunluğu (atom/cm³)

cap_data = np.genfromtxt("neutron_capture_cross_sections.csv",
                         delimiter=",", skip_header=1)
e_cap    = cap_data[:, 0]             # eV
sigma_H1 = cap_data[:, 6]            # barn — H1_barn sütunu
# Plot enerji grid'ine hizala (log-log interpolasyon; gridler aynı olsa da güvenli)
sigma_H = np.interp(np.log10(energy), np.log10(e_cap), sigma_H1)
Sigma_H = n_H * sigma_H * 1e-24       # cm⁻¹

Sigma_H_th = Sigma_H[idx_th]
safe_plot(ax, energy, Sigma_H,
          color="#777777", linewidth=1.8, linestyle=":",
          alpha=0.9,
          label=(r"Pure H$_2$O (baseline)"
                 f"  ($\\Sigma_{{th}}$ = {Sigma_H_th:.3f} cm$^{{-1}}$)"))

# ── Termal enerji çizgisi ──
ax.axvline(x=0.0253, color="#333333", linestyle="--", linewidth=2.5,
           alpha=0.8, zorder=1)
ax.annotate(r"$E_{thermal}$ = 0.0253 eV",
            xy=(0.0253, 8), xytext=(0.5, 8),
            fontsize=12, fontweight="bold", color="#333333",
            arrowprops=dict(arrowstyle="->", color="#333333", lw=1.5),
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="#333333", alpha=0.9),
            va="center", ha="left")

# ── Eksen ayarları ──
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(1e-5, 2e7)
ax.set_ylim(1e-4, 1e2)

ax.set_xlabel("Neutron Energy (eV)", fontsize=15, fontweight="bold")
ax.set_ylabel(r"Macroscopic Cross Section $\Sigma$ (cm$^{-1}$)",
              fontsize=15, fontweight="bold")
ax.set_title("Macroscopic Neutron Capture Cross Sections\n"
             "Doped Water Solutions (G4NDL 4.7.1)",
             fontsize=16, fontweight="bold", pad=15)

# ── Legend — element başlıkları ile gruplanmış ──
legend = ax.legend(loc="upper right", fontsize=11, framealpha=0.9,
                   edgecolor="gray", fancybox=True, ncol=1)
legend.get_frame().set_linewidth(0.8)

# ── Grid ──
ax.grid(True, which="major", linestyle="-", alpha=0.3, color="gray")
ax.grid(True, which="minor", linestyle=":", alpha=0.15, color="gray")

plt.tight_layout()

# ── Kaydet ──
output_png = "macroscopic_cross_section_plot.png"
output_pdf = "macroscopic_cross_section_plot.pdf"
plt.savefig(output_png, dpi=300, bbox_inches="tight")
plt.savefig(output_pdf, bbox_inches="tight")
print(f"[OK] Grafik kaydedildi: {output_png}, {output_pdf}")

plt.show()
