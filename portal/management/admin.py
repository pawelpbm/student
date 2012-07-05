# -*- coding: utf-8 -*-
from django.contrib import admin
from models import LdapGroup, LdapUser, TemporaryUser
from misc import generate_uid_number, calculate_account_expiration
from django.shortcuts import render_to_response
from django import template, forms
from django.contrib.admin import helpers
from mail import send_activation_mail
from widget import ExpireWidget
from django.contrib.admin.widgets import AdminDateWidget
from misc import expiration_days_to_date

class TemporaryUserAdmin(admin.ModelAdmin):
	""" Class for displaying TemporaryUser in admin panel"""
    list_display = ('username', 'name_and_surname')
    actions = ['activate']
    
    def name_and_surname(self, obj):
		"""Return name and surname"""
        return obj.name + ' ' + obj.surname
    
    name_and_surname.short_description = 'Imię i nazwisko'
    
    def activate(self, request, queryset):
		"""Create account for TemporaryUser in LDAP database and remove from SQLite database

		Arguments:
		request - HTTPRequest object
		queryset - queryset containing list of users that was marked on list
        
        """
        if 'apply_update' in request.POST:
			# apply_update is in request.POST when there was confirmation in question about activating users without confirmed email address
            modified_count = 0
            for obj in queryset:
                newUid = generate_uid_number()
                if obj.ssh_public_key:
                    LdapUser(cn = obj.name + " " + obj.surname,
                             gid_number = newUid,
                             home_directory = "/home/" + obj.username,
                             sn = obj.surname,
                             uid = obj.username,
                             uid_number = newUid,
                             ssh_public_key = [obj.ssh_public_key],
                             user_password = obj.password,
                             login_shell = "/bin/bash",
                             mail = obj.email,
                             shadow_expire = calculate_account_expiration(obj.studies_year)
                             ).save()
                else:
                    LdapUser(cn = obj.name + " " + obj.surname,
                             gid_number = newUid,
                             home_directory = "/home/" + obj.username,
                             sn = obj.surname,
                             uid = obj.username,
                             uid_number = newUid,
                             user_password = obj.password,
                             login_shell = "/bin/bash",
                             mail = obj.email,
                             shadow_expire = calculate_account_expiration(obj.studies_year)
                             ).save()
                     
                LdapGroup(cn = obj.username,
                          gid_number = newUid
                          ).save()
                send_activation_mail(obj)
                obj.delete()
                modified_count = modified_count + 1
            if modified_count == 1:
                self.message_user(request, "Aktywowano 1 użytkownika tymczasowego bez potwierdzonego adresu email.")
            else:
                self.message_user(request, "Aktywowano %s użytkowników tymczasowych bez potwierdzonego adresu email." % modified_count)
            return None

        # If there is no apply_update we can activate users with confirmed email and ask admin about activation users without confirmed email
        modified_count = 0
        queryset_without_confirmation = queryset.filter(confirmed=False)
        queryset_with_confirmation = queryset.filter(confirmed=True)
        
        for obj in queryset_with_confirmation:
            newUid = generate_uid_number()
            if obj.ssh_public_key:
                LdapUser(cn = obj.name + " " + obj.surname,
                         gid_number = newUid,
                         home_directory = "/home/" + obj.username,
                         sn = obj.surname,
                         uid = obj.username,
                         uid_number = newUid,
                         ssh_public_key = [obj.ssh_public_key],
                         user_password = obj.password,
                         login_shell = "/bin/bash",
                         mail = obj.email,
                         shadow_expire = calculate_account_expiration(obj.studies_year)
                         ).save()
            else:
                LdapUser(cn = obj.name + " " + obj.surname,
                         gid_number = newUid,
                         home_directory = "/home/" + obj.username,
                         sn = obj.surname,
                         uid = obj.username,
                         uid_number = newUid,
                         user_password = obj.password,
                         login_shell = "/bin/bash",
                         mail = obj.email,
                         shadow_expire = calculate_account_expiration(obj.studies_year)
                         ).save()
                     
            LdapGroup(cn = obj.username,
                      gid_number = newUid
                      ).save()
            send_activation_mail(obj)
            obj.delete()
            modified_count = modified_count + 1
        
        if modified_count == 0:
            pass
        elif modified_count == 1:
            self.message_user(request, "Aktywowano 1 użytkownika tymczasowego.")
        else:
            self.message_user(request, "Aktywowano %s użytkowników tymczasowych." % modified_count)

		# If there is at least one user without confirmed email we're creating form with list of that users
        if queryset_without_confirmation.count():    
            opts = self.model._meta
            app_label = opts.app_label
            context = {
                       "title": "Jesteś pewien?",
                       "deletable_objects": [obj.username for obj in queryset_without_confirmation],
                       'queryset': queryset_without_confirmation,
                       "app_label": app_label,
                       "opts": opts,
                       'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
                       }

            return render_to_response("activate_confirmation.html", context, context_instance=template.RequestContext(request))

	# Name of option in the action list
    activate.short_description = u'Aktywuj wybranych użykowników tymczasowych'

class LdapUserAdminForm(forms.ModelForm):
	"""Form for displaying LdapUser in admin panel"""
    class Meta:
		# We're changing widget of field shadow_expire to our ExpireWidget that handle displaying days from unix date in calendar form
        widgets = {
            'shadow_expire': ExpireWidget
            }

class LdapUserAdmin(admin.ModelAdmin):
	"""Class for displaying LdapUser in admin panel"""
    actions = ['delete_with_groups']
    
    exclude = ('ssh_public_key',)

    form = LdapUserAdminForm
    
    def delete_with_groups(self, request, queryset):
		"""Deleting user and users group from LDAP"""
        for obj in queryset:
            LdapGroup.objects.filter(gid_number=obj.uid_number).delete()
            obj.delete()
        
    delete_with_groups.short_description = u'Usuń wybranych użytkowników LDAP wraz z ich grupami'

admin.site.register(LdapGroup)
admin.site.register(LdapUser, LdapUserAdmin)
admin.site.register(TemporaryUser, TemporaryUserAdmin)
