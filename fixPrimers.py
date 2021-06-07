import os
from sys import path as sysPath

sysPath.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from __init__ import db

from database import PrimerData, UserDataDB, PrimerDataDB

# recalculates primers

for user in UserDataDB.query.all():
    for comp in user.getAllComponents().all():
        oldPrimerData = comp.getPrimerData()

        if oldPrimerData.getPrimersFound():
            seq = comp.getSeq()

            TMgoal = (comp.getLeftTM() + comp.getRightTM()) / 2

            newPrimerData = PrimerData.makeNew(seq, TMgoal, 2)

            newPrimerData.addSpacerSeqs2(comp.getSpacerData())

            p = PrimerDataDB(
                primersFound=newPrimerData.getPrimersFound(),
                seqLeft=newPrimerData.getSeqLeft(),
                seqRight=newPrimerData.getSeqRight(),
                GCleft=newPrimerData.getGCleft(),
                GCright=newPrimerData.getGCright(),
                TMleft=newPrimerData.getTMleft(),
                TMright=newPrimerData.getTMright(),
            )

            # add to the database
            db.session.add(p)

            db.session.commit()

            comp.setPrimerDataID(p.getID())
            p.setCompID(comp.getID())

            db.session.delete(oldPrimerData)

            db.session.commit()  # is it necessary? perhaps
