#include "G4Box.hh"
#include "G4Tubs.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4SystemOfUnits.hh"
#include "G4VisAttributes.hh"
#include "DetectorConstruction.hh"
#include "MaterialManager.hh" 

DetectorConstruction::DetectorConstruction() {}
DetectorConstruction::~DetectorConstruction() {}

G4VPhysicalVolume* DetectorConstruction::Construct()
{
    auto materials = MaterialManager::Instance();
    auto worldMat = materials->GetMaterial("G4_AIR");
    auto waterMat = materials->GetMaterial("G4_WATER");
    auto steelMat = materials->GetMaterial("G4_STAINLESS-STEEL");

    // --- Boyutlar ---
    G4double innerRadius = 525.7*mm;
    G4double innerHeight = 1193*mm;
    G4double wallThickness = 50*mm;
    G4double fullHeight = 1200*mm;
    G4double outerRadius = innerRadius + wallThickness;

    // --- World boyutları ---
    G4double worldSize = 2.5*(outerRadius);
    G4Box* solidWorld = new G4Box("World", worldSize, worldSize, worldSize);

    G4LogicalVolume* logicWorld =
        new G4LogicalVolume(solidWorld, worldMat, "World");
    G4VPhysicalVolume* physWorld =
        new G4PVPlacement(0, G4ThreeVector(), logicWorld, "World", 0, false, 0, true);

    // --- Su hacmi (iç silindir) ---
    G4Tubs* solidWater = new G4Tubs("WaterTank",
                                    0, innerRadius,
                                    0.5*innerHeight,
                                    0*deg, 360*deg);

    G4LogicalVolume* logicWater =
        new G4LogicalVolume(solidWater, waterMat, "WaterTank");
    new G4PVPlacement(0, G4ThreeVector(), logicWater,
                      "WaterTank", logicWorld, false, 0, true);

    // --- Tank duvarı (silindir kabuğu) ---
    G4Tubs* solidTank = new G4Tubs("TankShell",
                                   innerRadius,
                                   outerRadius,
                                   0.5*fullHeight,
                                   0*deg, 360*deg);

    G4LogicalVolume* logicTank =
        new G4LogicalVolume(solidTank, steelMat, "TankShell");
    new G4PVPlacement(0, G4ThreeVector(), logicTank,
                      "TankShell", logicWorld, false, 0, true);

    G4VisAttributes* waterVis = new G4VisAttributes(G4Colour(0.,0.,1.,0.4));
    waterVis->SetForceSolid(true);
    logicWater->SetVisAttributes(waterVis);

    G4VisAttributes* steelVis = new G4VisAttributes(G4Colour(0.5,0.5,0.5,0.1));
    steelVis->SetForceWireframe(true);
    logicTank->SetVisAttributes(steelVis);

    G4VisAttributes* worldVis = new G4VisAttributes();
    worldVis->SetVisibility(false);
    logicWorld->SetVisAttributes(worldVis);

    return physWorld;
}
