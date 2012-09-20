from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from django.contrib.admin.models import User
from django.core.mail import send_mail
from django.template import Context, loader, Template
from django.core.mail import EmailMultiAlternatives
from optparse import make_option


class Command(BaseCommand):
    help = """Send a newsletter to all users in an email template"""
    args = """template: template name for html mail and plain text alternative. Takes argument without extension."""
    
    option_list = BaseCommand.option_list + (
           
            make_option('-r', '--for-real', 
                action='store_true', 
                dest='action',
                default=False, 
                help='Do the action.'),
                
            make_option('-t', '--template', 
                action='store', 
                dest='template',
                default='', 
                help='Enter template name (without the extension)'),
                
            make_option('-s', '--subject', 
                action='store', 
                dest='subject',
                default='', 
                help='Enter the email subject line'),
                
            make_option('-e', '--email', 
                action='store', 
                dest='email',
                default='', 
                help='Enter an email address for testing purposes'),
                 
            )
            
    def handle(self, *args, **options):
        action = options.get('action', False)
        template = options.get('template', '')
        subject = options.get('subject', '')
        email = options.get('email', '')
        if not action: 
            print "add option -r (or --for-real) to execute."
        if not template:
            print "Please add  template argument. (-t, --template)"
            return None
        if not subject:
            print "Please add subject argument. (-s, --subject)"
            return None
        print 'with emailtemplate %s' % template
        t = loader.get_template('emailtemplates/%s.html' % template)
        alt = loader.get_template('emailtemplates/%s.txt' % template)
        if not email:
            users = User.objects.all()
            for user in users:
                if user.is_active:
                    if user.email:
                        print '%s %s %s' % (user.first_name, user.last_name, user.email)
                        c = Context({'name': user.first_name})
                        subject, from_email, to = subject, 'beeldnet@schepper.nl', user.email
                        text_content = alt.render(c)
                        html_content = t.render(c)
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        if action:
                            try:
                                msg.send()
                                print 'Successfully sent email to %s.' % user.email
                            except Exception, inst:
                                print 'An error occurred %s' % inst
        else:
            print 'Send test email to %s.' % email
            c = Context({'name': 'Admin'})
            subject, from_email, to = subject, 'beeldnet@schepper.nl', email
            text_content = alt.render(c)
            html_content = t.render(c)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            if action:
                try:
                    msg.send()
                    print 'Successfully sent email to %s.' % email
                except Exception, inst:
                    print 'An error occurred %s' % inst
            
    
    