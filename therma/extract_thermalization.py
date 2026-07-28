#!/usr/bin/env python3
"""
Nötronun suda termalleşmesi (moderasyon) verilerini G4NDL'den çıkarır.

Termalleşmenin motoru ELASTİK SAÇILMADIR: hızlı nötron H çekirdeğine
elastik çarparak adım adım enerji kaybeder ve termal dengeye iner.

Çıkarılan veriler:
  - H-1  serbest atom elastik σ        (Elastic/CrossSection)
  - O-16 serbest atom elastik σ        (Elastic/CrossSection)
  - Suda BAĞLI H elastik+inelastik σ   (ThermalScattering, S(α,β), 293.6 K)

Bağlı su eğrisi, düşük enerjide kimyasal bağ etkisiyle serbest atomun
çok üstüne (~800 barn) çıkar — suyun neden bu kadar iyi moderatör
olduğunu gösteren asıl ilginç kısım budur.

Çıktı: thermalization_data.csv
"""

import zlib
import os
import csv
import numpy as np

# ── G4NDL veri dizini ──
G4NDL_DIR = "/usr/local/share/Geant4/data/G4NDL4.7.1"
ELASTIC_DIR = os.path.join(G4NDL_DIR, "Elastic", "CrossSection")
TSL_DIR = os.path.join(G4NDL_DIR, "ThermalScattering", "Inelastic", "CrossSection")

# Bağlı su için seçilen sıcaklık (oda sıcaklığı)
WATER_TEMPERATURE = 293.6  # K

# ── Moderasyon fiziği sabitleri ──
N_A = 6.02214076e23   # Avogadro (1/mol)
RHO_WATER = 1.0       # g/cm³
M_WATER = 18.015      # g/mol
E_FAST = 2.0e6        # eV  — başlangıç nötron enerjisi (2 MeV)
E_THERMAL = 0.0253    # eV  — termal enerji


def read_elastic(filepath):
    """G4NDL serbest-atom tesir kesiti dosyası (başlık satırı + (E,σ) çiftleri)."""
    with open(filepath, "rb") as f:
        raw = zlib.decompress(f.read()).decode("utf-8")
    lines = raw.strip().split("\n")
    values = []
    for line in lines[1:]:               # ilk satır = başlık (indeks/sayım)
        values.extend(float(t) for t in line.split())
    energies = np.array(values[0::2])    # eV
    xs = np.array(values[1::2])          # barn
    return energies, xs


def read_thermal_bound(filepath, temperature):
    """
    G4NDL ThermalScattering (S(α,β)) tesir kesiti dosyasını okur.
    Format: 'G4NDL', açıklama, ardından sıcaklık blokları:
        [flag] [n] [T] [npts]  ardından npts adet (E,σ) çifti.
    İstenen sıcaklığın bloğunu döndürür.
    """
    with open(filepath, "rb") as f:
        raw = zlib.decompress(f.read()).decode("utf-8")
    lines = raw.strip().split("\n")
    toks = " ".join(lines[2:]).split()   # 0,1 = 'G4NDL' ve açıklama satırı

    blocks = {}
    p = 0
    while p < len(toks):
        _flag = int(float(toks[p]))
        _n = int(float(toks[p + 1]))
        T = float(toks[p + 2])
        npts = int(float(toks[p + 3]))
        p += 4
        vals = toks[p:p + 2 * npts]
        p += 2 * npts
        arr = np.array([float(x) for x in vals]).reshape(-1, 2)
        blocks[T] = arr

    if temperature not in blocks:
        raise ValueError(f"{temperature} K bulunamadı. Mevcut: {list(blocks.keys())}")
    arr = blocks[temperature]
    return arr[:, 0], arr[:, 1]          # eV, barn


def interp_loglog(common_e, e, xs):
    """Veriyi ortak enerji grid'ine log-log uzayında interpolasyon yapar."""
    out = np.zeros_like(common_e)
    mask = (common_e >= e[0]) & (common_e <= e[-1])
    # log-log; sıfır σ değerlerine karşı küçük taban
    out[mask] = np.interp(np.log10(common_e[mask]), np.log10(e),
                          np.maximum(xs, 1e-30))
    return out


def xi_factor(A):
    """Ortalama logaritmik enerji azalımı ξ (çarpışma başına)."""
    if A == 1:
        return 1.0
    alpha = ((A - 1.0) / (A + 1.0)) ** 2
    return 1.0 + alpha / (1.0 - alpha) * np.log(alpha)


