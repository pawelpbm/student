# -*- coding: utf-8 -*-
import ldap
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from models import TemporaryUser, LdapUser, LdapUserGroup
from django.shortcuts import render_to_response, redirect
from forms import LogInForm, RegistrationForm, RepoForm, AccountForm, UserGroupForm
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from misc import strip_polish_letters, find_primary_key
from mail import send_confirmation_mail
from misc import generate_confirmation_link
from misc import hash_password
from student.management.misc import list_user_repos
from models import git_entry, repo_entry
import urllib
import os.path

from django.core.urlresolvers import reverse

def home(request):
    """View for displaying main page with login form"""
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    request.session['username'] = username
                    return HttpResponseRedirect('/')
                else:
                    return render_to_response('invitation.html',  {'form': form, 'error': u'Użytkownik nieaktywny.'}, context_instance=RequestContext(request))
            else:
                return render_to_response('invitation.html',  {'form': form, 'error': u'Nieprawidłowy login lub hasło.'}, context_instance=RequestContext(request))
    else:
        form = LogInForm()

    return render_to_response('invitation.html',  {'form': form,}, context_instance=RequestContext(request))

def logout_view(request):
    """View for loggin out users"""
    logout(request)
    return HttpResponseRedirect('/')

@login_required
def account(request):
    """View for displaying and modyfing acount information"""
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            ssh_public_key = form.cleaned_data['ssh_public_key']
            
            username = request.user.username
            user = LdapUser.objects.get(uid=username)
            
            user.mail = email

            keys = user.ssh_public_key
            keys_new = []
            for key in keys:
                if key.startswith(('ssh-dss','ssh-rsa',)):
                    keys_new.append(ssh_public_key)
                else:
                    keys_new.append(key)
                    
            user.ssh_public_key = keys_new
            user.save()

            return render_to_response('account.html', {'form': form, 'changed': 1}, context_instance=RequestContext(request))
          
    else:
        username = request.user.username
        user = LdapUser.objects.get(uid=username)
        form = AccountForm(initial={'email': user.mail, 'ssh_public_key': find_primary_key(user)})
        
    return render_to_response('account.html',  {'form': form,}, context_instance=RequestContext(request))



@login_required
def delete(request, reponame, username, permissions):
    """View for removing permission for repositories"""
    ownername = request.user.ldap_user._username
    Repos = repo_entry(ownername)
    try:
        if permissions == 'ro':
            entry = Repos.objects.get(repo=reponame, userRO__contains=username)
            entry.userRO.remove(username)
            entry.save()
        elif permissions == 'rw':
            entry = Repos.objects.get(repo=reponame, userRW__contains=username)
            entry.userRW.remove(username)
            entry.save()
    except ObjectDoesNotExist:
        return HttpResponse("Brak obiektu do usunięcia.")
    
    return git_repos(request, repository_modification={'username': username, 'reponame': reponame, 'permission': 'zapis' if permissions == 'rw' else 'odczyt', 'modification': 'del'})
    

@login_required
def usergroups(request, usergroup_modification=None, err=None):
    """View displaying list of repositories"""
    username = request.user.ldap_user._username
    groupsOwner = LdapUserGroup.objects.filter(owner=username)
    groupsMember = []
    for ug in LdapUserGroup.objects.all():
        if username in ug.members:
            groupsMember.append(ug)
    return render_to_response('groups.html',  {'err': err, 'groupsOwner': groupsOwner, 'groupsMember': groupsMember, 'usergroup_modification': usergroup_modification}, context_instance=RequestContext(request))

@login_required
def usergroup_add(request):
    """View for adding new user group"""

    if request.method == 'POST':
        form = UserGroupForm(request.POST)
        if form.is_valid():    
            username = request.user.username
            groupname = form.cleaned_data['groupname']

            group = LdapUserGroup(name=groupname, owner=username, members=[])
            
            try:
                group.save()            
            except ldap.ALREADY_EXISTS:
                return usergroups(request, err={'err': 'usergroup_exist'})
                
            return usergroups(request, usergroup_modification={'groupname': groupname, 'modification': 'add'})
    else:
        form = UserGroupForm()

    return render_to_response('group_add.html',  {'form': form,}, context_instance=RequestContext(request))
    
@login_required
def usergroup_delete(request, groupname):
    """View for removing user groups"""
    username = request.user.ldap_user._username
    
    try:
        entry = LdapUserGroup.objects.get(name=groupname)
        entry.delete()
        #entry.save()
    except ObjectDoesNotExist:
        return HttpResponse("Brak grupy do usunięcia.")
    
    return usergroups(request, usergroup_modification={'groupname': groupname, 'modification': 'del'})
    
@login_required
def usergroup_member_delete(request, groupname, username):
    """View for removing user groups"""
    #username = request.user.ldap_user._username
    
    try:
        entry = LdapUserGroup.objects.get(name=groupname)
        entry.members.remove(username)
        entry.save()
    except ObjectDoesNotExist :
        #return HttpResponse("Brak grupy do usunięcia.")
        return usergroups(request, err={'err': 'usergroup_not_exist'})
    except ValueError :
        #return HttpResponse("Nie ma takiego użytkownika")
        return usergroups(request, err={'err': 'usergroup_member_not_exist'})
    #return HttpResponse("grupa: " + groupname + "<br />User: " + username)
    return usergroups(request, usergroup_modification={'groupname': groupname, 'modification': 'del'})
    


