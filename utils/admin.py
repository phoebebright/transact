from django.contrib import admin
from utils.models import *


class SayAdmin(admin.ModelAdmin):
    
    class Meta:
        model = Say
        
    list_display = ('phrase','usedin')
    readonly_fields = ('phrase','usedin')
    fields = ('phrase','en_gb_text','usedin')



class MailLogAdmin(admin.ModelAdmin):

    class Meta:
        model = MailLog

    list_display = ('subject','from_email', 'to_email', 'sent_date')
    list_filter =	('sent_date', )
    ordering = ('-sent_date',)

admin.site.register(Say, SayAdmin) 
admin.site.register(Notification)
admin.site.register(MailLog, MailLogAdmin)
