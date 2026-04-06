from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from app.rating.serializers import RatingSerializer
from rest_framework.permissions import IsAuthenticated
from app.rating.models import Rating

class RatePostView(GenericAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        
        serializer = RatingSerializer(
            data=request.data,
            context={
                "request":request
            }
        )
        
        serializer.is_valid(raise_exception=True)
        rating=serializer.save()

        return Response({
            "message": "Submitted Rating",
            "rating": rating.rating
        })