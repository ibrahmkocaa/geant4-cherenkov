#ifndef MATERIAL_MANAGER_HH
#define MATERIAL_MANAGER_HH

#include "G4Material.hh"
#include "G4NistManager.hh"
#include "globals.hh"
#include <map>

class MaterialManager
{
public:
    static MaterialManager* Instance();

    G4Material* GetMaterial(const G4String& name);

private:
    MaterialManager();             
    void CreateMaterials();       

    static MaterialManager* fInstance;
    std::map<G4String, G4Material*> fMaterials;
};

#endif
