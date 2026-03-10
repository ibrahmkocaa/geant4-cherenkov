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
        G4double fractionGd = 0.5 * perCent;   // %0.3 Gd
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
        G4double fractionB = 0.5 * perCent;   // %0.3 B
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
        G4double fractionLi = 0.5 * perCent;   // %0.3 Li
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

    // ==========================================================
    // Optik özellikler (Cherenkov için kırılma indisi gerekli)
    // ==========================================================
    {
        // Su için optik özellikler
        std::vector<G4double> photonEnergy = {
            2.034*eV, 2.068*eV, 2.103*eV, 2.139*eV,
            2.177*eV, 2.216*eV, 2.256*eV, 2.298*eV,
            2.341*eV, 2.386*eV, 2.433*eV, 2.481*eV,
            2.532*eV, 2.585*eV, 2.640*eV, 2.697*eV,
            2.757*eV, 2.820*eV, 2.885*eV, 2.954*eV,
            3.026*eV, 3.102*eV, 3.181*eV, 3.265*eV,
            3.353*eV, 3.446*eV, 3.545*eV, 3.649*eV,
            3.760*eV, 3.877*eV, 4.002*eV, 4.136*eV
        };

        std::vector<G4double> refractiveIndex = {
            1.3435, 1.344,  1.3445, 1.345,
            1.3455, 1.346,  1.3465, 1.347,
            1.3475, 1.348,  1.3485, 1.349,
            1.350,  1.3505, 1.351,  1.3518,
            1.3522, 1.3530, 1.3535, 1.354,
            1.355,  1.356,  1.357,  1.358,
            1.3590, 1.360,  1.3615, 1.363,
            1.3645, 1.366,  1.368,  1.370
        };

        std::vector<G4double> absorption = {
            3.448*m, 4.082*m, 6.329*m, 9.174*m,
            12.346*m, 13.889*m, 15.152*m, 17.241*m,
            18.868*m, 20.000*m, 26.316*m, 35.714*m,
            45.455*m, 47.619*m, 52.632*m, 52.632*m,
            55.556*m, 52.632*m, 52.632*m, 47.619*m,
            45.455*m, 41.667*m, 37.037*m, 33.333*m,
            30.000*m, 28.500*m, 27.000*m, 24.500*m,
            22.000*m, 19.500*m, 17.500*m, 14.500*m
        };

        G4MaterialPropertiesTable* waterMPT = new G4MaterialPropertiesTable();
        waterMPT->AddProperty("RINDEX", photonEnergy, refractiveIndex);
        waterMPT->AddProperty("ABSLENGTH", photonEnergy, absorption);

        fMaterials["G4_WATER"]->SetMaterialPropertiesTable(waterMPT);

        // Katkılı sulara da aynı optik özellikleri ata
        G4MaterialPropertiesTable* gdMPT = new G4MaterialPropertiesTable();
        gdMPT->AddProperty("RINDEX", photonEnergy, refractiveIndex);
        gdMPT->AddProperty("ABSLENGTH", photonEnergy, absorption);
        fMaterials["GdDopedWater"]->SetMaterialPropertiesTable(gdMPT);

        G4MaterialPropertiesTable* boronMPT = new G4MaterialPropertiesTable();
        boronMPT->AddProperty("RINDEX", photonEnergy, refractiveIndex);
        boronMPT->AddProperty("ABSLENGTH", photonEnergy, absorption);
        fMaterials["BoronDopedWater"]->SetMaterialPropertiesTable(boronMPT);

        G4MaterialPropertiesTable* liMPT = new G4MaterialPropertiesTable();
        liMPT->AddProperty("RINDEX", photonEnergy, refractiveIndex);
        liMPT->AddProperty("ABSLENGTH", photonEnergy, absorption);
        fMaterials["LithiumDopedWater"]->SetMaterialPropertiesTable(liMPT);
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
