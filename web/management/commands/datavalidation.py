

#python
from datetime import date, datetime, timedelta

#django
from django.core.management.base import NoArgsCommand, CommandError


#app

from web.models import *



class Command(NoArgsCommand):
    """Add test data
    """
    
    def handle_noargs(self, **options):
         
        print  'Checking for any non-staff users not linked to a Client'
        
        for user in User.objects.filter(is_staff = False):
            
            try:
                if user.get_profile().client:
                    pass
            except:
                print 'No client linked to user %s' % user.username
                
        print  'Checking Client balances are correct'
        
        for client in Client.objects.all():
            
            if client.balance != client.calculated_balance():
            
                print 'Client balance in model does not match sum of payments.  Balance = %.f2 and Payment total = %.f2' % (client.balance, client.calculated_balance())
                
                