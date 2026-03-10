#include "RunAction.hh"
#include "G4Run.hh"
#include "G4SystemOfUnits.hh"
#include <iostream>

G4int RunAction::fCerenkovCount = 0;
G4Mutex RunAction::fMutex = G4MUTEX_INITIALIZER;

RunAction::RunAction() {}
RunAction::~RunAction() {}

void RunAction::AddCerenkovCount(G4int count)
{
    G4AutoLock lock(&fMutex);
    fCerenkovCount += count;
}

G4int RunAction::GetCerenkovCount()
{
    G4AutoLock lock(&fMutex);
    return fCerenkovCount;
}

void RunAction::ResetCerenkovCount()
{
    G4AutoLock lock(&fMutex);
    fCerenkovCount = 0;
}

void RunAction::BeginOfRunAction(const G4Run*)
{
    if (G4Threading::IsMasterThread()) {
        ResetCerenkovCount();
    }
}

void RunAction::EndOfRunAction(const G4Run* run)
{
    if (G4Threading::IsMasterThread()) {
        G4int nEvents = run->GetNumberOfEvent();
        G4int totalCerenkov = GetCerenkovCount();
        G4cout << "\n===== Run Summary =====" << G4endl;
        G4cout << "Total events: " << nEvents << G4endl;
        G4cout << "Total Cerenkov photons: " << totalCerenkov << G4endl;
        if (nEvents > 0) {
            G4cout << "Average Cerenkov photons/event: "
                   << (G4double)totalCerenkov / nEvents << G4endl;
        }
        G4cout << "=======================\n" << G4endl;
    }
}
