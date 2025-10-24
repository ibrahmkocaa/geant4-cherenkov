#include "SteppingAction.hh"
#include "G4Step.hh"
#include "G4Track.hh"
#include "G4ParticleDefinition.hh"
#include "G4ProcessType.hh"
#include "G4SystemOfUnits.hh"
#include "G4RunManager.hh"
#include "G4Event.hh"
#include "G4EventManager.hh"
#include "G4HadronicProcess.hh"
#include "G4Nucleus.hh"
#include "G4ios.hh"
#include <iostream>

SteppingAction::SteppingAction() {}
SteppingAction::~SteppingAction() {}

void SteppingAction::UserSteppingAction(const G4Step* step)
{
    const G4Track* track = step->GetTrack();
    G4String particleName = track->GetDefinition()->GetParticleName();

    // Sadece nötronlar
    if (particleName != "neutron") return;

    const G4VProcess* process = step->GetPostStepPoint()->GetProcessDefinedStep();
    if (!process) return;

    G4String processName = process->GetProcessName();

    // bilgiler
    G4int eventID = G4EventManager::GetEventManager()->GetConstCurrentEvent()->GetEventID();
    G4int trackID = track->GetTrackID();
    G4int stepNumber = track->GetCurrentStepNumber();

    G4ThreeVector position = step->GetPostStepPoint()->GetPosition();
    G4double globalTime = step->GetPostStepPoint()->GetGlobalTime();
    G4double stepLength = step->GetStepLength();
    G4double edep = step->GetTotalEnergyDeposit();
    G4double kineticE = track->GetKineticEnergy();
    G4TrackStatus status = track->GetTrackStatus();

    G4cout << "[Event " << eventID << "] [Track " << trackID << "] [Step " << stepNumber << "] [Neutron] "
           << "Proc=" << processName;

    // Hedef çekirdek bilgisi (Z, A) (tüm hadronic süreçler için)
    if (process->GetProcessType() == fHadronic) {
        G4HadronicProcess* hadProc = dynamic_cast<G4HadronicProcess*>(const_cast<G4VProcess*>(process));
        if (hadProc) {
            const G4Nucleus* targetNucleus = hadProc->GetTargetNucleus();
            if (targetNucleus) {
                G4int Z = targetNucleus->GetZ_asInt();
                G4int A = targetNucleus->GetA_asInt();
                G4cout << " | Target(Z=" << Z << ", A=" << A << ")";
            } else {
                G4cout << " | Target(unknown nucleus)";
            }
        }
    }

    G4cout << " | Pos=(" << position.x()/mm << ", " << position.y()/mm << ", " << position.z()/mm << ") mm"
           << " | Time=" << globalTime/ns << " ns"
           << " | StepLength=" << stepLength/mm << " mm"
           << " | Edep=" << edep/keV << " keV"
           << " | Ekin=" << kineticE/MeV << " MeV";

    if (processName == "nCapture") {
        G4HadronicProcess* hadProc = dynamic_cast<G4HadronicProcess*>(const_cast<G4VProcess*>(process));
        if (hadProc) {
            const G4Nucleus* targetNucleus = hadProc->GetTargetNucleus();
            if (targetNucleus) {
                G4int Z = targetNucleus->GetZ_asInt();
                G4int A = targetNucleus->GetA_asInt();
                G4cout << " | CapturedBy(Z=" << Z << ", A=" << A << ")";
            }
        }
    }

    // ikincil parçacıkları listele
    const std::vector<const G4Track*>* secondaries = step->GetSecondaryInCurrentStep();
    if (secondaries && !secondaries->empty()) {
        G4cout << "\n   --> Secondaries produced (" << secondaries->size() << "):";
        for (const auto& sec : *secondaries) {
            G4String secName = sec->GetDefinition()->GetParticleName();
            G4double secEkin = sec->GetKineticEnergy();
            G4ThreeVector secPos = sec->GetPosition();

            G4cout << "\n       * " << secName
                   << " | Ekin=" << secEkin/MeV << " MeV"
                   << " | Pos=(" << secPos.x()/mm << ", "
                   << secPos.y()/mm << ", "
                   << secPos.z()/mm << ") mm";
        }
    }

    // nötron sonlandıysa
    if (status == fStopAndKill || status == fKillTrackAndSecondaries) {
        G4cout << " | Neutron track ended (killed)";
    }

    // Eğer kaçış olduysa
    if (status == fStopAndKill && processName == "Transportation") {
        G4cout << " | Escaped from geometry!";
        G4cout << " | ExitPos=("
               << position.x()/mm << ", "
               << position.y()/mm << ", "
               << position.z()/mm << ") mm";
    }

    G4cout << G4endl;
}
