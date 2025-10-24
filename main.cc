// Gerekli Geant4 sınıfları ve C++ kütüphaneleri dahil ediliyor.
#include "G4RunManagerFactory.hh"       
#include "G4UImanager.hh"               
#include "G4UIExecutive.hh"             
#include "G4VisExecutive.hh"            
#include "QGSP_BERT_HP.hh"           
#include "QGSP_BIC_HP.hh"           
#include "FTFP_BERT_HP.hh"           
#include "DetectorConstruction.hh"  
#include "ActionInitialization.hh"  



int main(int argc, char** argv)
{
    auto* runManager = G4RunManagerFactory::CreateRunManager(G4RunManagerType::Default);

    runManager->SetUserInitialization(new DetectorConstruction());
    runManager->SetUserInitialization(new FTFP_BERT_HP());
    runManager->SetUserInitialization(new ActionInitialization());

    G4VisManager* visManager = new G4VisExecutive();
    visManager->Initialize();

    G4UImanager* UImanager = G4UImanager::GetUIpointer();

    if (argc == 1) {
        G4UIExecutive* ui = new G4UIExecutive(argc, argv);
        UImanager->ApplyCommand("/control/execute macros/vis.mac");
        ui->SessionStart();
        delete ui;
    } else {
        G4String command = "/control/execute ";
        G4String filename = argv[1];
        UImanager->ApplyCommand(command + filename);
    }

    delete visManager;
    delete runManager;
}