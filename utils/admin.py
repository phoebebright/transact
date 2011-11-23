from django.contrib import admin


class SayAdmin(admin.ModelAdmin):
    
    class Meta:
        model = Say
        
    list_display = ('phrase','usedin')
    readonly_fields = ('phrase','usedin')
    fields = ('phrase','en_gb_text','usedin')
   


admin.site.register(Trade, TradeAdmin)    
admin.site.register(Client, ClientAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Pool, PoolAdmin)
admin.site.register(Say, SayAdmin)
