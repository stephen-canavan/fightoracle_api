from rest_framework import serializers
from api.models import Fighter
from api.serializers.promotions import PromotionSummarySerializer
from fightoracle_api.settings import COUNTRIES


class FighterRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fighter
        fields = ["wins", "losses", "draws", "no_contests", "dqs"]


class FighterSerializer(serializers.ModelSerializer):
    record = FighterRecordSerializer(source="*")
    promotion = PromotionSummarySerializer()
    avatar_url = serializers.ImageField(source="avatar")
    country = serializers.SerializerMethodField()
    height = serializers.FloatField()
    reach = serializers.FloatField()
    weight_class = serializers.CharField(source="get_weight_class_display")
    stats = serializers.SerializerMethodField()
    last_five_results = serializers.ListField(read_only=True)

    class Meta:
        model = Fighter
        fields = [
            "id",
            "ufcstats_fighter_id",
            "fname",
            "sname",
            "nickname",
            "weight_class",
            "promotion",
            "dob",
            "height",
            "reach",
            "record",
            "stats",
            "last_five_results",
            "avatar_url",
            "country",
        ]

    def get_stats(self, obj):
        return {
            "slpm": float(obj.slpm) if obj.slpm else None,
            "str_acc": obj.str_acc,
            "sapm": float(obj.sapm) if obj.sapm else None,
            "str_def": obj.str_def,
            "td_avg": float(obj.td_avg) if obj.td_avg else None,
            "td_acc": obj.td_acc,
            "td_def": obj.td_def,
            "sub_avg": float(obj.sub_avg) if obj.sub_avg else None,
            "win_by_kotko": obj.win_by_kotko,
            "win_by_sub": obj.win_by_sub,
            "win_by_dec": obj.win_by_dec,
        }
    
    def get_country(self, obj):
        if not obj.country:
            return None

        flag_url = COUNTRIES.get_flag(obj.country.code)

        return {
            "code": obj.country.code,
            "name": obj.country.name,
            "flag": flag_url,  # CDN flag URL
        }


class FighterSummarySerializer(serializers.ModelSerializer):
    avatar_url = serializers.ImageField(source="avatar")

    class Meta:
        model = Fighter
        fields = ["id", "name", "avatar_url"]
