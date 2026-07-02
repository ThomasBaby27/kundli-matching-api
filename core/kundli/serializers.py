from rest_framework import serializers
from .models import BirthProfile, MatchHistory

class BirthDetailSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    date_of_birth = serializers.DateField(input_formats=['%Y-%m-%d'])
    time_of_birth = serializers.TimeField(input_formats=['%H:%M:%S'])
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

class KundliMatchRequestSerializer(serializers.Serializer):
    male = BirthDetailSerializer()
    female = BirthDetailSerializer()

class MatchHistorySerializer(serializers.ModelSerializer):
    male_name = serializers.CharField(source='male_profile.name', read_only=True)
    female_name = serializers.CharField(source='female_profile.name', read_only=True)
    class Meta:
        model = MatchHistory
        fields = [
            'id', 
            'male_name', 
            'female_name', 
            'compatibility_score', 
            'verdict', 
            'breakdown', 
            'calculated_at'
        ]