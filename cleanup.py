import sys, os
from django.core.management import setup_environ
import settings
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.getcwd(), 'libs'))
setup_environ(settings)

from web.models import Transaction

print "Looking for old, expired transactions..."
# add two days just to be safe...
expiry_safedate = datetime.now() + timedelta(days=2)
trans = Transaction.objects.filter(expire_at__lt=expiry_safedate, status__in=["A", "X", "C"])
print "Found %d old entries." % trans.count()
if trans.count():
    print "Deleting now..."
    trans.delete()
print "Done."
