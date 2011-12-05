from django_cron import cronScheduler, Job
from puzzles.models import *
import logging,random

logger = logging.getLogger(__name__)

class Synchronize(Job):
    run_every = 20
                                                                    
    def job(self):
        t = random.randint(0,100000)
        logger.error("runnig job: "+t)
        syncer.syncall()
        logger.error("run job: "+t)

cronScheduler.register(Synchronize)

