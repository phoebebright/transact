#python
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuidfield import UUIDField
from collections import defaultdict

#django
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.mail import send_mail, EmailMessage
from django.core.mail import send_mail, EmailMessage
from django.db import models
from django.db.models import Max, Q, Sum
from django.db.models.query import QuerySet
from django.db.models.signals import post_save
from django.http import Http404
from django.template import Context, Template
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

#app
import config
from livesettings import config_value
from web.exceptions import *
from utils.models import Notification, MailLog

"""
Decimals are used for both money values and for quantities.
Money values are held to 2 decimal places and the model should round as required before 
  returning a value.  It is for the API to ensure that the format of the number is correct.
Quantities are held to 3 decimal places to ensure that when a transaction for a specific value
  is requested, it can be filled exactly.  If only 2dp used, then you might not get a 
  transaction for EUR100.00, it might be EUR99.95
"""

# Used to quantize decimals for monetary values
TWODP = Decimal('0.01')
QTYDP = Decimal('0.001')

# number of decimal places used for quantities
QTY_NUM_DP = 3   

CURRENCIES = (('EUR','EUR'), ('GBP','GBP'), ('USD','USD'))
QUALITIES = (
    ('B','Bronze'),
    ('S','Silver'),
    ('G','Gold'),
    ('P','Platinum'),
    )
STATUS = (
    ('A', 'Pending'),
    ('C', 'Cancelled'),
    ('P', 'Paid'),
    ('X', 'Expired'),
    )

PAYMENT_STATUS = (
    ('F', 'Failed'),
    ('S', 'Success'),
    )

def LISTQUALITIES():
    """
    List of valid Product Qualities
    """
    
    return QUALITIES
    
    
class ProductType(models.Model):
    """
    Each product has a type
    eg. HYDR - Hydro, WIND - Wind, BIOM - Biomass
    """
    code = models.CharField(_('Product Code'), max_length=4, primary_key=True)
    name = models.CharField(_('Product Type'), max_length=32, unique=True)

    def __unicode__(self):
        return self.code 

    class Meta:
        ordering = ['code', ]
        verbose_name = "Product Type"
        verbose_name_plural = "Product Types"

    @classmethod
    def LISTTYPES(self):
    
        return self.objects.all()
        
            
class Customer(models.Model):
    """
    Customer is the person for whom the Client is purchasing the Product
    We may not know who the customer is, in which case we will allocate the 
    purchase to an anonymous user.
    Every Client must have one Anonymous Customer
    """

    anonymous = models.BooleanField(_('Anonymous'), default=True)
    name = models.CharField(_('Client Name'), max_length=50)
    clients = models.ManyToManyField('Client', through='Relationship')
    
    def __unicode__(self):
        return self.name 

    class Meta:
        ordering = ['name', ]

    
