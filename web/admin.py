
from web.models import *

from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import router
from django.http import HttpResponse,HttpResponseRedirect

class UserProfileInline(admin.StackedInline):
 model = UserProfile
 max_num = 1
 can_delete = False

UserAdmin.list_display = ('email', 'username', 'first_name', 'last_name', 'is_active', 'date_joined', 'last_login', 'is_staff')
UserAdmin.inlines = [UserProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class TradeAdmin(admin.ModelAdmin):

    class Meta:
        model = Trade 
        
        
    list_display = ('purchwhen','total','currency','tonnes','name','ref')
   
    search_fields =	 ('name','purchfrom','ref')
    ordering = ('-purchwhen',)


class ClientAdmin(admin.ModelAdmin):
    inlines = [UserProfileInline]
    
    class Meta:
        model = Client 
        
        
    list_display = ('name','active')   
    search_fields =	 ('name','uuid')
    ordering = ('-name',)

'''
Not Implemented
class AuthAdmin(admin.ModelAdmin):

    class Meta:
        model = Trade 
        
        
    list_display = ('alias','uuid','user','expire_at')
   
    search_fields =	 ('alias','uuid','user.username')
'''

class ProductTypeAdmin(admin.ModelAdmin):

    class Meta:
        model = ProductType 
        
        
    list_display = ('code','name')   
    ordering = ('code',)


class ProductAdmin(admin.ModelAdmin):

    class Meta:
        model = Product 
        
        
    list_display = ('name','trade', 'quality', 'type','price','currency','quantity_purchased', 'quantity2pool')
    filter_fields = ('quality', 'type','price','currency','quantity')   
    search_fields =	 ('name',)
    ordering = ('-name',)


    def move2pool(self, request, queryset):
    
        for item in queryset:
            item.move2pool(request.user)
    
    move2pool.short_description = "Move products to Pool"

    actions = [move2pool,]


class PoolAdmin(admin.ModelAdmin):

    class Meta:
        model = Pool 
        
        
    list_display = ('product','quality', 'type','quantity','price')   

       
class TransactionAdmin(admin.ModelAdmin):

    class Meta:
        model = Transaction 
        
        
    list_display = ('uuid','client','status', 'pool', 'product','price','currency','fee', 'quantity')


admin.site.register(Trade, TradeAdmin)    
admin.site.register(Client, ClientAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Pool, PoolAdmin)
admin.site.register(Transaction, TransactionAdmin)
#admin.site.register(Auth, AuthAdmin)
admin.site.register(PoolLevel)
#admin.site.register(UserProfile)