# -*- coding: utf-8 -*-
import threading
from django.core.mail import EmailMultiAlternatives

class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, text_content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.text_content = text_content
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMultiAlternatives(self.subject, self.text_content, 'student.icis.pcz.pl', self.recipient_list)
        msg.attach_alternative(self.html_content, "text/html")
        msg.send()
       

def send_html_mail(subject, html_content, text_content, recipient_list):
    """Function for creating and starting new thread for sending emails"""
    EmailThread(subject, html_content, text_content, recipient_list).start()

def send_confirmation_mail(user):
    """Prepare strings for confirmation email"""
    text_content = u'''Witaj, %s
    
    Aby potwierdzić swoją rejestrację na serwerze student.icis.pcz.pl odwiedź poniższą stronę:
    http://student.icis.pcz.pl/confirm/%s
    
    ''' % (user.name, user.confirmation_link)
    html_content = u'''Witaj, %s<br /><br /> Aby potwierdzić swoją rejestrację na serwerze student.icis.pcz.pl odwiedź poniższą stronę <a href="http://student.icis.pcz.pl/confirm/%s">http://student.icis.pcz.pl/confirm/%s</a>
    '''% (user.name, user.confirmation_link, user.confirmation_link)
    # We're calling function send_html_email with  prepared strings as arguments
    send_html_mail("student.icis.pcz.pl - potwierdzenie adresu email", html_content, text_content, [user.email])
    
def send_activation_mail(user):
    """Prepare strings for activation email"""
    text_content = u'''Witaj, %s
    
    Twoje konto na serwerze student.icis.pcz.pl zostało aktywowane.
    
    ''' % user.name
    
    html_content = u'''Witaj, %s<br /><br /> Twoje konto na serwerze student.icis.pcz.pl zostało aktywowane.
    '''% user.name
    # We're calling function send_html_email with  prepared strings as arguments
    send_html_mail("student.icis.pcz.pl - aktywacja konta", html_content, text_content, [user.email])
