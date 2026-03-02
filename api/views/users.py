from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.models import User
from api.serializers import UserSerializer
from rest_framework import viewsets
from api.permissions import IsOwner
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from api.serializers.users import ChangePasswordSerializer
from api.pagination import UserPagination


class UserViewSet(viewsets.ViewSet):
    pagination_class = UserPagination
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        if self.action == "change_password":
            return [IsOwner()]
        if self.action in ["destroy", "update", "partial_update"]:
            return [IsOwner(), IsAdminUser()]

        return [IsAdminUser()]

    def list(self, request):
        self.check_permissions(request)
        users = User.objects.all()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(page, context={"request": request}, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(User, username=pk)
        self.check_object_permissions(request, user)
        serializer = UserSerializer(user, context={"request": request})
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        user = get_object_or_404(User, username=pk)
        self.check_object_permissions(request, user)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, username=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, username=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request):
        print(f"Create user request: {request.data}")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def change_password(self, request, pk=None):
        user = get_object_or_404(User, username=pk)
        self.check_object_permissions(request, user)

        print(f"Change password request: {request.data}")

        # Ensure user is changing their own password
        if request.user != user:
            return Response(
                {"detail": "You can only change your own password."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.validated_data["current_password"]):
                return Response(
                    {"current_password": "Wrong password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(serializer.validated_data["new_password"])
            user.save()

            return Response({"detail": "Password updated successfully."})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