class Client(models.Model):
    """
    Clients purchase Products
    Only Clients can use the API
    
    Topup Values:
    topup_at_level - when the account falls below this value, automatically topup
        defaults to the maximum quantity that can be bought
    top_amount - amount to topup by  - default is maximum quantity again.
    balance is recalculated each time a payment occurs.  This avoids hitting the payment
       table each time the balance is checked.
       
    Note that notification_user field is optional. If not specified, no notifications are sent.
    """
    
    uuid = UUIDField(auto=True)
    name = models.CharField(_('Client Name'), max_length=50, unique=True)
    balance = models.DecimalField(_('Balance'), max_digits=9, decimal_places=2,default =0)
    currency = models.CharField(_('Default Currency'),  max_length=3, choices=CURRENCIES, default='EUR')
    quality = models.CharField(_('Default Quality'),  max_length=1, choices=QUALITIES, blank=True, null=True)
    type =  models.ForeignKey(ProductType, verbose_name = _('Default Product Type'), blank=True, null=True)
    recharge_level =  models.DecimalField(_('Topup at this level'), max_digits=9, decimal_places=2, default =10)
    recharge_by =  models.DecimalField(_('Topup by this amount'), max_digits=9, decimal_places=2, default=10)
    active = models.BooleanField(_('Active'), default=True)
    joined = models.DateTimeField(_('Created Date/Time'), auto_now_add=True)
    customers = models.ManyToManyField(Customer, through='Relationship')
    notification_user = models.ForeignKey(User, blank=True, null=True)
    
    
    def __unicode__(self):
        return self.name 

    class Meta:
        ordering = ['name', ]

    def save(self, *args, **kwargs):
        # every Client must have an anonymous Customer
        # so create one when a new client is added
        create_customer = not self.pk
                    
        super(Client, self).save(*args, **kwargs)
        
        # if new client, create an anonymous customer and link through relationship
        if create_customer:
            cust = Customer.objects.create(
                anonymous = True)
                
            Relationship.objects.create(
                client = self,
                customer = cust)
    
    def needs_recharge(self, amount = 0):
        """ Return True if the balance is below the recharge level
            Allow an option paramter to check if by including an amount that will take
            it below the recharge level.
        """
        
        return (self.balance + Decimal(str(amount)) <= self.recharge_level)
    
    def update_balance(self, amount):
        """ update the balanace only from this method.
            amounts may be positive or negative
            
            do recharge if drops below recharge level
            
            NOTE: for some reason, self.balance can hold
            an old value for balance, so have to get it
            again here to ensure it works.  Try removing
            the update and running tests to see if it
            still causes a problem.  Currently failing at
            the end of test_client_balance_and_recharge (PHB)
        """
        
        # get again to ensure have most up to date balance
        c=Client.objects.get(id=self.id)
 
        self.balance = c.balance + amount
        self.save(force_update=True)
        
        if self.needs_recharge():
            self.recharge(self.recharge_by)
        
    def transaction_fee(self):
        """in future fee can be varied by Client.
        for the moment return the default
        """
        
        return Decimal(config_value('web','DEFAULT_FEE'))
        
    def recharge(self, amount=0):
        """ Topup the client's account when it runs low
        return amount topped up by
        """
        if amount == 0:
            amount = self.topup_by
  
        else:
            amount = Decimal(str(amount))
            
            
        if amount > 0:

            Payment.objects.create(
                client = self,
                payment_type = 'R',
                amount = amount)
                
            self.recharge_notification()                                    

        return amount

    def recharge_notification(self):
        """ Send notificaiton of recharge if an email field is specified
        """

        if self.notification_user:
            try:
                notify = ClientNotification.objects.get(name='AccountRecharge')
            except ClientNotification.DoesNotExist:
                raise MissingRechargeNotification
       
            return notify.notify(self.notification_user.email, client=self, context = {'NOW': datetime.now()},)
         
               
     
        
    def can_pay(self, amount):
        """Check there are enough funds to pay this amount
        """

        return (Decimal(str(amount)) <= self.balance)
        
    def calculated_balance(self):
        """ Calculate client balance as sum of all payments
        This should always be the same as the client.balance amount
        Note that it assumes that all transactions for a client
        are off the same currency
        """
       
        p = Payment.objects.filter(client = self).aggregate(balance=Sum('amount'))
        
        if p['balance'] == None:
            return 0
        else:
            return p['balance']

        
            
class Relationship(models.Model):
    """
    Links customers to client
    A customer by be the customer of many clients
    A customer can be a standalone customer, not linked to a client - although
      there is currently no functionality for a customer to purchase directly
    """
    customer = models.ForeignKey(Customer)
    client = models.ForeignKey(Client)
    
'''
Not implemented yet
class Auth(models.Model):
    """
    Authority given by a User to access the system
    Privileges can be controlled
    """
    
    uuid = UUIDField(auto=True)
    user = models.ForeignKey(User)
    alias = models.CharField(_('Alias'),  max_length=32, null=True)
    allowed = models.CharField(_('Allowed API Calls'),  max_length=100, blank=True, null=True)
    expire_at = models.DateTimeField(_('Expire ated Date/Time'), null=True)
    
    def __unicode__(self):
        return self.alias 

    class Meta:
        ordering = ['-uuid', ]
    
    def save(self, *args, **kwargs):
        # set alias to uuid if alias not specified
        if not self.alias:
            self.alias = self.uuid
            
        super(Auth, self).save(*args, **kwargs)
'''   

