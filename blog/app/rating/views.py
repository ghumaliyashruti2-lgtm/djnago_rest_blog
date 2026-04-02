from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from app.rating.models import Rating
from app.post.models import Post

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rate_post(request):
    post_id = request.data.get("post")
    rating_value = request.data.get("rating")

    post = get_object_or_404(Post, id=post_id)

    rating_obj, created = Rating.objects.update_or_create(
        user=request.user,
        post=post,
        defaults={"rating": rating_value}
    )

    return Response({
        "message": "Submitted Rating",
        "rating": rating_obj.rating
    })