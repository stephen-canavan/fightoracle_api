from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from api.models import Event
from api.serializers import EventSerializer
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.decorators import action
from api.services.events import complete_event
from api.pagination import EventPagination


class EventViewSet(viewsets.ViewSet):
    pagination_class = EventPagination
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self, pk=None, **kwargs):
        promotion_id = self.kwargs.get("promotion_pk")
        query_set = Event.objects.all()

        if promotion_id:
            query_set = query_set.filter(promotion_id=promotion_id)

        return query_set

    def list(self, request, **kwargs):
        events = self.get_queryset(**kwargs)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(events, request)
        serializer = EventSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        event = get_object_or_404(Event, id=pk)
        serializer = EventSerializer(event)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        event = get_object_or_404(Event, id=pk)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        event = get_object_or_404(Event, id=pk)

        try:
            complete_event(event.id)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"status": "completed"})
