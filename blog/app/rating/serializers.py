from rest_framework import serializers
from django.shortcuts import get_object_or_404
from app.post.models import Post
from .models import Rating

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'post', 'rating']
        read_only_fields = ['id']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def validate_post(self, value):
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post not found")
        return value
        
    def save(self, **kwargs):
        user = self.context['request'].user
        post = self.validated_data.get('post')
        rating_value = self.validated_data.get('rating')

        rating_obj, create= Rating.objects.update_or_create(
            user=user,
            post=post,
            defaults={"rating": rating_value}
        )

        return rating_obj