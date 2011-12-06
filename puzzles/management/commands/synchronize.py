from django.core.management.base import BaseCommand, CommandError
from puzzles.syncer import *
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = '<order_id order_id...>'
    help = 'Synchronizes all data'

    def handle(self, *args, **options):
        if len(args)>0:
            if "all" == args[0]:
                syncall()
            elif "orders" == args[0]:
                addneworders()
            elif "prints" == args[0]:
                addnewprints()
            elif "status" == args[0]:
                addprintstatus()


