from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from apps.ratings.serializers import RatingSerializer
from rest_framework.permissions import IsAuthenticated
from apps.ratings.models import Rating
from apps.posts.models import Post
from blog.permission import IsOwnerOrReadOnly
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger(__name__)

class RatePostView(GenericAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated,IsOwnerOrReadOnly]

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
            "message": "Rating submitted successfully",
            "rating": rating.rating
        }, status=status.HTTP_200_OK)
        
        
    @swagger_auto_schema(
    operation_id="Update Rating",
    request_body=RatingSerializer,
    responses={200: RatingSerializer}
    )
    def put(self, request, *args, **kwargs):
        serializer = RatingSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        rating = serializer.save()

        return Response({
            "message": "Rating updated successfully",
            "rating": rating.rating
        }, status=status.HTTP_200_OK)
                
            
    @swagger_auto_schema(
        operation_id="Delete Rating",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["post"],
            properties={
                "post": openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={
            200: openapi.Response("Rating deleted successfully"),
            404: openapi.Response("Rating not found")
        }
    )
    
    
    def delete(self, request, *args, **kwargs):
        post_id = request.data.get("post") 
        post = get_object_or_404(Post, id=post_id)
        print (post)
        if post_id is None:
            logger.error(f"user {request.user.username} not provide any post id for delete rating ")
        else:
            if post.user != request.user:
                logger.debug(f"user {request.user.username} provide post id {post_id} for delete rating ")
            else:
                logger.debug(f"user {request.user.username} provide post id {post_id} for delete own rating ")
            
        rating = Rating.objects.filter(
            user=request.user,
            post_id=post_id
        ).first()

        if not rating:
            logger.error(f"user {request.user.username} not provide rating value ")
            return Response({
                "message": "Rating not found"
            }, status=status.HTTP_404_NOT_FOUND)
        else:
            if post.user != request.user:
                logger.debug(f"user {request.user.username} try to delete rating value {rating.rating} on post id {post_id} ")
            else:
                logger.debug(f"user {request.user.username} try to delete own rating value {rating.rating} on post id {post_id} ")
            rating.delete()

            return Response({
                "message": "Rating deleted successfully"
            }, status=status.HTTP_200_OK)