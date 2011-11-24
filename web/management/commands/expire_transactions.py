from django.core.management.base import NoArgsCommand, CommandError

from web.models import Transaction

class Command(NoArgsCommand):
    """
    expire transactions passed their expiry date
    """
    
    def handle_noargs(self, **options):
        Transaction.expire_all()
        