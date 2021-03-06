from Karten.models import *
from Karten.errors import *
from Karten.json_utils import *
from django.utils.translation import ugettext as _
from datetime import datetime
from django.utils import timezone

from django.http import HttpResponseRedirect, HttpResponse
from django.http import Http404, QueryDict


from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework import status
from Karten.serializers import *
from rest_framework.decorators import detail_route, list_route, link, api_view, permission_classes

import json
import jsonpickle
from rest_framework.parsers import JSONParser

class KartenUserViewSet(viewsets.ModelViewSet):

    queryset = KartenUser.objects.all()
    serializer_class = KartenUserSerializer
    permission_classes = (permissions.AllowAny,)

    def update(self, reqeust):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        user = self.get_object()
        user.date_last_seen = timezone.now()
        user.save()
        serializer = KartenUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user_serializer = self.serializer_class(data=request.DATA)
        if user_serializer.is_valid():
            new_user = user_serializer.object
            new_user.set_password(new_user.password)
            time_now = timezone.now()
            new_user.date_joined = time_now
            new_user.date_last_seen = time_now
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class KartenStackViewSet(viewsets.ModelViewSet):

    serializer_class = KartenStackSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return KartenStack.objects.filter(allowed_users=user)
    def pre_save(self, obj):
        obj.owner = self.request.user

    def post_save(self, obj, created):
        if created is True:
            obj.allowed_users.add(self.request.user)

class KartenCurrentUserView(APIView):

    serializer_class = KartenUserSerializer

    model = KartenUser

    def get(self, request, format=None):
        user = request.user
        user_serializer = self.serializer_class(user)
        return Response(user_serializer.data)

    def put(self, request):

        update_dict = JSONParser().parse(request)
        updated_user = KartenUserSerializer(request.user, data=update_dict, partial=True)
        if updated_user.is_valid():
            updated_user.save()
            return Response(updated_user.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)



class KartenUserFriendsView(viewsets.ViewSet):

    serializer_class = KartenUserSerializer
    model = KartenUser

    def list(self, request, user_id=None):
        try:
            user = KartenUser.objects.get(id=user_id)
            users = user.friends.all()
            serializer = self.serializer_class(users, many=True)
            return Response(serializer.data)
        except KartenUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class KartenUserFriendRequestView(viewsets.ViewSet):
   
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request):
        try:
            friends_requesting = request.DATA.getlist('user_ids')
            new_requests = []
            new_friends = KartenUser.objects.filter(id__in=friends_requesting)
            for new_friend in new_friends:
                friend_request = KartenUserFriendRequest(requesting_user=self.request.user,
                        accepting_user=new_friend, accepted=False)
                friend_request.save()
                new_requests.append(friend_request)
            serialized_request = KartenFriendRequestSerializer(new_requests, many=True)
            return Response(serialized_request.data, status=status.HTTP_201_CREATED)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except KartenUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        try:
            removed_request = KartenUserFriendRequest.objects.get(requesting_user=request.DATA)
            removed_request.delete()
            return Response(status=status.HTTP_200_OK)
        except KartenUserFriendRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        friend_requests = KartenUserFriendRequest.objects.filter(requesting_user=self.request.user.id)
        serialized_requests = KartenFriendRequestSerializer(friend_requests, many=True)
        return Response(serialized_requests.data, status=status.HTTP_200_OK)

class KartenUserFriendAcceptView(viewsets.ViewSet):

    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        friend_requests = KartenUserFriendRequest.objects.filter(accepting_user=self.request.user.id)
        serialized_requests = KartenFriendRequestSerializer(friend_requests, many=True)
        return Response(serialized_requests.data, status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def accept(self, request, pk):

        try:
            accepting_request = KartenUserFriendRequest.objects.get(id=pk)
            accepting_request.accepted = True
            accepting_request.save()
            return Response(status=status.HTTP_200_OK)
        except KartenUserFriendRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @detail_route(methods=['post'])
    def deny(self, request, pk):

        try:
            denying_request = KartenUserFriendRequest.objects.get(id=pk)
            denying_request.accepted = False
            denying_request.save()
            return Response(status=status.HTTP_200_OK)
        except KartenUserFriendRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def user_search(request):
    query = request.GET.get('q')
    if query is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    matching_users = KartenUser.objects.filter(username__icontains=query)
    serialized_matches = KartenUserSerializer(matching_users, many=True)
    return Response(serialized_matches.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def share_stack(request, stack_id):
    stack = KartenStack.objects.get(id=stack_id)
    if stack.owner.id is not request.user.id:
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        user_dict = JSONParser().parse(request)
        allowed_user_list = user_dict['allowed_users']
    except ValueError:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    user_objs = KartenUser.objects.filter(id__in=allowed_user_list)

    stack.allowed_users.clear()
    stack.allowed_users.add(*user_objs)
    stack.save()
    user_ids = [user.id for user in stack.allowed_users.all()]
    serialized_allowed_users = json.dumps(user_ids)
    return Response(serialized_allowed_users, status=status.HTTP_201_CREATED)
