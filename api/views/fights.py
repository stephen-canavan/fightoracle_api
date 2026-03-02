from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from api.models import Fight, Fighter
from api.serializers import FightSerializer
from django.db.models import Q
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.decorators import action

from api.services.fights import complete_fight
from api.pagination import FightPagination


class FightViewSet(viewsets.ViewSet):
    pagination_class = FightPagination
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        fighter_id = self.kwargs.get("fighter_pk")
        event_id = self.kwargs.get("event_pk")
        query_set = Fight.objects.all()

        if event_id:
            query_set = query_set.filter(event=event_id)
        if fighter_id:
            query_set = query_set.filter(
                Q(fighter_red__id=fighter_id) | Q(fighter_blue__id=fighter_id)
            )

        return query_set.order_by('-event__date', 'card_position')

    def list(self, request, **kwargs):
        fights = self.get_queryset()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(fights, request)
        serializer = FightSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        fight = get_object_or_404(Fight, id=pk)
        serializer = FightSerializer(fight)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        fight = get_object_or_404(Fight, id=pk)
        fight.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        fight = get_object_or_404(Fight, id=pk)

        winner = get_object_or_404(Fighter, pk=request.data["winner_id"])
        method = request.data["method"]
        round = request.data["round"]

        complete_fight(fight, winner=winner, method=method, round=round)

        return Response({"status": "completed"})
