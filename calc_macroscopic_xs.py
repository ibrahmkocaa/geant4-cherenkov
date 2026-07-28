#!/usr/bin/env python3
"""
Katkılı su malzemelerinin makroskopik tesir kesitlerini (Σ) hesaplar.
Σ = n × σ  (n: atom yoğunluğu, σ: mikroskopik tesir kesiti)

Katkılayıcılar:
  - Gd (doğal: %14.80 Gd-155, %15.65 Gd-157)
  - B  (zenginleştirilmiş: %96 B-10, %4 B-11)
  - Li (zenginleştirilmiş: %95 Li-6, %5 Li-7)

Konsantrasyonlar: %0.1, %0.3, %0.5 kütle oranı
"""

import numpy as np
import csv

# ── Sabitler ──
N_A = 6.02214076e23      # Avogadro sayısı (1/mol)
RHO_WATER = 1.0           # g/cm³ (katkılı su yoğunluğu ≈ saf su)
M_WATER = 18.015          # g/mol (H₂O)

# ── İzotop verileri ──
# Atom kütleleri (g/mol)
A = {
    "Li6": 6.015, "Li7": 7.016,
    "B10": 10.013, "B11": 11.009,
    "Gd155": 154.923, "Gd157": 156.924,
    "H1": 1.008, "O16": 15.999,
}

# Doğal izotop bolluğu
NATURAL_ABUNDANCE = {
    "Gd": {"Gd155": 0.1480, "Gd157": 0.1565},  # diğer Gd izotopları ihmal
}

# Zenginleştirilmiş Li (projedeki gibi)
ENRICHED_LI = {"Li6": 0.95, "Li7": 0.05}

# Zenginleştirilmiş B (projedeki gibi) — B-11 yakalama ihmal (σ ≈ 0.005 barn)
ENRICHED_B = {"B10": 0.96}

# Ortalama atom kütleleri (katkılayıcı element bazında)
A_ELEMENT = {
    "Gd": 157.25,  # doğal Gd
    "B":  0.96 * A["B10"] + 0.04 * A["B11"],   # zenginleştirilmiş B (~10.05)
    "Li": 0.95 * A["Li6"] + 0.05 * A["Li7"],  # zenginleştirilmiş Li
}

# H-1 termal nötron yakalama tesir kesiti (barn) — su bazlı arka plan
SIGMA_H_THERMAL = 0.332  # barn

# Konsantrasyonlar (kütle oranı)
CONCENTRATIONS = [0.001, 0.003, 0.005]   # %0.1, %0.3, %0.5


def read_cross_section_csv(filename="neutron_capture_cross_sections.csv"):
    """CSV'den enerji ve izotop tesir kesitlerini okur."""
    data = np.genfromtxt(filename, delimiter=",", skip_header=1)
    return {
        "energy": data[:, 0],    # eV
        "Li6":    data[:, 1],    # barn
        "Li7":    data[:, 2],
        "B10":    data[:, 3],
        "Gd155":  data[:, 4],
        "Gd157":  data[:, 5],
    }


def calc_number_density(mass_fraction, rho, A_element):
    """
    Katkılayıcının atom yoğunluğunu hesaplar (atom/cm³).
    n = w × ρ × N_A / A
    """
    return mass_fraction * rho * N_A / A_element


def calc_macroscopic_xs(sigma_data, dopant_type, concentration):
    """
    Makroskopik tesir kesitini (Σ) hesaplar: Σ = n × σ  (cm⁻¹)

    Toplam = Σ(katkılayıcı izotopları) + Σ(H in water)
    """
    energy = sigma_data["energy"]
    w = concentration

    # Katkılayıcı atom yoğunluğu
    n_dopant = calc_number_density(w, RHO_WATER, A_ELEMENT[dopant_type])

    # Su kısmının H atom yoğunluğu (2 H per H₂O)
    n_H = 2 * (1 - w) * RHO_WATER * N_A / M_WATER

    # H yakalama tesir kesiti (~1/v davranışı: σ(E) = σ_th × sqrt(0.0253/E))
    sigma_H = SIGMA_H_THERMAL * np.sqrt(0.0253 / np.maximum(energy, 1e-10))
    sigma_H = np.minimum(sigma_H, 1e6)  # çok düşük enerjilerde sınırla

    # Σ_H (su arka plan) — barn → cm²: 1 barn = 1e-24 cm²
    Sigma_H = n_H * sigma_H * 1e-24     # cm⁻¹

    # Katkılayıcı izotoplarının katkısı
    Sigma_dopant = np.zeros_like(energy)

    if dopant_type == "Gd":
        for iso, abundance in NATURAL_ABUNDANCE["Gd"].items():
            n_iso = n_dopant * abundance
            Sigma_dopant += n_iso * sigma_data[iso] * 1e-24
    elif dopant_type == "B":
        for iso, abundance in ENRICHED_B.items():
            n_iso = n_dopant * abundance
            Sigma_dopant += n_iso * sigma_data[iso] * 1e-24
    elif dopant_type == "Li":
        for iso, abundance in ENRICHED_LI.items():
            n_iso = n_dopant * abundance
            Sigma_dopant += n_iso * sigma_data[iso] * 1e-24

    Sigma_total = Sigma_dopant + Sigma_H

    return {
        "energy": energy,
        "Sigma_dopant": Sigma_dopant,    # cm⁻¹
        "Sigma_H": Sigma_H,             # cm⁻¹
        "Sigma_total": Sigma_total,      # cm⁻¹
    }


