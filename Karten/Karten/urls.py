from django.conf.urls import patterns, include, url
import Karten
from Karten import views

from django.contrib import admin
admin.autodiscover()

from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

user_list = views.KartenUserViewSet.as_view(actions={
    'get' : 'list',
    'post' : 'create',
})

user_stacks = views.KartenStackViewSet.as_view(actions={
    'get' : 'list',
    'post' : 'create',
})

router = DefaultRouter()
router.register(r'users', views.KartenUserViewSet)
router.register(r'stacks', views.KartenStackViewSet, base_name='user_stacks')

urlpatterns = patterns('Karten.views',
    url(r'^user/(?P<user_id>\w+)/stacks/all', 'get_user_stacks'),
    url(r'^user/(?P<user_id>\w+)/friends/$', 'get_user_friends'),
    url(r'^user/(?P<user_id>\w+)/friends/add', 'create_user_friend'),

    url(r'^stack/create', 'create_stack'),
    url(r'^stack/(?P<stack_id>\w+)/delete', 'delete_stack'),
    url(r'^stack/(?P<stack_id>\w+)/user/(?P<user_id>\w+)/add', 'add_user_to_stack'),
    url(r'^stack/(?P<stack_id>\w+)/user/(?P<user_id>\w+)/delete', 'remove_user_from_stack'),
    url(r'^stack/(?P<stack_id>\w+)/users/all', 'get_all_users_for_stack'),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
        url(r'^', include(router.urls)),
)
urlpatterns += patterns('',
            url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token')
)

urlpatterns += patterns('',
            url(r'^api-auth/', include('rest_framework.urls',
                                               namespace='rest_framework')),
            )
