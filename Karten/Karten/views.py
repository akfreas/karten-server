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
from jsonpickle.pickler import Pickler

class KartenUserViewSet(viewsets.ModelViewSet):

    queryset = KartenUser.objects.all()
    serializer_class = KartenUserSerializer

    def retrieve(self, request, pk=None):
        user = self.get_object()
        user.date_last_seen = datetime.now()
        user.save()
        serializer = KartenUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user_serializer = self.serializer_class(data=request.DATA)
        if user_serializer.is_valid():
            new_user = user_serializer.object
            new_user.set_password(new_user.password)
            time_now = datetime.now()
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
        user = self.request.user
        user_serializer = self.serializer_class(user)
        return Response(user_serializer.data)



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

@api_view(['POST', 'DELETE'])
@permission_classes((permissions.IsAuthenticated,))
def share_stack(request, stack_id):
    stack = KartenStack.objects.get(id=stack_id)
    if stack.owner.id is not request.user.id:
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'POST':
        share_user_ids = request.POST.getlist('user_ids')
        share_users = KartenUser.objects.filter(id__in=share_user_ids)
        stack.allowed_users.add(*share_users)
        stack.save()
        serialized_allowed_users = KartenUserSerializer(share_users, many=True)
        return Response(serialized_allowed_users.data, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        try:
            user_dict = json.loads(request.body)
            user_list = user_dict['user_ids']
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        stack.allowed_users.remove(*user_list)
        stack.save()
        new_allowed_users = KartenUserSerializer(stack.allowed_users.all(), many=True)
        allowed_user_ids =  [u.id for u in stack.allowed_users.all()]

        return Response(json.dumps(allowed_user_ids), status=status.HTTP_200_OK)

def create_stack(request):
    
    params = request.GET
    if 'owner[id]' in params:
        user_id = params['owner[id]']
    elif 'owner[external_user_id]' in params:
        user_id = params['owner[external_user_id]']
    else:
        e = KartenStackException(message="You need to provide a user ID to create a stack.")
        return e.http_response()

    try:
        user = KartenUser.find_by_unique(user_id)
    except KartenUser.DoesNotExist:
        e = KartenUserDoesNotExist(user_id)
        return e.http_response()

    new_stack = KartenStack(name=params['name'], 
                                 owner=user)
    if 'description' in params.keys():
        new_stack.description = params['description']

    try:
        new_stack.owner = user
        new_stack.creation_date = timezone.now()
        new_stack.save()
    except KartenCouchDBException as e:
        return e.http_response()

    new_stack.allowed_users.add(user)
    new_stack.save()
    return HttpResponse(content=new_stack.to_json(), content_type="application/json")
   

def delete_stack(request, stack_id):
    params = request.GET
    try:
        stack = KartenStack.objects.get(id=stack_id)
    except KeyError:
        exception = ErrorMessage(e.description, e.name)
        return exception.http_response()
    except KartenStack.DoesNotExist:
        KartenStackException(params['id'])
        return KartenStackException.http_response()

    stack.delete()
    return HttpResponse(content=stack.to_json(), content_type="appliction/json")


def get_user_stacks(request, user_id):

    try:
        user = KartenUser.objects.get(id=user_id)
    except KartenUser.DoesNotExist:
        exception = KartenUserDoesNotExist(user_id)
        return exception.http_response()

    stacks = to_json(user.stacks.all())
    return HttpResponse(content=jsonpickle.encode(stacks, unpicklable=False), mimetype="application/json")
    

def add_user_to_stack(request, stack_id, user_id):

    try:
        stack = KartenStack.objects.get(id=stack_id)
    except KartenStack.DoesNotExist:
        e = KartenStackDoesNotExist(stack_id)
        return e.http_response()

    try:
        user = KartenUser.objects.get(id=user_id)
    except KartenUser.DoesNotExist:
        try:
            user = KartenUser.objects.get(external_user_id=user_id)
        except KartenUser.DoesNotExist:
            e = KartenUserDoesNotExist(user_id)
            return e.http_response()

    stack.allowed_users.add(user)
    stack.save()

    response_dict = to_json(stack)
    response_dict['allowed_users'] = to_json(stack.allowed_users.all())
    return HttpResponse(content=jsonpickle.encode(response_dict, unpicklable=False), content_type="application/json")


def remove_user_from_stack(request, stack_id, user_id):

    try:
        stack = KartenStack.objects.get(id=stack_id)
    except KartenStack.DoesNotExist:
        e = KartenStackDoesNotExist(stack_id)
        return e.http_response()

    try:
        user = KartenUser.objects.get(id=user_id)
    except KartenUser.DoesNotExist:
        e = KartenUserDoesNotExist(user_id)
        return e.http_response()

    stack.allowed_users.remove(user)
    stack.save()
    response_dict = to_json(stack)
    response_dict['allowed_users'] = to_json(stack.allowed_users.all())
    return HttpResponse(content=jsonpickle.encode(response_dict, unpicklable=False), content_type="application/json")


def get_all_users_for_stack(request, stack_id):

    try:
        stack = KartenStack.objects.get(id=stack_id)
    except KartenStack.DoesNotExist:
        e = KartenStackDoesNotExist(stack_id)
        return e.http_response()
    users = stack.users.all()
    json_dict = to_json(users)

    return HttpResponse(pickler.encode(json_dict, unpicklable=False), content_type="application_json")


