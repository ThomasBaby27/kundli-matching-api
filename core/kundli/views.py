from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from .models import BirthProfile, MatchHistory
from .utils import calculate_ashtakoot_match
from .serializers import KundliMatchRequestSerializer, MatchHistorySerializer
from datetime import datetime

class KundliMatchView(APIView):
    # Enforces valid JWT token submission via 'Authorization: Bearer <token>' header
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        History Endpoint: Retrieves all past match history records.
        """
        # Fetch history records ordered by the most recent calculations
        history = MatchHistory.objects.all().order_by('-calculated_at')
        serializer = MatchHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def post(self, request):
    #     data = request.data
    #     try:
    #         male_data = data.get('male')
    #         female_data = data.get('female')

    #         # Basic input validation validation
    #         if not male_data or not female_data:
    #             return Response(
    #                 {"error": "Both male and female birth details are required."}, 
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )

    #         # 1. Create a distinct Redis cache key using the birth dates
    #         cache_key = f"match_{male_data.get('date_of_birth')}_{female_data.get('date_of_birth')}"
    #         cached_result = cache.get(cache_key)
            
    #         if cached_result:
    #             # Return immediately from cache memory (Highly optimized)
    #             return Response({"source": "cache", "data": cached_result}, status=status.HTTP_200_OK)
            
    #         # FIX: Convert date_of_birth strings into true Python date objects before ORM operations
    #         if isinstance(male_data.get('date_of_birth'), str):
    #             male_data['date_of_birth'] = datetime.strptime(male_data['date_of_birth'], "%Y-%m-%d").date()
                
    #         if isinstance(female_data.get('date_of_birth'), str):
    #             female_data['date_of_birth'] = datetime.strptime(female_data['date_of_birth'], "%Y-%m-%d").date()

    #         # 2. Persist or fetch profiles from PostgreSQL
    #         male_profile, _ = BirthProfile.objects.get_or_create(gender='M', **male_data)
    #         female_profile, _ = BirthProfile.objects.get_or_create(gender='F', **female_data)

    #         # 3. Check if an identical match execution history already exists in DB
    #         existing_match = MatchHistory.objects.filter(
    #             male_profile=male_profile, 
    #             female_profile=female_profile
    #         ).first()
            
    #         if existing_match:
    #             response_data = self.format_response(existing_match)
    #             # Store back into Redis cache for subsequent fast reads (1 hour TTL)
    #             cache.set(cache_key, response_data, timeout=3600)
    #             return Response({"source": "database", "data": response_data}, status=status.HTTP_200_OK)

    #         # 4. Perform live calculations since it's a completely new pair query
    #         score, verdict, breakdown = calculate_ashtakoot_match(male_profile, female_profile)
            
    #         # 5. Record the transaction result in MatchHistory
    #         new_match = MatchHistory.objects.create(
    #             male_profile=male_profile,
    #             female_profile=female_profile,
    #             compatibility_score=score,
    #             verdict=verdict,
    #             breakdown=breakdown
    #         )
            
    #         response_data = self.format_response(new_match)
    #         # Seed to Redis cache
    #         cache.set(cache_key, response_data, timeout=3600)
            
    #         return Response({"source": "calculated", "data": response_data}, status=status.HTTP_201_CREATED)

    #     except KeyError as ke:
    #         return Response({"error": f"Missing required field: {str(ke)}"}, status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    def post(self, request):
        """
        Calculation Endpoint: Handles data validation, caching, and matching logic.
        """
        # Replace manual dict checking with DRF Serializer validation
        serializer = KundliMatchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Validated data parses your strings into proper python date/time objects automatically
        validated_data = serializer.validated_data
        male_data = validated_data['male']
        female_data = validated_data['female']

        try:
            # 1. Create a distinct Redis cache key using the birth dates
            cache_key = f"match_{male_data.get('date_of_birth')}_{female_data.get('date_of_birth')}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                return Response({"source": "cache", "data": cached_result}, status=status.HTTP_200_OK)

            # 2. Persist or fetch profiles from PostgreSQL
            male_profile, _ = BirthProfile.objects.get_or_create(gender='M', **male_data)
            female_profile, _ = BirthProfile.objects.get_or_create(gender='F', **female_data)

            # 3. Check if an identical match execution history already exists in DB
            existing_match = MatchHistory.objects.filter(
                male_profile=male_profile, 
                female_profile=female_profile
            ).first()
            
            if existing_match:
                response_data = self.format_response(existing_match)
                cache.set(cache_key, response_data, timeout=3600)
                return Response({"source": "database", "data": response_data}, status=status.HTTP_200_OK)

            # 4. Perform live calculations
            score, verdict, breakdown = calculate_ashtakoot_match(male_profile, female_profile)
            
            # 5. Record the transaction result in MatchHistory
            new_match = MatchHistory.objects.create(
                male_profile=male_profile,
                female_profile=female_profile,
                compatibility_score=score,
                verdict=verdict,
                breakdown=breakdown
            )
            
            response_data = self.format_response(new_match)
            cache.set(cache_key, response_data, timeout=3600)
            
            return Response({"source": "calculated", "data": response_data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        

    def format_response(self, match):
        """Helper function to cleanly format the payload match details"""
        return {
            "compatibility_score": match.compatibility_score,
            "verdict": match.verdict,
            "breakdown": match.breakdown,
            "calculated_at": match.calculated_at
        }