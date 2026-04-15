from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import permissions
from app.like.serializers import ToggleLikeSerializer
from drf_yasg.utils import swagger_auto_schema
from app.permission import IsOwnerOrReadOnly

class ToggleLikeView(GenericAPIView):

    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = ToggleLikeSerializer
    
    @ swagger_auto_schema(
        operation_description= "Like/Unlike Post",
        request_body = ToggleLikeSerializer,
        response = {200:ToggleLikeSerializer,},
        operation_id = "Like"
    )
    def post(self, request, post_id):
        
        serializer = ToggleLikeSerializer(
            data = {"post_id":post_id},
            context={"request":request}
        )
        
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        
        return Response(data)
