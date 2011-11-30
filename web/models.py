#python
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuidfield import UUIDField
from collections import defaultdict

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
from web.exceptions import *

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
    quantity =  models.DecimalField(_('Quantity Available'), max_digits=9, decimal_places=2)
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

    @classmethod
    def LISTPRODUCTS(self):
        """
        List of currently available products
        """
        
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
            return queryset.order_by('added')[0]
        else:
            if client:
                raise NoMatchInPoolClientException()
            else:
                raise NoMatchInPoolException()

    @classmethod
    def QTYCHECK(cls, value, quality=None, type=None, client=None):
        """
        returns the product id of the first product added to the pool that matches the requirements
        """
        
        # valid quantity
        
        if isinstance(value,Decimal):
            v=value
        else:
            v = Decimal(str(value))

            
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
            if item.price * item.quantity > v:
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
    quantity =  models.DecimalField(_('Quantity'), max_digits=9, decimal_places=2)
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
        return self.price + self.fee
        
    @property
    def payment(self):
        
        try:
            return Payment.objects.get(trans=self)
        except Payment.DoesNotExist:
            return None
   
    @classmethod
    def new(self, client, quantity=None, value=None, quality=None, type=None):
        """
        create a new transaction of status Pending
        """
        
        if not quantity and not value:
            raise TransactionNeedsQtyorVal
        
        if quantity:
            qty = Decimal(str(quantity))
            item = Pool.PRICECHECK(qty, quality=quality, type=type)
            v = item.price*qty
        if value:
            v = Decimal(str(value))
            item = Pool.QTYCHECK(v, quality=quality, type=type)
            
            qty = Decimal(str(round((v - client.transaction_fee() ) / item.price,2)))
            
        # TODO in future need to do a lock between doing a price check and
        # creating a transaction
        
        
        t = Transaction.objects.create(
            client = client,
            pool = item,
            product = item.product,
            price = Decimal(item.price*qty),
            fee = client.transaction_fee(),
            currency = item.currency,
            quantity = qty,
            )        
        
        # remove items from the Pool
        item.remove_quantity(qty)
        
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
        return self.payment_date 

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


class PoolLevel(models.Model):
    """
    Monitor usage and minimum levels of quality/producttype items in the pool
    One record for each possible comibination of quality/producttype 
    
    Initially only used for the admin user to set the minimum level in the pool
    When the minimum level is reached an email is sent to admin.
    """
    
    quality = models.CharField(_('Default Quality'),  max_length=1, choices=QUALITIES, blank=True, null=True)
    type =  models.ForeignKey(ProductType, verbose_name = _('Default Product Type'), blank=True, null=True)
    minlevel =  models.DecimalField(_('Minimum Units'), max_digits=9, decimal_places=2)
    
    
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