class Trade(models.Model):
    """
    Record purchase of Carbon Credits from an Exchange
    """
    
    name = models.CharField(_('Carbon Credit Name'), max_length=50)
    purchfrom = models.CharField(_('Purchased From'),  max_length=12)
    purchwhen = models.DateTimeField(_('Purchase Date/Time'), auto_now_add=True, editable=True)
    total = models.DecimalField(_('Total Paid'), max_digits=9, decimal_places=2,default =0)
    currency = models.CharField(_('Default Currency'),  max_length=3, choices=CURRENCIES, default='EUR')
    tonnes =  models.DecimalField(_('Tonnes'), max_digits=9, decimal_places=QTY_NUM_DP)
    ref =  models.CharField(_('Purchase Ref'), max_length=50, blank=True, null=True)
    
    def __unicode__(self):
        return self.name 

    class Meta:
        ordering = ['-purchwhen', ]

    def save(self, *args, **kwargs):
        # adding a trade automatically creates a new product
        create_product = not self.pk
                    
        super(Trade, self).save(*args, **kwargs)
        
        if create_product:
            Product.objects.create(name=self.name,
                trade=self,
                currency = self.currency,
                price = (Decimal(self.total)/Decimal(self.tonnes)*(Decimal('1')+Decimal(config_value('web','PROFIT_MARGIN')))),
                quantity_purchased=self.tonnes)
            
class Product(models.Model):
    """
    Products sold by Transact
    """
    uuid = UUIDField(auto=True)
    name = models.CharField(_('Product Name'), max_length=50)
    trade = models.ForeignKey(Trade)
    quality = models.CharField(_('Default Quality'),  max_length=1, choices=QUALITIES, blank=True, null=True)
    type =  models.ForeignKey(ProductType, verbose_name = _('Default Product Type'), blank=True, null=True)
    price = models.DecimalField(_('Price'), max_digits=9, decimal_places=2,default =0)
    currency = models.CharField(_('Default Currency'),  max_length=3, choices=CURRENCIES, default=config_value('web','DEFAULT_CURRENCY'))
    quantity_purchased =  models.DecimalField(_('Quantity Purchased'), max_digits=9, decimal_places=QTY_NUM_DP)
    quantity2pool =  models.DecimalField(_('Quantity Moved to Pool'), max_digits=9, decimal_places=QTY_NUM_DP, default=0)
    
    def __unicode__(self):
        return self.name 

    class Meta:
        ordering = ['-name', ]

    def move2pool(self, max_qty=1000, user=None):
        """
        add entries to the pool, maximum of 1000 units per entry
        make sure only added once
        """
        
        # check quality and type have been added
        
        if not self.quality:
            raise ProductQualityRequired
        if not self.type:
            raise ProductTypeRequired
        

        # TODO: split a large quantity into multiple records if required
        
        # add product to pool
        
        Pool.objects.create(product=self,
            quantity=self.quantity_purchased,
            quality=self.quality,
            type = self.type,
            price = self.price)

        # deduct from quantity2pool 
        self.quantity2pool = self.quantity_purchased
        self.save()
        
        # call PoolLevel to ensure there is a record in there for this quality/type
        PoolLevel.check_level_ok(self.quality, self.type)
        
                 
        return True

    @property
    def quality_name(self):
        """return quality name from quaility field"""
        for (code,name) in QUALITIES:
            if code == self.quality:
                return name