def main():
    print("=" * 70)
    print("  Makroskopik Tesir Kesiti (Σ) Hesabı — Katkılı Su Malzemeleri")
    print("=" * 70)

    sigma_data = read_cross_section_csv()

    # ── Termal enerji indeksi ──
    idx_th = np.argmin(np.abs(sigma_data["energy"] - 0.0253))

    # ── Sonuç tablosu ──
    print(f"\n  {'Katkılayıcı':<12s} {'Kons.':<8s} "
          f"{'n_dopant':<14s} {'Σ_dopant':<14s} {'Σ_H(su)':<14s} "
          f"{'Σ_toplam':<14s} {'λ_mfp':<10s}")
    print(f"  {'':12s} {'':8s} "
          f"{'(atom/cm³)':14s} {'(cm⁻¹)':14s} {'(cm⁻¹)':14s} "
          f"{'(cm⁻¹)':14s} {'(cm)':10s}")
    print("  " + "-" * 85)

    # ── CSV çıktısı ──
    output_csv = "macroscopic_cross_sections.csv"
    header = ["Energy_eV"]

    all_results = {}

    for dopant in ["Gd", "B", "Li"]:
        for conc in CONCENTRATIONS:
            result = calc_macroscopic_xs(sigma_data, dopant, conc)
            label = f"{dopant}_{conc*100:g}pct"   # ör. Gd_0.1pct
            all_results[label] = result
            header.append(f"{label}_Sigma_total_cm-1")
            header.append(f"{label}_Sigma_dopant_cm-1")

            # Termal değerler
            Sigma_d_th = result["Sigma_dopant"][idx_th]
            Sigma_H_th = result["Sigma_H"][idx_th]
            Sigma_tot_th = result["Sigma_total"][idx_th]
            n_d = calc_number_density(conc, RHO_WATER, A_ELEMENT[dopant])
            mfp = 1.0 / Sigma_tot_th if Sigma_tot_th > 0 else float('inf')

            conc_label = f"%{conc*100:g}"
            if dopant == "Li":
                dopant_label = f"Li(enr.)"
            elif dopant == "B":
                dopant_label = f"B(enr.)"
            else:
                dopant_label = dopant

            print(f"  {dopant_label:<12s} {conc_label:<8s} "
                  f"{n_d:<14.4e} {Sigma_d_th:<14.6f} {Sigma_H_th:<14.6f} "
                  f"{Sigma_tot_th:<14.6f} {mfp:<10.4f}")

    # ── CSV dosyasına yaz ──
    energy = sigma_data["energy"]
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for i in range(len(energy)):
            row = [f"{energy[i]:.6e}"]
            for label, result in all_results.items():
                row.append(f"{result['Sigma_total'][i]:.6e}")
                row.append(f"{result['Sigma_dopant'][i]:.6e}")
            writer.writerow(row)

    # ── Özet: aynı konsantrasyonda (%0.3) katkılayıcı karşılaştırması ──
    print(f"\n{'=' * 70}")
    print(f"  Karşılaştırma: %0.3 katkıda Gd / B / Li (aynı kütle oranı)")
    print(f"{'=' * 70}")

    r_gd = all_results["Gd_0.3pct"]
    r_b  = all_results["B_0.3pct"]
    r_li = all_results["Li_0.3pct"]

    print(f"\n  {'':18s} {'Σ_dopant (cm⁻¹)':>18s} {'Σ_toplam (cm⁻¹)':>18s} {'MFP (cm)':>10s}")
    print(f"  {'-'*65}")

    for label, res in [("%0.3 Gd", r_gd), ("%0.3 B(enr.)", r_b), ("%0.3 Li(enr.)", r_li)]:
        Sd = res["Sigma_dopant"][idx_th]
        St = res["Sigma_total"][idx_th]
        mfp = 1.0/St if St > 0 else float('inf')
        print(f"  {label:18s} {Sd:18.6f} {St:18.6f} {mfp:10.4f}")

    print(f"\n  → Aynı kütle oranında zenginleştirilmiş B, en yüksek makroskopik")
    print(f"    tesir kesitini verir (en kısa yakalama yolu): B > Gd > Li.")
    print(f"    Bunun nedeni B'nin çok daha düşük atom kütlesi (~10) sayesinde")
    print(f"    aynı kütle oranında çok daha yüksek atom yoğunluğuna ulaşmasıdır.")

    print(f"\n  [OK] {output_csv} yazıldı ({len(energy)} veri noktası)")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