@login_required
def git_repos(request, repository_modification=None, err=None):
    """View displaying list of repositories"""
    username = request.user.ldap_user._username
    Repos = repo_entry(username)
    repos = []
    for repo in Repos.objects.all():
        repos.append({"name" : repo.repo, "perms": {'userRO': repo.userRO, 'userRW': repo.userRW}})
    del Repos
    return render_to_response('repos.html',  {'err': err, 'repos': repos, 'repository_modification': repository_modification}, context_instance=RequestContext(request))

@login_required
def git_repo_add(request):
    """View for adding repository permissions"""
    repos = list_user_repos(request.user.username)
    if request.method == 'POST':
        form = RepoForm(request.POST, repos=repos)
        if form.is_valid():    
            my_username = request.user.username
            username = form.cleaned_data['username']
            reponame = form.cleaned_data['reponame']
            permissions = form.cleaned_data['permissions']

            # User that want access to repo
            guest = LdapUser.objects.get(uid=username)

            # Owner of repo
            user = LdapUser.objects.get(uid=my_username)
            
            command = 'command="/var/student/gitserver.py %s" ' % (guest,)
            try:
                user.ssh_public_key.append(command + find_primary_key(guest))
                user.save()
            except ldap.TYPE_OR_VALUE_EXISTS:
                pass
            
            Git = git_entry(my_username)
            git = Git()
            git.ou = "git"
            try:
                git.save()
            except ldap.ALREADY_EXISTS:
                pass
            
            Repo = repo_entry(my_username)
            try:
                repo = Repo.objects.get(repo=reponame)
            except ObjectDoesNotExist:
                repo = Repo()

            repo.repo = reponame;
            if permissions == "rw":
                repo.userRW.append(username)
            elif permissions == "ro":
                repo.userRO.append(username)

            try:
                repo.save()            
            except ldap.TYPE_OR_VALUE_EXISTS:
                return git_repos(request, err={'err': 'permission_exist'})
                
            return git_repos(request, repository_modification={'username': username, 'reponame': reponame, 'permission': 'zapis' if permissions == 'rw' else 'odczyt', 'modification': 'add'})
    else:
        if not repos:
            return render_to_response('repos.html',  {'error_no_git_dir': True}, context_instance=RequestContext(request))
        form = RepoForm(repos=repos)

    return render_to_response('repo_add.html',  {'form': form,}, context_instance=RequestContext(request))
    

def confirm(request, activation_key):
    """View for confirming email address"""
    form = LogInForm()
    try:
        user = TemporaryUser.objects.get(confirmation_link=activation_key)
        if user.confirmed:
            return render_to_response('invitation.html',  {'confirmed': 1, 'form': form}, context_instance=RequestContext(request))
        user.confirmed = True
        user.save()
        return render_to_response('invitation.html',  {'confirmed': 2, 'form': form}, context_instance=RequestContext(request))
    except ObjectDoesNotExist:
        return render_to_response('invitation.html',  {'confirmed': 3, 'form': form}, context_instance=RequestContext(request))

def registration(request):
    """Registration view"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            surname = form.cleaned_data['surname']
            email = form.cleaned_data['email']
            password = form.cleaned_data['repeat_password']
            ssh_public_key = form.cleaned_data['ssh_public_key']
            studies_year = form.cleaned_data['studies_year']
            
            if not username:
                username = strip_polish_letters(name[0] + surname).lower()
                        
            user = TemporaryUser(username=username,
                                 name=name,
                                 surname=surname,
                                 email=email,
                                 password=password,
                                 ssh_public_key=ssh_public_key,
                                 studies_year=studies_year,
                                 confirmed=False,
                                 confirmation_link=generate_confirmation_link())
            user.save()
            send_confirmation_mail(user)
            form = LogInForm()
            return render_to_response('invitation.html',  {'confirmed': 4, 'form': form}, context_instance=RequestContext(request))
          
    else:
        form = RegistrationForm()

    return render_to_response('registration.html',  {'form': form,}, context_instance=RequestContext(request))



def exam_verification(request):
    """View used by exams and examsmanagement applications to verify user login and password by sending jsonp answer"""
    
    callback = ''
    isLogged = 'false'
    #log = open('/tmp/student.log', 'w')
    
    if request.method == 'GET':       
        login = request.GET['login']
        login = urllib.unquote(login)
        #login = urllib.unquote(urllib.quote(login.encode("utf8")))
        password = request.GET['password']
        password = urllib.unquote(password)
        #log.write(login + '\n')
        #log.write(password + '\n')
        try:
            callback = request.GET['callback']
        except KeyError:
            pass
        
        try:
            l = ldap.open('localhost')
            l.bind_s('uid=' + login + ',ou=users,dc=icis,dc=pcz,dc=pl', password)
            isLogged = 'true'    
            l.unbind_s()     
        except:
            pass
    
    if callback:
        data = callback + '([{"response":"' + isLogged + '"}]);'
    else:
        data = '[{"response":"' + isLogged + '"}]'
    #log.write(callback + '\n')
    #log.flush()    
    #log.close()
    response = HttpResponse(data, content_type='text/javascript')
    response['Content-Length'] = len(data)
    response['Expires'] = '-1'
    response['Cache-Control'] = 'no-cache'
    response['Pragma'] = 'no-cache'
    return response