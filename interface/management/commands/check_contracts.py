from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from emma.interface.models import *
import datetime
import logging
from django.core.management import setup_environ
import settings
setup_environ(settings)


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=os.path.join(settings.APP_LOGS_ROOT, 'check_contracts.log'),
                    filemode='w')

check_contracts_interval = getattr(settings, 'CHECK_CONTRACTS_INTERVAL', 365)
class Command(NoArgsCommand):
    """
    Check all contracts at a certain interval. If a contract is expired, reset it.
    The user will need to sign the contract again.
    """
    def handle_noargs(self, **options):
        for contract in Contract.objects.all():
            if datetime.date.today() == (contract.date_signed + datetime.timedelta(check_contracts_interval)):
                contract.contract = 0
                contract.save()
                logging.info('reset contract of user %s' % contract.username)
            else:
                logging.info('user contract %s OK' % contract.username)
            
    