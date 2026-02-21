from api.models import Prediction
from rest_framework import serializers
from django.utils import timezone
from api.serializers.events import EventSummarySerializer
from api.serializers.users import UserSummarySerializer
from api.serializers.fights import FightSummarySerializer, FightResultSerializer
from api.serializers.fighters import FighterSummarySerializer
from api.models import Fight, Event


class PredictionResultSerializer(serializers.ModelSerializer):
    predicted_winner = FighterSummarySerializer()

    class Meta:
        model = Prediction
        fields = ["predicted_winner", "predicted_method", "predicted_round"]


class PredictionSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    fight = FightSummarySerializer(read_only=True)
    event = EventSummarySerializer(source="fight.event", read_only=True)
    result = FightResultSerializer(source="fight", read_only=True)
    predicted_result = PredictionResultSerializer(source="*", read_only=True)
    prediction_date = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", read_only=True
    )

    # Write-only fields for POST
    fight_id = serializers.PrimaryKeyRelatedField(
        queryset=Fight.objects.all(), source="fight", write_only=True
    )
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(), source="event", write_only=True
    )

    class Meta:
        model = Prediction
        fields = "__all__"
        read_only_fields = ["points_potential", "points_earned", "perfect_prediction"]

    def create(self, validated_data):
        user = validated_data.pop("user")
        fight = validated_data["fight"]

        obj, _ = Prediction.objects.update_or_create(
            user=user,
            fight=fight,
            defaults=validated_data,
        )
        return obj

    def validate(self, attrs):
        fight = attrs.get("fight")

        # If updating and fight not provided, use existing fight
        if not fight and self.instance:
            fight = self.instance.fight

        if fight and fight.event.date <= timezone.now():
            print("Date error")
            raise serializers.ValidationError(
                "You cannot make or modify a prediction once the event has started."
            )

        return attrs
