from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
from .models import Friend
from authentication.models import User
from django.shortcuts import get_object_or_404


class BaseFriendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def serialize_friend(self, friendship):
        return {
            'id': friendship.id,
            'recipient': friendship.recipient.username,
            'sender': friendship.sender.username,
            'state': friendship.state
        }


class FriendShipStatus(BaseFriendView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        username = request.GET.get('username')
        current_user = request.user
        target_user = get_object_or_404(User, username=username)

        try:
            friendship = Friend.objects.get(
                Q(sender=current_user, recipient=target_user) |
                Q(sender=target_user, recipient=current_user)
            )
        except Friend.DoesNotExist:
            return Response({'error': 'relation not found'}, status=status.HTTP_404_NOT_FOUND)

        friend = self.serialize_friend(friendship)

        return Response(
            friend,
            status=status.HTTP_200_OK
        )


# lists
class AcceptedFriendView(BaseFriendView):
    def get(self, request):
        current_user = request.user

        accepted_friends = Friend.objects.filter(
            Q(sender=current_user) | Q(recipient=current_user),
            state='accepted'
        )

        serialized_friends = [
            self.serialize_friend(friendship)
            for friendship in accepted_friends
        ]

        return Response(
            serialized_friends,
            status=status.HTTP_200_OK
        )


class BlockedFriendView(BaseFriendView):
    def get(self, request):
        current_user = request.user

        blocked_friends = Friend.objects.filter(
            sender=current_user,
            state='blocked'
        )

        serialized_friends = [
            self.serialize_friend(friendship)
            for friendship in blocked_friends
        ]

        return Response(
            serialized_friends,
            status=status.HTTP_200_OK
        )


class IncomingFriendRequestView(BaseFriendView):
    def get(self, request):
        current_user = request.user

        incoming_requests = Friend.objects.filter(
            recipient=current_user,
            state='pending'
        )

        serialized_friends = [
            self.serialize_friend(friendship)
            for friendship in incoming_requests
        ]

        return Response(
            serialized_friends,
            status=status.HTTP_200_OK
        )


class OutgoingFriendRequestView(BaseFriendView):
    def get(self, request):
        current_user = request.user

        outgoing_requests = Friend.objects.filter(
            sender=current_user,
            state='pending'
        )

        serialized_friends = [
            self.serialize_friend(friendship)
            for friendship in outgoing_requests
        ]

        return Response(
            serialized_friends,
            status=status.HTTP_200_OK
        )


# actions


class SendFriendRequestView(BaseFriendView):
    def post(self, request):
        username = request.data.get('username')
        print('username: ', username)
        current_user = request.user
        target_user = get_object_or_404(User, username=username)
        print('target_user: ', target_user)

        try:
            friendship = Friend.objects.get(sender=target_user, recipient=current_user, state='none')
            friendship.state = 'pending'
            friendship.save()
            friend = self.serialize_friend(friendship)
            return Response(friend, status=status.HTTP_201_CREATED)
        except Friend.DoesNotExist:
            friendship = Friend.objects.create(sender=current_user, recipient=target_user, state='pending')
            friend = self.serialize_friend(friendship)
            return Response(friend, status=status.HTTP_201_CREATED)


class ConfirmFriendRequestView(BaseFriendView):
    def post(self, request):
        username = request.data.get('username')
        current_user = request.user
        target_user = get_object_or_404(User, username=username)

        friend_request = get_object_or_404(Friend, sender=target_user, recipient=current_user, state='pending')
        friend_request.state = 'accepted'
        friend_request.save()
        friend = self.serialize_friend(friendship=friend_request)
        return Response(friend, status=status.HTTP_200_OK)


class CancelFriendRequestView(BaseFriendView):
    def post(self, request):
        username = request.data.get('username')
        current_user = request.user
        target_user = get_object_or_404(User, username=username)

        try:
            friendship = Friend.objects.filter(
                Q(sender=current_user, recipient=target_user, state='pending') |
                Q(sender=target_user, recipient=current_user, state='pending')
            ).delete()
            friend = self.serialize_friend(friendship)
            return Response(friend, status=status.HTTP_200_OK)
        except Friend.DoesNotExist:
            return Response({'error': 'relation not found'}, status=status.HTTP_404_NOT_FOUND)


class RemoveFriendView(BaseFriendView):
    def post(self, request):
        username = request.data.get('username')
        current_user = request.user
        target_user = get_object_or_404(User, username=username)
        try:
            friendship = Friend.objects.filter(
                Q(sender=current_user, recipient=target_user, state='accepted') |
                Q(sender=target_user, recipient=current_user, state='accepted')
            ).delete()
            friend = self.serialize_friend(friendship)
            return Response(friend, status=status.HTTP_200_OK)
        except Friend.DoesNotExist:
            return Response({'error': 'relation not found'}, status=status.HTTP_404_NOT_FOUND)


class BlockView(BaseFriendView):
    def post(self, request):
        username = request.data.get('username')
        current_user = request.user
        target_user = get_object_or_404(User, username=username)

        try:
            Friend.objects.filter(
                Q(sender=current_user, recipient=target_user) |
                Q(sender=target_user, recipient=current_user)
            ).delete()
        except Friend.DoesNotExist:
            print('')
        friendship = Friend.objects.create(sender=current_user, recipient=target_user, state='blocked')
        friend = self.serialize_friend(friendship)
        return Response(friend, status=status.HTTP_200_OK)


class UnblockView(BaseFriendView):
    def post(self, request):
        username = request.data.get('username')
        current_user = request.user
        target_user = get_object_or_404(User, username=username)

        try:
            friendship = Friend.objects.filter(
                Q(sender=current_user, recipient=target_user, state='blocked')
            ).delete()
            friend = self.serialize_friend(friendship)
            return Response(friend, status=status.HTTP_200_OK)
        except Friend.DoesNotExist:
            return Response({'error': 'relation not found'}, status=status.HTTP_404_NOT_FOUND)