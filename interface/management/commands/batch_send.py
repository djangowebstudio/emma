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
            )
            
    def handle(self, template='', subject='', *args, **options):
        action = options.get('action', False)
        if not action: 
            print "add option -r (or --for-real) to execute."
        if not template:
            print "Please add template as first argument."
            return None
        if not subject:
            print "Please add subject as second argument."
            return None
        print 'with emailtemplate %s' % template
        t = loader.get_template('emailtemplates/%s.html' % template)
        alt = loader.get_template('emailtemplates/%s.txt' % template)
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
                        except Exception, inst:
                            print 'An error occurred %s' % inst
    
    