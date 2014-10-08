from django.conf.urls import patterns, include, url
import Karten
from Karten import views

from django.contrib import admin
admin.autodiscover()

from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

router = DefaultRouter()
router.register(r'users', views.KartenUserViewSet)
router.register(r'stacks', views.KartenStackViewSet, base_name='user_stacks')
router.register(r'users/(?P<user_id>[^/]+)/friends', views.KartenUserFriendsView)
router.register(r'friends/outgoing', views.KartenUserFriendRequestView, base_name='outgoing_requests')
router.register(r'friends/incoming', views.KartenUserFriendAcceptView, base_name='incoming_requests')

urlpatterns = patterns('Karten.views',
    url(r'^stacks/(?P<stack_id>\w+)/user/(?P<user_id>\w+)/add', 'add_user_to_stack'),
    url(r'^users/me', views.KartenCurrentUserView.as_view()),
#    url(r'friends/requests/outgoing', views.KartenUserFriendRequestView.as_view()),
#    url(r'friends/requests/incoming', views.KartenUserFriendAcceptView.as_view()),

    ## Below: to be deleted!

    url(r'^user/(?P<user_id>\w+)/stacks/all', 'get_user_stacks'),

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
