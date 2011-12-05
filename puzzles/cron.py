from django_cron import cronScheduler, Job
from puzzles.models import *
import logging

logger = logging.getLogger(__name__)

class Synchronize(Job):
    run_every = 20
                                                                    
    def job(self):
        logger.error("run job")
        syncer.syncall()

cronScheduler.register(Synchronize)

