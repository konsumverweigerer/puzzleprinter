from django.core.management.base import BaseCommand, CommandError
from django_cron import cronScheduler, Job
from puzzles.models import *

class Command(BaseCommand):
    args = '<order_id order_id...>'
    help = 'Synchronizes all data'

    def handle(self, *args, **options):
        pass

class Synchronize(Job):
    run_every = 300
                                                                    
    def job(self):
        pass

cronScheduler.register(Synchronize)
