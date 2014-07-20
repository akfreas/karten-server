from django.conf.urls import patterns, include, url
import Karten

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('Karten.views',
    url(r'^users', 'all_users'),
    url(r'^user/create', 'create_user'),
    url(r'^user/(?P<user_id>\w+)$', 'get_user'),
    url(r'^user/(?P<user_id>\w+)/update', 'update_user'),
    url(r'^user/(?P<user_id>\w+)/stacks/all', 'get_user_stacks'),
    url(r'^user/(?P<user_id>\w+)/friends/$', 'get_user_friends'),
    url(r'^user/(?P<user_id>\w+)/friends/add', 'create_user_friend'),
    #url(r'^user/(?P<user_id>\w+)/friends/remove/(?P<friend_id>\w+)', 'remove_user_friend'),

    url(r'^stack/create', 'create_stack'),
    url(r'^stack/(?P<stack_id>\w+)/delete', 'delete_stack'),
    url(r'^stack/(?P<stack_id>\w+)/user/(?P<user_id>\w+)/add', 'add_user_to_stack'),
    url(r'^stack/(?P<stack_id>\w+)/user/(?P<user_id>\w+)/delete', 'remove_user_from_stack'),
    url(r'^stack/(?P<stack_id>\w+)/users/all', 'get_all_users_for_stack'),
    

    url(r'^admin/', include(admin.site.urls)),
)
