from django.conf.urls import patterns, include, url
import Karten

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('Karten.views',
    # Examples:
    # url(r'^$', 'Karten.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^users', 'all_users'),
    url(r'^user/create', 'create_user'), #POST
    url(r'^user/(?P<user_id>\w+)$', 'get_user'),
    url(r'^user/(?P<user_id>\w+)/update', 'update_user'), #POST
    url(r'^user/(?P<user_id>\w+)/databases/all', 'get_user_databases'),
    url(r'^user/(?P<user_id>\w+)/friends/$', 'get_user_friends'),
    url(r'^user/(?P<user_id>\w+)/friends/add', 'create_user_friend'), #POST
    url(r'^user/(?P<user_id>\w+)/friends/remove/(?P<friend_id>\w+)', 'remove_user_friend'),

    url(r'^database/create', 'create_database'),
    url(r'^database/(?P<database_id>\w+)/delete', 'delete_database'),
    url(r'^database/(?P<database_id>\w+)/user/(?P<user_id>\w+)/add', 'add_user_to_database'),
    url(r'^database/(?P<database_id>\w+)/user/(?P<user_id>\w+)/delete', 'remove_user_from_database'),
    url(r'^database/(?P<database_id>\w+)/users/all', 'get_all_users_for_database'),
    

    url(r'^admin/', include(admin.site.urls)),
)
