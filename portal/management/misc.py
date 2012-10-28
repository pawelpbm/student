# -*- coding: utf-8 -*-
from models import LdapUser
import random
from student.settings import INITIAL_UID

def generate_confirmation_link():
    """Function for generating random string that is used in urls for confirmation link"""
    return random.getrandbits(128)

def strip_polish_letters(string):
    """Stripping polish letters in usernames"""
    import re
    r = {u"ę":'e',u"ó":'o',u"ą":'a',u"ś":'s',u"ł":'l',u"ż":'z',u"ź":'z',u"ć":'c',u"ń":'n', 
         u"Ę":'E',u"Ó":'O',u"Ą":'A',u"Ś":'S',u"Ł":'l',u"Ż":'Z',u"Ź":'Z',u"Ć":'C',u"Ń":'N'}
    for i, a in enumerate(string):
        if a in r:
            string = string[:i] + r[a] + string[i+1:]

    pattern = re.compile('[\W_]+')
    string = pattern.sub('', string) 
    return string

def generate_uid_number():
    """Generating UID numers

    We're checking for maximum UID numer in LDAP database and incrementing it
    """
    try:
        uid = LdapUser.objects.order_by('-uid_number')[0].uid_number + 1
    except IndexError:
        # If there is no users in LDAP we're using INITIAL_UID constant defined in settings.py
        uid = INITIAL_UID
    return uid

def get_salt():
    """Preparing salt for SSHA password"""
    import string
    
    salt = ""
    for _ in range(16):
        salt += random.choice(string.letters + string.digits)
    return salt

def hash_password(password):
    """Hashing password befere writing them

    Password are hashed as in LDAP DB and stored as it in SQLITE DB before moving user to LDAP DB
    """
    import base64
    import sha
    
    salt = get_salt()
    return "{SSHA}" + base64.encodestring(sha.new(str(password) + salt).digest() + salt)[:-1]
    
def user_exist(username):
    """Checking if there is user or temp user with username"""
    from models import TemporaryUser
    from django.core.exceptions import ObjectDoesNotExist
    
    user_temp = []
    user_ldap = []

    try:
        user_temp = TemporaryUser.objects.get(username=username)
    except ObjectDoesNotExist:
        pass
        
    try:
        user_ldap = LdapUser.objects.get(uid=username)
    except ObjectDoesNotExist:
        pass
            
    if user_ldap or user_temp:
        return True
    return False

def email_exist(email):
    """Checking if there is user or temp user with email addres"""
    from models import TemporaryUser
    from django.core.exceptions import ObjectDoesNotExist
    
    user_temp = []
    user_ldap = []

    try:
        user_temp = TemporaryUser.objects.get(email=email)
    except ObjectDoesNotExist:
        pass
        
    try:
        user_ldap = LdapUser.objects.get(mail=email)
    except ObjectDoesNotExist:
        pass
            
    if user_ldap or user_temp:
        return True
    return False

def calculate_account_expiration(year):
    """Calculating accounte expiration

    Basing on study year from registration form we're creating timestamp in form of number of days from using date to October 1st of year of finishing studies.
    """
    import datetime
    today = datetime.date.today()  
    minus = 5 if today.month < 9 else 6
    left =  minus - year  
    year_of_finish = today.year + left
    expiration_date = datetime.date(year_of_finish, 10, 1)
    expiration = expiration_date - datetime.date(1970, 1, 1)
    return expiration.days

def expiration_days_to_date(days):
    """Function that is used in WidgetExpire"""
    import datetime
    return datetime.date(1970, 1, 1) + datetime.timedelta(days)

def date_to_expiration_days(date):
    """Function that is used in WidgetExpire"""
    import datetime
    expiration = datetime.datetime.strptime(date, '%d.%m.%Y') - datetime.datetime(1970, 1, 1, 0, 0, 0)
    return expiration.days

def find_primary_key(user):
    """Finding primary public key for specified user"""
    keys = user.ssh_public_key
    for key in keys:
        if key.startswith(('ssh-dss','ssh-rsa',)):
            return key
    return None

def list_user_repos(username):
    """Function that list subdirectories in ~/git/ as user repos"""
    import os
    user = LdapUser.objects.get(uid=username)
    home_dir =  user.home_directory + "/git/"
    if not os.path.isdir(home_dir):
        return False
    directories = [ name for name in os.listdir(home_dir) if os.path.isdir(os.path.join(home_dir, name)) and name[0] is not "." ]
    return zip(directories, directories)