class Pool(models.Model):
    """
    Products currently available for sale
    This is a denormalised entity to make it quicker and to avoid contention
    quantity is decreased each time a transaction is completed
    the record is deleted when the quantity reaches zero once all transaction related to this
     pool item are closed
    Note that the transactions linked to a pool item must not be deleted if a pool item is deleted
    """
    
    uuid = UUIDField(auto=True)
    product = models.ForeignKey(Product)
    quantity =  models.DecimalField(_('Quantity Available'), max_digits=9, decimal_places=QTY_NUM_DP)
    quality = models.CharField(_('Default Quality'),  max_length=1, choices=QUALITIES, blank=True, null=True)
    type =  models.ForeignKey(ProductType, verbose_name = _('Default Product Type'), blank=True, null=True)
    price = models.DecimalField(_('Price'), max_digits=9, decimal_places=2,default =0)
    currency = models.CharField(_('Default Currency'),  max_length=3, choices=CURRENCIES, default=config_value('web','DEFAULT_CURRENCY'))
    added = models.DateTimeField(_('Added to Pool Date/Time'), auto_now_add=True)
    
    
    def __unicode__(self):
        return self.product.name

    class Meta:
        ordering = ['-id', ]
        verbose_name = "Pool"
        verbose_name_plural = "Pool"

    def total_price(self, qty, client=None):
        """
        Return total price including fees for specified quantity
        """

        if client:
            fee = client.transaction_fee()
        else:
            fee = config_value('web','DEFAULT_FEE')
            
        return ((self.price * qty) + fee).quantize(TWODP)

    '''
    NOT USED
    def qty_for_price(self, price, client=None):
        """
        Return quantity that can be bought for a specified price
        """

        if client:
            price -= client.transaction_fee()
        else:
            price -= config_value('web','DEFAULT_FEE')
            
        return (price / self.price).quantize(QTYDP)
    '''
    
    @classmethod
    def LISTPRODUCTS(self):
        """
        List of currently available products
        """
        print '-->',config_value('web','MIN_QUANTITY')
        return self.objects.filter(quantity__gte = config_value('web','MIN_QUANTITY'))
    
    def remove_quantity(self, units):
        """
        decrease quantity by units
        """
        
        if units > self.quantity:
            raise Unable2RemoveUnits
        else:
            self.quantity = self.quantity - Decimal(str(units))
            self.save()
            
            PoolLevel.check_level_ok(quality = self.quality, type = self.type)
            
    @classmethod
    def level(self, quality=None, type=None):
        """
        calculate the number of units in the pool for a specific
        quality and type.  If quality and/or type not specified, 
        calculate for all.
        """
        
        query = self.objects.all()
        
        if quality:
            query = query.filter(quality=quality)
            
        if type:
            query = query.filter(type=type)
            
        return query.aggregate(Sum('quantity')).values()[0]
        
        
        
    @classmethod
    def PRICECHECK(cls, quantity, quality=None, type=None, client=None):
        """
        returns the product id of the first product added to the pool that matches the requirements
        """
  
        # valid quantity
        
        if isinstance(quantity,Decimal):
            qty=quantity
        else:
            qty = Decimal(str(quantity))

        if qty < config_value('web','MIN_QUANTITY'):
            raise BelowMinQuantity

        if qty > config_value('web','MAX_QUANTITY'):
            raise AboveMaxQuantity
            
        # convert type to ProductType if required
        if type and type>' ' and not isinstance(type, ProductType):
            try:
                type = ProductType.objects.get(code=type)
            except ProductType.DoesNotExist:
                raise InvalidProductType
        
        # use client default is quality/type not specified

        if not quality and client:
            quality = client.quality
            
        if not type and client:
            type = client.type
            
        # get a price 
        
        queryset = cls.objects.filter(quantity__gte = qty)
        
        if quality and quality>" ":
            queryset = queryset.filter(quality = quality)
            
        if type:
            queryset = queryset.filter(type__code = type)
        
        #q = str(queryset.query)


        if queryset.count()>0:
            # first in first out - return earliest entry 
            item = queryset.order_by('added')[0]
            
            if item.total_price(qty, client) < config_value('web','MIN_VALUE'):
                raise BelowMinValue
            else:
                return item
            
        else:
            if client:
                raise NoMatchInPoolClientException()
            else:
                raise NoMatchInPoolException()

    @classmethod
    def QTYCHECK(cls, value, client, quality=None, type=None, ):
        """
        returns the product id of the first product added to the pool that matches the requirements
        """
        
        # valid quantity
        
        if isinstance(value,Decimal):
            v = value
        else:
            v = Decimal(str(value))
            
        if v <  config_value('web','MIN_VALUE'):
            raise BelowMinValue


        # remove fee from value before further calculation

        if client:
            v = v - client.transaction_fee()
        else:
            v = v - config_value('web','DEFAULT_FEE')
        
      
        # convert type to ProductType if required
        if type and type>' ' and not isinstance(type, ProductType):
            try:
                type = ProductType.objects.get(code=type)
            except ProductType.DoesNotExist:
                raise InvalidProductType
        
        # use client default is quality/type not specified

        if not quality and client:
            quality = client.quality
            
        if not type and client:
            type = client.type
            
        # get a price 
        
        queryset = cls.objects.all()
        
        if quality and quality>" ":
            queryset = queryset.filter(quality = quality)
            
        if type:
            queryset = queryset.filter(type__code = type)
        
        #q = str(queryset.query)

        # take first item where there are enough units
        for item in queryset.order_by('added'):
            if (v /item.price) <= item.quantity:
                return item

        if client:
            raise NoMatchInPoolClientException()
        else:
            raise NoMatchInPoolException()
        
    @classmethod
    def LISTTYPES(self, blank_name=None):
        """
        return list of product types for available items in the pool
        eg. returns [(u'HYDR', u'Hydro'), (u'WIND', u'Wind')]
        blank is an optional label to use to create a blank first option
        eg. blank='Any', returns [(u'', u'Any'), (u'HYDR', u'Hydro'), (u'WIND', u'Wind')]
        """
        
        items = self.objects.filter(quantity__gte = config_value('web','MIN_QUANTITY')).values_list('type','type__name').distinct().order_by('type')

        # convert to list of tuples
        
        if blank_name:
            types=[('',blank_name),]
        else:
            types = []
        
        for (code, name) in items:
            types.append((code,name))
  
        return types

    @classmethod
    def LISTQUALITIES(self, blank_name=None):
        """
        return list of product types for available items in the pool
        eg. returns [('G', 'Gold'), ('P', 'Platinum')]
        blank is an optional label to use to create a blank first option
        eg. blank='Any', returns [(u'', u'Any'), ('G', 'Gold'), ('P', 'Platinum')]
        """
        
        items = self.objects.filter(quantity__gte = Decimal(config_value('web','MIN_QUANTITY'))).values_list('quality').distinct().order_by('quality')
        # flatten list

        items = [item for sublist in items for item in sublist]
        
        # build list from all possible qualities so you get description

        # convert to list of tuples
        
        if blank_name:
            qualities=[('',blank_name),]
        else:
            qualities = []

        for (code,name) in QUALITIES:
            if code in items:
                qualities.append((code,name))

        return qualities
            
        
    @classmethod
    def clean(cls):
        """
        remove all items in the pool with quantities less than the minimum quantity that
        can be sold.
        do not remove if there is a transaction referencing this pool item as that will 
        be a pending Transaction
        create an adjusting transaction to remove the remaining quantity so the books balance
        """
        
