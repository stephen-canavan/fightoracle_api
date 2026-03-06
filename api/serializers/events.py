from rest_framework import serializers
from api.models import Event
from api.serializers.promotions import PromotionSummarySerializer


class EventSerializer(serializers.ModelSerializer):
    promotion = PromotionSummarySerializer()

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "promotion",
            "country",
            "city",
            "venue",
            "date",
            "status",
            "banner_image",
        ]


class EventSummarySerializer(serializers.ModelSerializer):
    promotion_logo = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = ["id", "name", "date", "status", "promotion_logo", "banner_image", "city", "country"]
    
    def get_promotion_logo(self, obj):
        if obj.promotion and obj.promotion.logo:
            return obj.promotion.logo.url
        return None
