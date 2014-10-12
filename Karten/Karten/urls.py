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
router.register(r'user/(?P<user_id>[^/]+)/friends', views.KartenUserFriendsView)
router.register(r'friends/requests/outgoing', views.KartenUserFriendRequestView, base_name='outgoing_requests')
router.register(r'friends/requests/incoming', views.KartenUserFriendAcceptView, base_name='incoming_requests')

urlpatterns = patterns('Karten.views',
    url(r'^stacks/(?P<stack_id>\w+)/share', views.share_stack),
    url(r'^users/me', views.KartenCurrentUserView.as_view()),
    url(r'^users/search', views.user_search),
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