class TransItemMixin(object):

    def open(self):
        return self.filter(status='A')
 
        
class TransItemQuerySet(QuerySet, TransItemMixin):
    pass

class TransManager(models.Manager, TransItemMixin):
    def get_query_set(self):
        return TransItemQuerySet(self.model, using=self._db)
        
class Transaction(models.Model):
    """
    Purchase of a Product from the Pool by a Client (on behalf of a Customer)
    Note that the pool id will be set to null once the transaction status moves beyond Pending
    The Client purchases a Voucher for a certain number of units.  The Voucher ID they are given is the transaction id.
    A transaction is Open if the status is Pending, otherwise the transaction is Closed
    """
    
    uuid = UUIDField(auto=True)
    status = models.CharField(_('Status'),  max_length=1, choices=STATUS, default='A')
    pool = models.ForeignKey(Pool, null=True)
    product = models.ForeignKey(Product)
    client = models.ForeignKey(Client)    
    customer = models.ForeignKey(Customer, blank=True, null=True)
    price =  models.DecimalField(_('Price'), max_digits=9, decimal_places=2, default=0)
    fee =  models.DecimalField(_('Fee'), max_digits=9, decimal_places=2, default=0)
    currency = models.CharField(_('Default Currency'),  max_length=3, choices=CURRENCIES, default=config_value('web','DEFAULT_CURRENCY'))
    quantity =  models.DecimalField(_('Quantity'), max_digits=9, decimal_places=QTY_NUM_DP)
    created = models.DateTimeField(_('Created Date/Time'), auto_now_add=True, editable=False)
    closed = models.DateTimeField(_('Closed Date/Time'), null=True, blank=True)
    expire_at = models.DateTimeField(_('Expire ated Date/Time'), null=True)
    
    objects = TransManager()


    def __unicode__(self):
        return self.product.name

    class Meta:
        ordering = ['-id', ]

    def save(self, *args, **kwargs):
        
        # set expire_at datetime if blank
        if not self.id:
            self.expire_at = datetime.now() + timedelta(seconds=config_value('web','EXPIRE_TRANSACTIONS_AFTER_SECONDS'))
                    
        super(Transaction, self).save(*args, **kwargs)

    @property
    def total(self):
        return self.price + self.fee
        
    @property
    def is_open(self):
        return self.status=='A'
        
    @property
    def is_closed(self):
        return not self.status=='A'
        
    @property
    def total(self):
        return Decimal(str(round(self.price + self.fee, ndigits=2)))
        
    @property
    def payment(self):
        
        try:
            return Payment.objects.get(trans=self)
        except Payment.DoesNotExist:
            return None
   
    @classmethod
    def new(cls, client, quantity=None, value=None, quality=None, type=None):
        """
        create a new transaction of status Pending
        """
        
        if not quantity and not value:
            raise TransactionNeedsQtyorVal
        
        # check quantity is within allowed range
        
        if quantity:
            qty = Decimal(str(quantity))
            item = Pool.PRICECHECK(qty, quality=quality, type=type, client=client)
            v = item.price*qty
        if value:
            v = Decimal(str(value))
            item = Pool.QTYCHECK(v, quality=quality, type=type, client=client)
            
            qty = Decimal(str(round((v - client.transaction_fee() ) / item.price,QTY_NUM_DP)))
            
        # TODO in future need to do a lock between doing a price check and
        # creating a transaction
        
        
        t = Transaction.objects.create(
            client = client,
            pool = item,
            product = item.product,
            price = Decimal(str(round(item.price*qty,2))) ,
            fee = client.transaction_fee(),
            currency = item.currency,
            quantity = qty,
            )        
        
        # remove items from the Pool
        item.remove_quantity(qty)
        
        return t
        
    def can_pay(self, ref=None):
        ''' Check enough to pay
        '''
        return self.client.can_pay(self.total)
        
    def pay(self, ref=None):
        """
        create a payment entity and mark status of this transaction to paid
        """
        
        # check client has enough in account
        
        if self.client.can_pay(self.total):
            p = Payment.objects.create(
                trans=self, 
                client=self.client,
                ref=ref,
                status='S', 
                amount=self.total, 
                currency=self.currency)
                
            self.status = 'P'
            self.pool = None
            self.save()
                        
            self.payment_notification()
            
            return p
            
        else:
            raise NotEnoughFunds
            
    def payment_notification(self):
        """ Send email notification to client
            Don't send notifications if no user specified
        """
         
        if self.client.notification_user:
            try:
                notify = ClientNotification.objects.get(name='TransactionPaid')
            except ClientNotification.DoesNotExist:
                raise MissingPaymentNotification
                
            return notify.notify(self.client.notification_user.email, trans=self, client=self.client)

        
    @classmethod
    def expire_all(self):
        """
        expire all transactions past their expiry date
        """
        
        items = self.objects.filter(expire_at__lt = datetime.now())
        n = 0
        
        for item in items:
            if self.is_open:
                item.expire()
                n += 1
                
        return n
        
                
    def expire(self):
        """
        update status to expired and put quanity back in the pool
        """
        
        if self.is_closed:
            raise Unable2ExpireTransaction()
        else:
            self.status = 'X'
            self.pool = None
            self.save()

    def cancel(self):
        """
        update status to cancelled and put quanity back in the pool
        """
        
        if self.is_closed:
            raise Unable2CancelTransaction()
        else:
            self.status = 'C'
            self.pool = None
            self.save()
      
    '''
    NOT YET DEPLOYED - DO MANUALLY IN ADMIN
    def refund(self):
        """
        put this quanity of items back in the pool and refund
        """
        
        if self.is_open:
            raise Unable2RefundTransaction()
        else:
            self.cancel()
            #TODO: NOW UNDO PAYMENT
    '''
            

    @property
    def status_name(self):
        """return status name from status field"""
        for (code,name) in STATUS:
            if code == self.status:
                return name
    


