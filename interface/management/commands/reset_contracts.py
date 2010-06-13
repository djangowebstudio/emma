from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from emma.interface.models import *

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        c = Contract.objects.all()
        for contract in c:
            contract.contract = 0
            try:
                contract.save()
                print('contract for %s reset' % contract.username)
            except Exception, inst:
                raise CommandError(inst)
            