#python

#django
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail, EmailMessage
from django.utils.html import strip_tags


class Say(models.Model):
    phrase = models.CharField(max_length=75, primary_key=True)
    en_gb_text = models.TextField(_('Content'), blank=True)
    status = models.CharField(max_length=15, blank=True)
    userlevel = models.IntegerField()
    usedin = models.TextField(_('Screen(s) where Used'),blank=True, null=True)

    def __unicode__(self):
        return self.phrase

    
    class Meta:
        verbose_name = "Screen Message"
        
    @classmethod
    def say(cls, phrase, page=None):
        """
        return block of text linked to phrase
        """
        
        try:
            content = cls.objects.get(phrase=phrase)
            text = content.output()
            
        except cls.DoesNotExist:
             text = re.sub('((?=[A-Z][a-z])|(?<=[a-z])(?=[A-Z]))', ' ', phrase).strip()
             content = cls.objects.create(phrase=phrase, en_gb_text = text, status='auto', usedin=page, userlevel=0)
        
        #  track where phrases are used if in debug mode
        if settings.DEBUG and page:
            if not page in content.usedin:
                content.usedin += "," + page
                content.save()
    
        return text
    
        
    def output(self, language=None):
        return self.en_gb_text

class MailLog(models.Model):
    """
    Record emails sent 
    To send an email, add a new item to MailLog and then call send on the object
    """

    subject = models.CharField(_('Subject'), max_length=120)
    body = models.TextField(_('Body'), null=True)
    from_email = models.CharField(_('From Email'), max_length=100)
    to_email = models.TextField(_('To Email'), )
    sent_date = models.DateTimeField(_('Sent Date/Time'), null=True, editable=False)
    priority = models.BooleanField(_('Priority'), default=False)
    created = models.DateTimeField(_('Created Date/Time'), auto_now_add=True, editable=False)
    created_by = models.ForeignKey(User, blank=True, null=True)
    mailed = models.ManyToManyField(User, verbose_name=_('Mailed to Users'),related_name="mailed")


    def save(self, *args, **kwargs): 
        self.subject = self.subject[:119]
        super(MailLog, self).save(*args, **kwargs)

        
    def __unicode__(self):
        return self.subject

    class Meta:
        ordering = ['-id',]

    def send(self, priority=False, individual=True, attach=None):
        """
        send or resend an item in the MailLog
        have to use EmailMessage and send as setting the priority not availabe in send_mail
        If individual is true the a separate email is sent for each person in the to_email list
        """     
        
        # save options used
        self.priority=priority
        self.individual = individual
        self.save()

        sendto = self.to_email.split(',')

        # sendto can be blank because no email added to log or because a group with
        # no emails attached was used.  
        # return False but don't raise error here

        if len(sendto) == 1 and len(sendto[0])==0:
            return False

        
        if  settings.EMAIL_DEBUG:
            self.to_email = settings.TEST_EMAIL
                    
        
        if individual:
            try:
               for  toemail in sendto:
               
                    if priority:
                        msg = EmailMessage(self.subject, self.body, self.from_email, [toemail,], 
        headers={'X-Priority': 1})
                    else:
                         msg = EmailMessage(self.subject, self.body, self.from_email, [toemail,])

            except:
                 return False

        else:
            try:
                if priority:
                    msg = EmailMessage(self.subject, self.body, self.from_email, sendto, 
    headers={'X-Priority': 1})
                else:
                     msg = EmailMessage(self.subject, self.body, self.from_email, sendto)

                
            except:
                return False



        if attach:
            msg.attach(attach)
            
        msg.send()
                            
        self.sent_date = datetime.now()
        self.save()
        
        return True               


class Notification(models.Model):
    """
    holds formats for email notifications
    """
    name = models.CharField(max_length=30, unique=True)
    app = models.CharField(max_length=20)
    subject = models.CharField(max_length=120)
    body = models.TextField(null=True)
    from_email = models.EmailField(null=True, blank=True)
    priority = models.BooleanField(_('Send as Priority Email'), default=False)

    def __unicode__(self):
        return  self.name
        
    class Meta:
        ordering = ['name',]

    def notify(self, send_to, context=None, attach=None, priority=None):
        """
        send this notification to list of people supplied
        attach is a list of attachments in the form of mime content
        send_to can be a comma separated string or a list of emails
        """
        
        if context:
            t1 = Template(self.body)
            c = Context(context)
            body = t1.render(c)

            t2 = Template(self.subject)
            subject = t2.render(c)
            
            
        else:
            body = self.body
            subject = self.subject
        
        if type(send_to) == type(list()):
            # dedupelicate list and join with commas
            send_to = ', '.join(list(set(send_to)))
            
        # default to priority in notification object but override by setting parameter to this function
        if priority == None:
            priority = self.priority

        mlog = MailLog.objects.create(subject = subject,
            body = body,
            from_email = self.from_email,
            notification = self,
            to_email = send_to,
            priority = priority,
            )
                    
        mlog.save()     

        return mlog.send(attach=attach)
        
