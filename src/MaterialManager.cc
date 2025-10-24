#include "MaterialManager.hh"
#include "G4SystemOfUnits.hh"
#include "G4Element.hh"
#include "G4Material.hh"
#include "G4Isotope.hh"
#include <iostream>

MaterialManager* MaterialManager::fInstance = nullptr;

MaterialManager* MaterialManager::Instance()
{
    if (!fInstance)
        fInstance = new MaterialManager();
    return fInstance;
}

MaterialManager::MaterialManager()
{
    CreateMaterials();
}

void MaterialManager::CreateMaterials()
{
    auto nist = G4NistManager::Instance();

    // --- Temel malzemeler ---
    fMaterials["G4_WATER"] = nist->FindOrBuildMaterial("G4_WATER");
    fMaterials["G4_AIR"] = nist->FindOrBuildMaterial("G4_AIR");
    fMaterials["G4_STAINLESS-STEEL"] = nist->FindOrBuildMaterial("G4_STAINLESS-STEEL");

    // ==========================================================
    // 1. Gadolinyum katkılı su (%0.3 Gd)
    // ==========================================================
    {
        G4double density = 1.0 * g/cm3;
        G4double fractionGd = 0.1 * perCent;   // %0.3 Gd
        G4double fractionH2O = 100.0*perCent - fractionGd;

        G4Material* gdDopedWater = new G4Material("GdDopedWater", density, 2);
        gdDopedWater->AddMaterial(fMaterials["G4_WATER"], fractionH2O);
        gdDopedWater->AddElement(nist->FindOrBuildElement("Gd"), fractionGd);

        fMaterials["GdDopedWater"] = gdDopedWater;
    }

    // ==========================================================
    // 2. Boron katkılı su (%0.3 B)
    // ==========================================================
    {
        G4double density = 1.0 * g/cm3;
        G4double fractionB = 0.1 * perCent;   // %0.3 B
        G4double fractionH2O = 100.0*perCent - fractionB;

        G4Material* boronDopedWater = new G4Material("BoronDopedWater", density, 2);
        boronDopedWater->AddMaterial(fMaterials["G4_WATER"], fractionH2O);
        boronDopedWater->AddElement(nist->FindOrBuildElement("B"), fractionB);

        fMaterials["BoronDopedWater"] = boronDopedWater;
    }

    // ==========================================================
    // 3. Lityum katkılı su (%0.3 zenginleştirilmiş Li)
    // ==========================================================
    {
        G4double density = 1.0 * g/cm3;
        G4double fractionLi = 0.1 * perCent;   // %0.3 Li
        G4double fractionH2O = 100.0*perCent - fractionLi;

        // Li izotoplarını oluştur
        G4Isotope* isoLi6 = new G4Isotope("Li6", 3, 6, 6.015*g/mole);
        G4Isotope* isoLi7 = new G4Isotope("Li7", 3, 7, 7.016*g/mole);

        // Zenginleştirilmiş element (95% Li6, 5% Li7)
        G4Element* LiEnriched = new G4Element("EnrichedLithium", "Li", 2);
        LiEnriched->AddIsotope(isoLi6, 95.*perCent);
        LiEnriched->AddIsotope(isoLi7, 5.*perCent);

        // Lityum katkılı su malzemesi
        G4Material* lithiumDopedWater = new G4Material("LithiumDopedWater", density, 2);
        lithiumDopedWater->AddMaterial(fMaterials["G4_WATER"], fractionH2O);
        lithiumDopedWater->AddElement(LiEnriched, fractionLi);

        fMaterials["LithiumDopedWater"] = lithiumDopedWater;
    }

    G4cout << "[MaterialManager] Custom materials created successfully.\n" << G4endl;
}

G4Material* MaterialManager::GetMaterial(const G4String& name)
{
    if (fMaterials.count(name))
        return fMaterials[name];

    G4cerr << "[MaterialManager] Warning: Material '" << name
           << "' not found! Returning AIR instead.\n";
    return fMaterials["G4_AIR"];
}
