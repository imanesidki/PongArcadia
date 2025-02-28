from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
from .models import Friend
from authentication.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


# lists
class BaseFriendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def serialize_friend(self, friendship, current_user):
        friend_user = friendship.recipient if friendship.sender == current_user else friendship.sender
        return {
            'id': friendship.id,
            'friend_id': friend_user.id,
            'username': friend_user.username,
            'state': friendship.state
        }


class AcceptedFriendView(BaseFriendView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        current_user = request.user

        accepted_friends = Friend.objects.filter(
            Q(sender=current_user) | Q(recipient=current_user),
            state='accepted'
        )

        serialized_friends = [
            self.serialize_friend(friendship, current_user)
            for friendship in accepted_friends
        ]

        return Response(
            {"data": serialized_friends},
            status=status.HTTP_200_OK
        )



class BlockedFriendView(BaseFriendView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        current_user = request.user

        blocked_friends = Friend.objects.filter(
            sender=current_user,
            state='blocked'
        )

        serialized_friends = [{
            'id': friendship.id,
            'friend_id': friendship.recipient.id,
            'username': friendship.recipient.username,
            'state': friendship.state
        } for friendship in blocked_friends]

        return Response(
            {"data": serialized_friends},
            status=status.HTTP_200_OK
        )


class IncomingFriendRequestView(BaseFriendView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        current_user = request.user

        incoming_requests = Friend.objects.filter(
            recipient=current_user,
            state='pending'
        )

        serialized_friends = [{
            'id': friendship.id,
            'friend_id': friendship.sender.id,
            'username': friendship.sender.username,
            'state': friendship.state
        } for friendship in incoming_requests]

        return Response(
            {"data": serialized_friends},
            status=status.HTTP_200_OK
        )


class OutgoingFriendRequestView(BaseFriendView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        current_user = request.user

        outgoing_requests = Friend.objects.filter(
            sender=current_user,
            state='pending'
        )

        serialized_friends = [{
            'id': friendship.id,
            'friend_id': friendship.recipient.id,
            'username': friendship.recipient.username,
            'state': friendship.state
        } for friendship in outgoing_requests]

        return Response(
            {"data": serialized_friends},
            status=status.HTTP_200_OK
        )


# actions


class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        target_user_id = request.data.get('target_user_id')
        current_user = request.user
        target_user = get_object_or_404(User, id=target_user_id)

        Friend.objects.create(sender=current_user, recipient=target_user, state='pending')
        return Response({'status': 'Friend request sent'}, status=status.HTTP_201_CREATED)


class ConfirmFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        target_user_id = request.data.get('target_user_id')
        current_user = request.user
        target_user = get_object_or_404(User, id=target_user_id)

        friend_request = get_object_or_404(Friend, sender=target_user, recipient=current_user, state='pending')
        if not friend_request:
            return Response({'Error': 'relation not found'}, status=status.HTTP_404_NOT_FOUND)
        friend_request.state = 'accepted'
        friend_request.save()
        return Response({'data': 'Friend request confirmed'}, status=status.HTTP_200_OK)


class CancelFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        target_user_id = request.data.get('target_user_id')
        current_user = request.user
        target_user = get_object_or_404(User, id=target_user_id)

        try:
            Friend.objects.filter(
                Q(sender=current_user, recipient=target_user, state='pending') |
                Q(sender=target_user, recipient=current_user, state='pending')
            ).delete()
        except Friend.DoesNotExist:
            return Response({'error': 'relation not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'data': 'Friend request cancelled'}, status=status.HTTP_200_OK)


class RemoveFriendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        target_user_id = request.data.get('target_user_id')
        current_user = request.user
        target_user = get_object_or_404(User, id=target_user_id)
        try:
            Friend.objects.filter(
                Q(user=current_user, friend=target_user, state='accepted') |
                Q(user=target_user, friend=current_user, state='accepted')
            ).delete()
        except Friend.DoesNotExist:
            return Response({'error': 'relation not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'data': 'Friend removed'}, status=status.HTTP_200_OK)


class BlockView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        target_user_id = request.data.get('target_user_id')
        current_user = request.user
        target_user = get_object_or_404(User, id=target_user_id)

        Friend.objects.filter(
            Q(sender=current_user, recipient=target_user) |
            Q(sender=target_user, recipient=current_user)
        ).delete()
        Friend.objects.create(sender=current_user, recipient=target_user, state='blocked')
        
        # Send WebSocket notification to the blocked user
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{target_user.username}",
            {
                "type": "block_status_update",
                "event": "block_status_update",
                "status": "blocked",
                "blocker": {
                    "id": current_user.id,
                    "username": current_user.username,
                }
            }
        )
        
        return Response({'data': 'User blocked'}, status=status.HTTP_200_OK)


class UnblockView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        target_user_id = request.data.get('target_user_id')
        current_user = request.user
        target_user = get_object_or_404(User, id=target_user_id)

        blocked = Friend.objects.filter(sender=current_user, recipient=target_user, state='blocked')
        if not blocked:
            return Response({'error': 'relation not found'}, status=status.HTTP_404_NOT_FOUND)
        blocked.delete()
        
        # Send WebSocket notification to the unblocked user
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{target_user.username}",
            {
                "type": "block_status_update",
                "event": "block_status_update",
                "status": "unblocked",
                "blocker": {
                    "id": current_user.id,
                    "username": current_user.username,
                }
            }
        )
        
        return Response({'data': 'User unblocked'}, status=status.HTTP_200_OK)


class CheckBlockedByView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        current_user = request.user
        target_user = get_object_or_404(User, id=user_id)
        
        # Check if target_user has blocked current_user
        is_blocked = Friend.objects.filter(
            sender=target_user,
            recipient=current_user,
            state='blocked'
        ).exists()
        
        return Response({
            'is_blocked': is_blocked
        }, status=status.HTTP_200_OK)