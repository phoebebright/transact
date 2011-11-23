#python
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuidfield import UUIDField

#django
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import models
from django.db.models import Max, Q, Sum
from django.db.models.query import QuerySet
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail, EmailMessage
from django.utils.html import strip_tags

#app
import config
from livesettings import config_value
from web.exceptions import NoMatchInPoolException, BelowMinQuantity, AboveMaxQuantity

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
    """
    
    uuid = UUIDField(auto=True)
    name = models.CharField(_('Client Name'), max_length=50, unique=True)
    currency = models.CharField(_('Default Currency'),  max_length=3, choices=CURRENCIES, default='EUR')
    quality = models.CharField(_('Default Quality'),  max_length=1, choices=QUALITIES, blank=True, null=True)
    type =  models.ForeignKey(ProductType, verbose_name = _('Default Product Type'), blank=True, null=True)
    active = models.BooleanField(_('Active'), default=True)
    joined = models.DateTimeField(_('Created Date/Time'), auto_now_add=True)
    customers = models.ManyToManyField(Customer, through='Relationship')
    
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
                
     
    def transaction_fee(self):
        """
        in future fee can be varied by Client.
        for the moment return the default
        """
        
        return Decimal(config_value('web','DEFAULT_FEE'))
        
class Relationship(models.Model):
    """
    Links customers to client
    A customer by be the customer of many clients
    A customer can be a standalone customer, not linked to a client - although
      there is currently no functionality for a customer to purchase directly
    """
    customer = models.ForeignKey(Customer)
    client = models.ForeignKey(Client)
    

class Trade(models.Model):
    """
    Record purchase of Carbon Credits from an Exchange
    """
    
    name = models.CharField(_('Carbon Credit Name'), max_length=50)
    purchfrom = models.CharField(_('Purchased From'),  max_length=12)
    purchwhen = models.DateTimeField(_('Purchase Date/Time'), auto_now_add=True, editable=True)
    total = models.DecimalField(_('Total Paid'), max_digits=9, decimal_places=2,default =0)
    currency = models.CharField(_('Default Currency'),  max_length=3, choices=CURRENCIES, default='EUR')
    tonnes =  models.DecimalField(_('Tonnes'), max_digits=9, decimal_places=2)
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
    currency = models.CharField(_('Default Currency'),  max_length=3, choices=CURRENCIES, default=config_value('web','DEFAULT_CURRENCY'))
    quality = models.CharField(_('Default Quality'),  max_length=1, choices=QUALITIES, blank=True, null=True)
    type =  models.ForeignKey(ProductType, verbose_name = _('Default Product Type'), blank=True, null=True)
    price = models.DecimalField(_('Price'), max_digits=9, decimal_places=2,default =0)
    currency = models.CharField(_('Currency'),  max_length=3, choices=CURRENCIES, default='EUR')
    quantity_purchased =  models.DecimalField(_('Quantity Purchased'), max_digits=9, decimal_places=2)
    quantity2pool =  models.DecimalField(_('Quantity Moved to Pool'), max_digits=9, decimal_places=2, default=0)
    
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
        
        # add multiple records if required
        
        
        Pool.objects.create(product=self,
            quantity=self.quantity_purchased,
            quality=self.quality,
            type = self.type,
            price = self.price)

        # deduct from quantity2pool 
        self.quantity2pool = self.quantity_purchased
        self.save()
                 
        return True

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
    quantity =  models.DecimalField(_('Quantity Available'), max_digits=9, decimal_places=2)
    quality = models.CharField(_('Default Quality'),  max_length=1, choices=QUALITIES, blank=True, null=True)
    type =  models.ForeignKey(ProductType, verbose_name = _('Default Product Type'), blank=True, null=True)
    price = models.DecimalField(_('Price'), max_digits=9, decimal_places=2,default =0)
    currency = models.CharField(_('Default Currency'),  max_length=3, choices=CURRENCIES, default=config_value('web','DEFAULT_CURRENCY'))
    added = models.DateTimeField(_('Added to Pool Date/Time'), auto_now_add=True)
    
    
    def __unicode__(self):
        return self.product 

    class Meta:
        ordering = ['-id', ]

    def remove_quanity(self, units):
        """
        decrease quantity by units
        """
        return True        
        
    @classmethod
    def price_check(cls, quantity, quality=None, type=None):
        """
        returns the product id of the first product added to the pool that matches the requirements
        """
        
        qty = Decimal(str(quantity))
        
        if qty < config_value('web','MIN_QUANTITY'):
            raise BelowMinQuantity

        if qty > config_value('web','MAX_QUANTITY'):
            raise AboveMaxQuantity
            
        queryset = cls.objects.filter(quantity__gte = qty)
        
        if quality:
            queryset = queryset.filter(quality = quality)
            
        if type:
            queryset = queryset.filter(type__code = type)
            
        if queryset.count()>0:

            return queryset.order_by('added')[0]
        else:
            raise NoMatchInPoolException()
            
        
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
    price =  models.DecimalField(_('Price'), max_digits=9, decimal_places=2, default=0)
    fee =  models.DecimalField(_('Fee'), max_digits=9, decimal_places=2, default=0)
    currency = models.CharField(_('Default Currency'),  max_length=3, choices=CURRENCIES, default=config_value('web','DEFAULT_CURRENCY'))
    quantity =  models.DecimalField(_('Quantity'), max_digits=9, decimal_places=2)
    created = models.DateTimeField(_('Created Date/Time'), auto_now_add=True, editable=False)
    closed = models.DateTimeField(_('Closed Date/Time'), null=True)
    expire_at = models.DateTimeField(_('Expire ated Date/Time'), null=True)
    
    def __unicode__(self):
        return self.product 

    class Meta:
        ordering = ['-id', ]

    def save(self, *args, **kwargs):
        
        self.expire_at = datetime.now() + timedelta(seconds=config_value('web','EXPIRE_TRANSACTIONS_AFTER_SECONDS'))
                    
        super(Transaction, self).save(*args, **kwargs)

        
    @property
    def is_open(self):
        return self.status=='A'
        
    @property
    def is_closed(self):
        return not self.status=='A'
        
    @property
    def total(self):
        return self.price + self.fee
   
    @classmethod
    def new(self, client, quantity, quality=None, type=None):
        """
        create a new transaction of status Pending
        """
        
        qty = Decimal(str(quantity))
        
        # in future need to do a lock between doing a price check and
        # creating a transaction
        
        # first get the item to purchase
        item = Pool.price_check(qty, quality=quality, type=type)
        
        
        t = Transaction.objects.create(
            pool = item,
            product = item.product,
            price = (item.price*qty),
            fee = client.transaction_fee(),
            currency = item.currency,
            quantity = qty,
            )        
        
        return t
        
        
    def pay(self, ref=None):
        """
        create a payment entity and mark status of this transaction to paid
        """
        
        p = Payment.objects.create(
            trans=self, 
            ref=ref,
            status='S', 
            amount=self.total, 
            currency=self.currency)
            
        self.status = 'P'
        self.pool = None
        self.save()
        return p
        
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
        
        if self.is_open:
            raise Unable2CancelTransaction()
        else:
            self.status = 'C'
            self.pool = None
            self.save()
            
    def refund(self):
        """
        put this quanity of items back in the pool and refund
        """
        
        if self.is_open:
            raise Unable2RefundTransaction()
        else:
            self.cancel()
            #NOW UNDO PAYMENT
            
        
class Payment(models.Model):
    """
    Attempted and successful payments of a transaction.
    Initially one payment to one complete transaction.
    """
    
    trans = models.ForeignKey(Transaction)
    status = models.CharField(_('Status'),  max_length=1, choices=PAYMENT_STATUS, default='F')
    payment_type = models.CharField(_('Type'),  max_length=1, default='A')
    ref = models.CharField(_('Payment Ref'), max_length=20, blank=True, null=True)
    payment_date = models.DateTimeField(_('Payment Date/Time'), auto_now_add=True)
    amount =  models.DecimalField(_('Payment Amount'), max_digits=9, decimal_places=2, default=0)
    currency = models.CharField(_('Default Currency'),  max_length=3, choices=CURRENCIES, default=config_value('web','DEFAULT_CURRENCY'))
    
    def __unicode__(self):
        return self.id 

    class Meta:
        ordering = ['-id', ]

    @property
    def is_paid(self):
    
        return (self.status=='S')
        
        


class UserProfile(models.Model):

    user = models.ForeignKey(User, unique=True)
    client = models.ForeignKey(Client, null=True, blank=True)
    
    def __str__(self):
        return "%s's profile" % self.user

