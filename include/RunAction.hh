#ifndef RUN_ACTION_HH
#define RUN_ACTION_HH

#include "G4UserRunAction.hh"
#include "G4AutoLock.hh"
#include "globals.hh"

class RunAction : public G4UserRunAction
{
public:
    RunAction();
    virtual ~RunAction();

    virtual void BeginOfRunAction(const G4Run* run) override;
    virtual void EndOfRunAction(const G4Run* run) override;

    static void AddCerenkovCount(G4int count);
    static G4int GetCerenkovCount();
    static void ResetCerenkovCount();

private:
    static G4int fCerenkovCount;
    static G4Mutex fMutex;
};

#endif
