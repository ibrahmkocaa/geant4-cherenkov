#include "PrimaryGeneratorAction.hh"
#include "G4ParticleGun.hh"
#include "G4ParticleTable.hh"
#include "G4SystemOfUnits.hh"
#include "G4RandomDirection.hh"
#include "G4Event.hh"

PrimaryGeneratorAction::PrimaryGeneratorAction()
{
    fParticleGun = new G4ParticleGun(1);

    auto particleTable = G4ParticleTable::GetParticleTable();
    auto neutron = particleTable->FindParticle("neutron");

    fParticleGun->SetParticleDefinition(neutron);
    fParticleGun->SetParticleEnergy(0.025 * eV);       
    fParticleGun->SetParticlePosition(G4ThreeVector(0., 0., 0.)); // tank merkezi
}

PrimaryGeneratorAction::~PrimaryGeneratorAction()
{
    delete fParticleGun;
}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* event)
{
    // izotropik yön
    G4ThreeVector direction = G4RandomDirection();
    fParticleGun->SetParticleMomentumDirection(direction);

    fParticleGun->GeneratePrimaryVertex(event);
}