class ClientNotification(Notification):
    
    class Meta:
        verbose_name = 'Client Notification'
         
    def notify(self, send_to, send_from=None, context=None, attach=None,  client=None, trans=None,):
        """
        send this notification to list of people supplied
        attach is a list of attachments in the form of mime content
        send_to can be a comma separated string or a list of emails
        """
        
        
        if not context:
            context = {}
            
        context.update({ 'trans' : trans,
            'client' : client,
            })

        t1 = Template(self.body)
        c = Context(context)
        body = t1.render(c)

        t2 = Template(self.subject)
        subject = t2.render(c)
        
        if type(send_to) == type(list()):
            send_to = ', '.join(send_to)
        
        if not send_from:
            send_from = self.from_email
            
        mlog = ClientMailLog.objects.create(subject = subject,
            body = body,
            from_email = send_from,
            notification = self,
            to_email = send_to,
            client = client,
            trans=trans)
                    
        mlog.save()     

        return mlog.send(attach=attach)
        
class ClientMailLog(MailLog):
    """
    Record emails sent 
    """

    trans = models.ForeignKey(Transaction, null=True)
    client = models.ForeignKey(Client)
    notification = models.ForeignKey(ClientNotification)

    class Meta:
        verbose_name = 'Client Mail Log'

    def delete(self, user=None):
        """
        don't delete
        """
        
        pass
        