def main():
    print("=" * 66)
    print("  Nötron Termalleşmesi (Moderasyon) Verileri — G4NDL 4.7.1")
    print("=" * 66)
    print(f"  Elastic : {ELASTIC_DIR}")
    print(f"  Bağlı su: {TSL_DIR}  (T = {WATER_TEMPERATURE} K)\n")

    # ── Ortak enerji grid'i ──
    common_e = np.logspace(np.log10(1e-5), np.log10(2e7), 2000)

    # ── Veri okuma + interpolasyon ──
    eH, xsH = read_elastic(os.path.join(ELASTIC_DIR, "1_1_Hydrogen.z"))
    eO, xsO = read_elastic(os.path.join(ELASTIC_DIR, "8_16_Oxygen.z"))
    eW, xsW = read_thermal_bound(os.path.join(TSL_DIR, "h_water.z"),
                                 WATER_TEMPERATURE)

    H_free = interp_loglog(common_e, eH, xsH)
    O_free = interp_loglog(common_e, eO, xsO)
    H_bound = interp_loglog(common_e, eW, xsW)

    idx_th = np.argmin(np.abs(common_e - E_THERMAL))

    print(f"  {'':22s}{'σ(termal)':>12s} {'σ(1 eV)':>12s} {'σ(1 MeV)':>12s}")
    print("  " + "-" * 60)
    i1 = np.argmin(np.abs(common_e - 1.0))
    iM = np.argmin(np.abs(common_e - 1.0e6))
    for name, arr in [("H-1 serbest elastik", H_free),
                      ("O-16 serbest elastik", O_free),
                      ("H suda bağlı (S(a,b))", H_bound)]:
        print(f"  {name:22s}{arr[idx_th]:>10.2f} b {arr[i1]:>10.2f} b {arr[iM]:>10.3f} b")

    # ── CSV çıktısı ──
    output_file = "thermalization_data.csv"
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Energy_eV",
                         "H1_free_elastic_barn",
                         "O16_free_elastic_barn",
                         "H_bound_water_barn"])
        for i in range(len(common_e)):
            writer.writerow([f"{common_e[i]:.6e}",
                             f"{H_free[i]:.6e}",
                             f"{O_free[i]:.6e}",
                             f"{H_bound[i]:.6e}"])

    # ── Moderasyon metrikleri (serbest-atom, klasik teori) ──
    xi_H = xi_factor(1)
    xi_O = xi_factor(16)

    # Su için atom yoğunlukları
    n_mol = RHO_WATER * N_A / M_WATER     # H₂O molekül/cm³
    n_H = 2 * n_mol
    n_O = 1 * n_mol

    # Temsili serbest saçılma σ (epitermal plato, ~1 eV)
    sig_H = H_free[i1]    # ~20 b
    sig_O = O_free[i1]    # ~3.8 b

    Sigma_s_H = n_H * sig_H * 1e-24       # cm⁻¹
    Sigma_s_O = n_O * sig_O * 1e-24
    Sigma_s = Sigma_s_H + Sigma_s_O

    # Ağırlıklı ortalama ξ (saçılmaya göre)
    xi_bar = (xi_H * Sigma_s_H + xi_O * Sigma_s_O) / Sigma_s
    N_coll = np.log(E_FAST / E_THERMAL) / xi_bar
    slowing_power = xi_bar * Sigma_s     # ξΣ_s (cm⁻¹)
    mfp_s = 1.0 / Sigma_s                # saçılma serbest yolu (cm)

    print(f"\n{'=' * 66}")
    print("  Moderasyon Metrikleri (su, serbest-atom yaklaşımı)")
    print(f"{'=' * 66}")
    print(f"  ξ_H (H-1)                         = {xi_H:.4f}")
    print(f"  ξ_O (O-16)                        = {xi_O:.4f}")
    print(f"  Σ_s (saçılma, makro)              = {Sigma_s:.4f} cm⁻¹")
    print(f"  Saçılma serbest yolu (1/Σ_s)      = {mfp_s:.4f} cm")
    print(f"  ξ̄ (ağırlıklı ortalama)            = {xi_bar:.4f}")
    print(f"  2 MeV → termal çarpışma sayısı N  = {N_coll:.1f}")
    print(f"  Yavaşlatma gücü ξΣ_s              = {slowing_power:.4f} cm⁻¹")

    print(f"\n  → Suda bağlı H, termal altı enerjide serbest H'nin "
          f"\n    {H_bound[idx_th] / H_free[idx_th]:.1f} katına çıkar "
          f"(0.0253 eV: {H_bound[idx_th]:.0f} b vs {H_free[idx_th]:.0f} b)")
    print(f"  → Nötron ~{N_coll:.0f} elastik çarpışmada termalleşir.")
    print(f"\n  [OK] {output_file} yazıldı ({len(common_e)} veri noktası)")
    print(f"{'=' * 66}\n")


if __name__ == "__main__":
    main()
