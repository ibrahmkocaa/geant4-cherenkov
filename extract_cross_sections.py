#!/usr/bin/env python3
"""
Geant4 G4NDL veri tabanından nötron absorpsiyon tesir kesitlerini çıkarır.
  - Li-6, Li-7, B-10 : Capture + Inelastic (n,t ve n,α reaksiyonları)
  - Gd-155, Gd-157   : Capture (radyatif yakalama baskın)
Çıktı: neutron_capture_cross_sections.csv
"""

import zlib
import os
import csv
import numpy as np

# ── G4NDL veri dizini ──
G4NDL_DIR = "/usr/local/share/Geant4/data/G4NDL4.7.1"
CAPTURE_DIR = os.path.join(G4NDL_DIR, "Capture", "CrossSection")
INELASTIC_DIR = os.path.join(G4NDL_DIR, "Inelastic", "CrossSection")

# ── Hedef izotoplar ve veri kaynakları ──
# "sources" listesi: (dizin, dosya adı) çiftleri — toplanarak toplam σ elde edilir
ISOTOPES = {
    "Li6": {
        "label": "Li-6",
        "sources": [
            (CAPTURE_DIR,   "3_6_Lithium.z"),
            (INELASTIC_DIR, "3_6_Lithium.z"),   # Li-6(n,t)α
        ]
    },
    "Li7": {
        "label": "Li-7",
        "sources": [
            (CAPTURE_DIR,   "3_7_Lithium.z"),
            (INELASTIC_DIR, "3_7_Lithium.z"),   # Li-7(n,n'α)t vb.
        ]
    },
    "B10": {
        "label": "B-10",
        "sources": [
            (CAPTURE_DIR,   "5_10_Boron.z"),
            (INELASTIC_DIR, "5_10_Boron.z"),    # B-10(n,α)Li-7
        ]
    },
    "Gd155": {
        "label": "Gd-155",
        "sources": [
            (CAPTURE_DIR,   "64_155_Gadolinium.z"),
            # Gd için inelastic ihmal edilebilir (capture >> inelastic)
        ]
    },
    "Gd157": {
        "label": "Gd-157",
        "sources": [
            (CAPTURE_DIR,   "64_157_Gadolinium.z"),
        ]
    },
    "H1": {
        "label": "H-1",
        "sources": [
            (CAPTURE_DIR,   "1_1_Hydrogen.z"),   # H-1(n,γ)D — su arka planı
        ]
    },
    "O16": {
        "label": "O-16",
        "sources": [
            (CAPTURE_DIR,   "8_16_Oxygen.z"),    # O-16(n,γ) — ihmal edilebilir
        ]
    },
}


def read_g4ndl_cross_section(filepath):
    """
    G4NDL zlib-sıkıştırılmış tesir kesiti dosyasını okur.
    Döndürür: (energies_eV, cross_sections_barn) numpy dizileri
    """
    with open(filepath, "rb") as f:
        raw = zlib.decompress(f.read()).decode("utf-8")

    lines = raw.strip().split("\n")
    values = []
    for line in lines[1:]:
        tokens = line.split()
        values.extend([float(t) for t in tokens])

    energies = np.array(values[0::2])       # eV
    cross_sections = np.array(values[1::2]) # barn

    return energies, cross_sections


def combine_cross_sections(sources, common_energies):
    """
    Birden fazla kaynaktaki tesir kesitlerini toplar (capture + inelastic).
    Ortak enerji grid'ine interpolasyon yapar.
    """
    total_xs = np.zeros_like(common_energies)

    for directory, filename in sources:
        filepath = os.path.join(directory, filename)
        if not os.path.exists(filepath):
            print(f"    [WARNING] Dosya bulunamadı: {filepath}")
            continue

        energies, xs = read_g4ndl_cross_section(filepath)
        source_type = "Capture" if "Capture" in directory else "Inelastic"

        # Ortak grid'e interpolasyon (log-log uzayında)
        log_e = np.log10(common_energies)
        log_e_data = np.log10(energies)

        # Enerji aralığı dışındakileri 0 yap
        mask = (common_energies >= energies[0]) & (common_energies <= energies[-1])
        interp_xs = np.zeros_like(common_energies)
        interp_xs[mask] = np.interp(log_e[mask], log_e_data, xs)

        xs_thermal = np.interp(0.0253, energies, xs)
        print(f"    {source_type:10s} : {len(energies):6d} pts, "
              f"σ(0.0253 eV) = {xs_thermal:12.2f} barn")

        total_xs += interp_xs

    return total_xs


def main():
    print("=" * 64)
    print("  Neutron Absorption Cross-Section Extraction from G4NDL")
    print("  (Capture + Inelastic)")
    print("=" * 64)
    print(f"  Data: {G4NDL_DIR}\n")

    # ── Ortak enerji grid'i: 1e-5 eV — 2e7 eV, 2000 logaritmik nokta ──
    e_min, e_max = 1e-5, 2e7
    common_energies = np.logspace(np.log10(e_min), np.log10(e_max), 2000)

    # ── Her izotop için tesir kesitlerini hesapla ──
    results = {}
    for name, info in ISOTOPES.items():
        print(f"\n  [{info['label']}]")
        total_xs = combine_cross_sections(info["sources"], common_energies)
        results[name] = total_xs

        # Termal değer
        idx_thermal = np.argmin(np.abs(common_energies - 0.0253))
        print(f"    TOPLAM   : σ(0.0253 eV) = {total_xs[idx_thermal]:12.2f} barn")

    # ── CSV çıktısı ──
    output_file = "neutron_capture_cross_sections.csv"
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        header = ["Energy_eV"] + [f"{name}_barn" for name in ISOTOPES.keys()]
        writer.writerow(header)

        for i, energy in enumerate(common_energies):
            row = [f"{energy:.6e}"]
            for name in ISOTOPES.keys():
                row.append(f"{results[name][i]:.6e}")
            writer.writerow(row)

    # ── Özet tablo ──
    print(f"\n{'=' * 64}")
    print(f"  Termal Nötron Tesir Kesitleri (E = 0.0253 eV)")
    print(f"  {'İzotop':<10s} {'Capture':>12s} {'Inelastic':>12s} {'TOPLAM':>12s}")
    print(f"  {'-'*48}")

    idx_th = np.argmin(np.abs(common_energies - 0.0253))
    for name, info in ISOTOPES.items():
        print(f"  {info['label']:<10s} {'—':>12s} {'—':>12s} "
              f"{results[name][idx_th]:>12.2f} barn")

    print(f"\n  [OK] {output_file} yazıldı ({len(common_energies)} veri noktası)")
    print(f"{'=' * 64}\n")


if __name__ == "__main__":
    main()
