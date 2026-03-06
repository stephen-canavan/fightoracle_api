from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.models import User, Prediction
from api.serializers import UserSerializer, PredictionSerializer
from rest_framework import viewsets
from api.permissions import IsOwner
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from api.serializers.users import ChangePasswordSerializer
from api.pagination import UserPagination
from collections import OrderedDict
from itertools import groupby


class UserViewSet(viewsets.ViewSet):
    pagination_class = UserPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve", "event_predictions"]:
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

    @action(detail=True, methods=["get"], url_path="predictions")
    def predictions(self, request, pk=None):
        """
        Get all predictions for a user (standard pagination).
        """
        user = get_object_or_404(User, username=pk)

        predictions = (
            Prediction.objects.filter(user=user)
            .select_related("fight__event", "fight__fighter_red", "fight__fighter_blue")
            .order_by("-prediction_date")
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(predictions, request)
        serializer = PredictionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"], url_path="event_predictions")
    def event_predictions(self, request, pk=None):
        """
        Get predictions grouped by event for a user.
        Returns complete event groups to avoid splitting predictions across pages.
        Supports filtering by event status via ?status=scheduled or ?status=completed
        """
        user = get_object_or_404(User, username=pk)

        # Get status filter from query params
        status_filter = request.query_params.get("status", None)

        # Get all predictions for the user, ordered by event date (desc) then event id
        predictions = (
            Prediction.objects.filter(user=user)
            .select_related("fight__event", "fight__fighter_red", "fight__fighter_blue")
        )
        
        # Apply status filter if provided
        if status_filter:
            if status_filter.lower() == "scheduled":
                predictions = predictions.filter(fight__event__status="SCHEDULED")
                # Scheduled events: soonest first (ascending date)
                predictions = predictions.order_by("fight__event__date", "fight__event__id", "fight__card_position")
            elif status_filter.lower() == "completed":
                predictions = predictions.filter(fight__event__status="COMPLETED")
                # Completed events: most recent first (descending date)
                predictions = predictions.order_by("-fight__event__date", "fight__event__id", "-fight__card_position")
        else:
            # No filter: order by date ascending (upcoming events first)
            predictions = predictions.order_by("fight__event__date", "fight__event__id", "fight__card_position")

        # Group predictions by event
        grouped = []
        for event_id, group in groupby(predictions, key=lambda p: p.fight.event.id):
            event_predictions = list(group)
            grouped.append({"event_id": event_id, "predictions": event_predictions})

        # Paginate the groups (not individual predictions)
        paginator = self.pagination_class()
        page_size = 999  # Load all events at once
        page_number = int(request.query_params.get("page", 1))

        start = (page_number - 1) * page_size
        end = start + page_size
        page_groups = grouped[start:end]

        # Flatten predictions from the page groups
        page_predictions = []
        for group in page_groups:
            page_predictions.extend(group["predictions"])

        # Serialize
        serializer = PredictionSerializer(page_predictions, many=True)

        # Build paginated response
        has_next = end < len(grouped)
        next_url = None
        if has_next:
            next_url = request.build_absolute_uri(f"?page={page_number + 1}")

        return Response(
            OrderedDict(
                [
                    ("count", len(predictions)),
                    ("next", next_url),
                    (
                        "previous",
                        None
                        if page_number == 1
                        else request.build_absolute_uri(f"?page={page_number - 1}"),
                    ),
                    ("results", serializer.data),
                ]
            )
        )