class Payment(models.Model):
    """
    Attempted and successful payments of a transaction.
    Initially one payment to one complete transaction.
    """
    
    trans = models.ForeignKey(Transaction, blank=True, null=True)
    client = models.ForeignKey(Client)
    status = models.CharField(_('Status'),  max_length=1, choices=PAYMENT_STATUS, default='F')
    payment_type = models.CharField(_('Type'),  max_length=1, default='A')
    ref = models.CharField(_('Payment Ref'), max_length=20, blank=True, null=True)
    payment_date = models.DateTimeField(_('Payment Date/Time'), auto_now_add=True)
    amount =  models.DecimalField(_('Payment Amount'), max_digits=9, decimal_places=2, default=0)
    currency = models.CharField(_('Default Currency'),  max_length=3, choices=CURRENCIES, default=config_value('web','DEFAULT_CURRENCY'))
    payment_details = models.TextField(_("Payment details"), blank=True, null=True)
    
    def __unicode__(self):
        return self.id 

    class Meta:
        ordering = ['-id', ]

    def save(self, *args, **kwargs):
        
        #  All payment types except 'R'echarge are negative (ie. they reduce balance)
        # so make them negative
       
        if self.payment_type != 'R':
            self.amount = self.amount * Decimal('-1')
        
                    
        super(Payment, self).save(*args, **kwargs)

        # clients balance is updated in Payment.save()
        self.client.update_balance(self.amount)
        
    @property
    def is_paid(self):
        
        return (self.status=='S')
        
        

class UserProfile(models.Model):

    user = models.ForeignKey(User, unique=True)
    client = models.ForeignKey(Client, null=True, blank=True)
    
    def __str__(self):
        return "%s's profile" % self.user

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class PoolLevel(models.Model):
    """
    Monitor usage and minimum levels of quality/producttype items in the pool
    One record for each possible comibination of quality/producttype 
    
    Initially only used for the admin user to set the minimum level in the pool
    When the minimum level is reached an email is sent to admin.
    """
    
    quality = models.CharField(_('Default Quality'),  max_length=1, choices=QUALITIES, blank=True, null=True)
    type =  models.ForeignKey(ProductType, verbose_name = _('Default Product Type'), blank=True, null=True)
    minlevel =  models.DecimalField(_('Minimum Units'), max_digits=9, decimal_places=QTY_NUM_DP)
    
    
    def __unicode__(self):
        return "%s/%s" % (self.quality, self.type)

    class Meta:
        ordering = ['quality','type__name' ]


                
        
    @classmethod
    def check_level_ok(self, quality, type):
        """ 
        pass a quality/type and check if the total units of this
        quality/type are below minimum levels
        """

        # allow passing the product type code 
        if not isinstance(type, ProductType):
            try:
                type = ProductType.objects.get(code=type)
            except ProductType.DoesNotExist:
                raise InvalidProductType
        
            
        try:
            item = self.objects.get(quality=quality, type=type)
        except self.DoesNotExist:
            item = self.objects.create(quality=quality, type=type,
                minlevel = config_value('web','DEFAULT_MIN_POOL_LEVEL'))
            #TODO write to a log file here or send notification that new record created.
            
        level = Pool.level(quality=quality, type=type)
        
        if level < item.minlevel:
            #TODO send notification
            return False
        else:
            return True
                
        
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
