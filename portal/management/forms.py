# -*- coding: utf-8 -*-
from django import forms
from misc import strip_polish_letters, hash_password, user_exist, email_exist
import struct, base64

class AccountForm(forms.Form):
    """Form that is used in modify account view"""
    email = forms.EmailField(label='Adres email')
    ssh_public_key = forms.CharField(widget=forms.Textarea(attrs={'rows':'4'}), label='Klucz publiczny')

    def clean_ssh_public_key(self):
        """Checking of public key

        Function checks if there are three fields in public key: key_type, data and commment. After that we check if key_type is the same key_type that is encoded in data section.
        
        """
        ssh_public_key = self.cleaned_data.get('ssh_public_key')
        try:
            key_type, data, _ = ssh_public_key.split()
            data = base64.decodestring(data)
            int_len = 4
            str_len = struct.unpack('>I', data[:int_len])[0]
            if not data[int_len:int_len+str_len] == key_type:
                self._errors["ssh_public_key"] = self.error_class(["Nieprawidłowy klucz."])
        except:
            self._errors["ssh_public_key"] = self.error_class(["Nieprawidłowy klucz."])
                  
        return ssh_public_key


class LogInForm(forms.Form):
    username = forms.CharField(max_length=200, label='Login')
    password = forms.CharField(max_length=200, widget=forms.PasswordInput, label='Hasło')
    
class RegistrationForm(forms.Form):
    """User registration form"""
    years = ((1,1), (2, 2), (3,3), (4,4), (5,5),)
   
    username = forms.CharField(max_length=200, required=False, help_text=u'Jeśli nie podasz loginu zostanie on automatycznie wygenerowany. Będzie to pierwsza litera imienia i nazwisko.')
    name  = forms.CharField(max_length=200, label='Imię')
    surname = forms.CharField(max_length=200, label='Nazwisko')
    email = forms.EmailField(label='Adres email')
    password = forms.CharField(max_length=200, widget=forms.PasswordInput, label='Hasło')
    repeat_password =  forms.CharField(max_length=200, widget=forms.PasswordInput, label='Powtórz hasło')
    ssh_public_key = forms.CharField(widget=forms.Textarea(attrs={'rows':'4'}), label='Klucz publiczny')
    studies_year = forms.ChoiceField(choices=years, label='Rok studiów')
    rules = forms.BooleanField(label="Oświadczam, że:")
    
    def clean_repeat_password(self):
        """Checking if password and repeat_password are identical"""
        password = self.cleaned_data.get('password')
        repeat_password = self.cleaned_data.get('repeat_password')
        
        if not repeat_password:
            self._errors["repeat_password"] = self.error_class(["You must confirm your password"])
        if password != repeat_password:
            self._errors["repeat_password"] = self.error_class(["Your passwords do not match"])
        return hash_password(repeat_password)
    
    def clean_email(self):
        """Checking if there is no user with the same email address"""
        email = self.cleaned_data.get('email')
        
        if email_exist(email):
            errors = self._errors.setdefault(forms.forms.NON_FIELD_ERRORS, forms.util.ErrorList())
            errors.append("Użytkownik z takim adresem juz istnieje! Jeśli zapomniales danch skontaktuj się z administratorem.")       
        return email
    

    def clean_surname(self):
        """Checking if there is no user with the same login"""
        
        name = self.cleaned_data.get('name')
        surname = self.cleaned_data.get('surname')
        username = name[0] + surname
        
        if user_exist(strip_polish_letters(username)):
            self._errors["username"] = self.error_class([u"Taki użytkownik już istnieje. Wybierz inny login"])

        return surname
    
    def clean_username(self):
        """Checking if there is no user with the same login in case wthe user provide username"""
        username = self.cleaned_data.get('username')
        
        if user_exist(username):
            self._errors["username"] = self.error_class(["Taki user już istnieje. Wybierz inny login"])

        return strip_polish_letters(username)
                
    def clean_ssh_public_key(self):
        """Checking of public key

        Function checks if there are three fields in public key: key_type, data and commment. After that we check if key_type is the same key_type that is encoded in data section.
        
        """
        ssh_public_key = self.cleaned_data.get('ssh_public_key')
        try:
            key_type, data, _ = ssh_public_key.split()
            data = base64.decodestring(data)
            int_len = 4
            str_len = struct.unpack('>I', data[:int_len])[0]
            if not data[int_len:int_len+str_len] == key_type:
                self._errors["ssh_public_key"] = self.error_class(["Nieprawidłowy klucz."])
        except:
            self._errors["ssh_public_key"] = self.error_class(["Nieprawidłowy klucz."])
                  
        return ssh_public_key
    
class RepoForm(forms.Form):
    """Form for adding GIT permmissions"""
    perms = (('---', '---'), ('rw','zapis'), ('ro', 'odczyt'),)
    username = forms.CharField(max_length=200, label='Nazwa użytkownika')
    reponame  = forms.ChoiceField(choices='', label='Repozytorium')
    permissions = forms.ChoiceField(choices=perms, label='Uprawnienia')
    
    
    def __init__(self, *args, **kwargs):
        """Initializing list of user repositories in dropdown box

        List of users repos is argument to constructor of RepoForm class (named parameter repos). We are removing it from list of named parameters, calling parent class constructor and initializing list.
        """
        repos = kwargs.pop('repos', tuple(""))
        super(RepoForm, self).__init__(*args, **kwargs)
        self.fields['reponame'].choices = repos

    def clean_permissions(self):
        """Checking if user choosed permission from dropdown list"""
        permission = self.cleaned_data.get('permissions')
        
        if permission == '---':
            self._errors["permissions"] = self.error_class(["Musisz wybrać uprawnienia."])
            
        return permission
    
class UserGroupForm(forms.Form):
    """Form for adding new user group"""
    groupname = forms.CharField(max_length=200, label='Nazwa użytkownika')

    def check_name(self):
        """Checking if user choosed permission from dropdown list"""
        permission = self.cleaned_data.get('permissions')
        
        if permission == '---':
            self._errors["permissions"] = self.error_class(["Musisz wybrać uprawnienia."])
            
        return permission

