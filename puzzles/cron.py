from django_cron import cronScheduler,Job

import syncer

import logging,random

logger = logging.getLogger(__name__)

class Synchronize(Job):
    run_every = 20
                                                                    
    def job(self):
        t = random.randint(0,100000)
        logger.error("running job: "+t)
        syncer.syncall()
        logger.error("run job: "+t)

cronScheduler.register(Synchronize)

