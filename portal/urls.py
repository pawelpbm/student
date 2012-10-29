from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'student.management.views.home', name='home'),
    url(r'^account/$', 'student.management.views.account', name='account'),
    url(r'^account/logout$', 'student.management.views.logout_view', name='logout_view'),
    url(r'^account/groups$', 'student.management.views.usergroups', name='usergroups'),
    url(r'^account/groups/add$', 'student.management.views.usergroup_add', name='usergroup_add'),
    url(r'^account/repositories$', 'student.management.views.git_repos', name='git_repos'),
    url(r'^account/repositories/add$', 'student.management.views.git_repo_add', name='git_repo_add'),
    url(r'^registration/$', 'student.management.views.registration', name='registration'),
    url(r'^confirm/(?P<activation_key>\w+)/$', 'student.management.views.confirm', name='confirm'),
    url(r'^account/repositories/del/(?P<reponame>\w+)/(?P<username>\w+)/(?P<permissions>\w+)$', 'student.management.views.delete', name='delete'),
     # url(r'^student/', include('student.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
