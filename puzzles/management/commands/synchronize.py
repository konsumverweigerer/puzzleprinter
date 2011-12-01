from django.core.management.base import BaseCommand, CommandError
from puzzles.syncer import *
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = '<order_id order_id...>'
    help = 'Synchronizes all data'

    def handle(self, *args, **options):
        pass

