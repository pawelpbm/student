# -*- coding: utf-8 -*-
from django.db import models
from ldapdb.models.fields import CharField as LDAPCharField
from ldapdb.models.fields import IntegerField as LDAPIntegerField
from ldapdb.models.fields import ListField as LDAPListField
import ldapdb.models
from student.settings import LDAP_SUFFIX 
    
class TemporaryUser(models.Model):
    """Class for TemporaryUser stored in SQLite."""

    class Meta:
        verbose_name = "Użytkownik tymczasowy"
        verbose_name_plural = "Użytkownicy tymczasowi"
    
    username = models.CharField(max_length=200, verbose_name='Login')  
    name  = models.CharField(max_length=200, verbose_name='Imię')
    surname = models.CharField(max_length=200, verbose_name='Nazwisko')
    email = models.EmailField()
    password = models.CharField(max_length=200, verbose_name='Hasło')
    ssh_public_key = models.CharField(max_length=1000, blank=True, verbose_name='Klucz publiczny')
    studies_year = models.IntegerField(verbose_name='Rok studiów')
    confirmed = models.BooleanField(verbose_name='Potwierdzony')
    confirmation_link = models.CharField(max_length=200, verbose_name='Link potwierdzający')
    
    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.username

def repo_entry(username):
	"""Function that returns class RepoEntry_username for specified username

	Class is generated dynamically, because of variable base_dn that must be properly set befeore __init__() in case of calling class methods.
    """
    object_classes = ['top', 'repository']
    
    base_dn = "ou=git,uid=" + username + ",ou=users," + LDAP_SUFFIX
    
    repo = LDAPCharField(db_column='repo', max_length=200, primary_key=True)
    userRW = LDAPListField(db_column='userRW')
    userRO = LDAPListField(db_column='userRO')
    
    to_str=lambda self: self.repo
    
    attrs = {}
    class Meta:
        app_label = "label"
        managed = False
        verbose_name = 'RepoEntry'
        verbose_name_plural = 'RepoEntry'
    attrs['__module__'] = 'management.models'
    attrs['Meta'] = Meta
    attrs['base_dn'] = base_dn
    attrs['object_classes'] = object_classes
    attrs['__str__'] = to_str 
    attrs['__unicode'] = to_str
    attrs['userRO'] = userRO
    attrs['userRW'] = userRW
    attrs['repo'] = repo
    return type('RepoEntry_' + username.encode('ascii','ignore'), (ldapdb.models.Model,), attrs)


def git_entry(username): 
	"""Function that returns class GitEntry_username for specified username

	Class is generated dynamically, because of variable base_dn that must be properly set befeore __init__() in case of calling class methods.
    """
    base_dn = "uid=" + username +",ou=users,"+ LDAP_SUFFIX
    object_classes = ['top', 'organizationalUnit']
    
    ou = LDAPCharField(db_column='ou', max_length=200, primary_key=True)
        
        

    class Meta:
        app_label = "label"
        managed = False
        verbose_name = 'GitEntry '
        verbose_name_plural = 'GitEntry'
    attrs = {}
    attrs['__module__'] = 'management.models'
    attrs['Meta'] = Meta
    attrs['base_dn'] = base_dn
    attrs['username'] = username
    attrs['object_classes'] = object_classes
    attrs['ou'] = ou
    
    return type('GitEntry_' + username.encode('ascii','ignore'), (ldapdb.models.Model,), attrs)

class LdapUser(ldapdb.models.Model):
    """Class for storing user in LDAP DB"""
    
    class Meta:
        verbose_name = "Użytkownik LDAP"
        verbose_name_plural = "Użytkownicy LDAP"
    
    base_dn = "ou=users," + LDAP_SUFFIX
    object_classes = ['top', 'posixAccount', 'person', 'organizationalPerson', 'inetOrgPerson', 'ldapPublicKey', 'shadowAccount']

    cn = LDAPCharField(db_column='cn', max_length=200, verbose_name='Imię i nazwisko')
    gid_number = LDAPIntegerField(db_column='gidNumber', unique=True, verbose_name="GID")
    home_directory = LDAPCharField(db_column='homeDirectory', verbose_name='Katalog domowy')
    sn = LDAPCharField(db_column='sn', verbose_name='Nazwisko')
    uid = LDAPCharField(db_column='uid', max_length=200, primary_key=True, verbose_name='Login')
    uid_number = LDAPIntegerField(db_column='uidNumber', unique=True, verbose_name='UID')
    mail = LDAPCharField(db_column='mail', verbose_name='Mail')
    ssh_public_key = LDAPListField(db_column='sshPublicKey', verbose_name='Klucz publiczny')
    login_shell = LDAPCharField(db_column='loginShell', verbose_name='Shell')
    user_password = LDAPCharField(db_column='userPassword', verbose_name='Hasło')
    shadow_expire = LDAPIntegerField(db_column='shadowExpire', verbose_name='Wygaśnięcie konta')

    def __str__(self):
        return self.uid

    def __unicode__(self):
        return self.uid
        
class LdapGroup(ldapdb.models.Model):
    """Class for storing group in LDAP DB"""
    
    class Meta:
        verbose_name = "Grupa LDAP"
        verbose_name_plural = "Grupy LDAP"
    
    base_dn = "ou=groups," + LDAP_SUFFIX
    object_classes = ['posixGroup', 'top']

    gid_number = LDAPIntegerField(db_column='gidNumber', unique=True, verbose_name='GID')
    cn = LDAPCharField(db_column='cn', max_length=200, primary_key=True, verbose_name='Nazwa')

    def __str__(self):
        return self.cn

    def __unicode__(self):
        return self.cn
