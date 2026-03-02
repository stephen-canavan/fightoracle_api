from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from api.models import Fighter
from api.serializers import FighterSerializer
from rest_framework.permissions import IsAdminUser, AllowAny
from api.pagination import FighterPagination


class FighterViewSet(viewsets.ViewSet):
    pagination_class = FighterPagination
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        event_id = self.kwargs.get("event_pk")
        fight_id = self.kwargs.get("fight_pk")
        query_set = Fighter.objects.all()

        if event_id:
            # fights = Fight.objects.get(event_id=event_id)
            pass

        if fight_id:
            pass

        return query_set

    def list(self, request, **kwargs):
        fighters = self.get_queryset()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(fighters, request)
        serializer = FighterSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        fighter = get_object_or_404(Fighter, id=pk)
        serializer = FighterSerializer(fighter)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        fighter = get_object_or_404(Fighter, id=pk)
        fighter.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
