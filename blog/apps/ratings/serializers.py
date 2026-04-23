from rest_framework import serializers
from django.shortcuts import get_object_or_404
from apps.posts.models import Post
from apps.follows.models import Follow
from apps.ratings.models import Rating
from apps.notifications.views import NotificationType, create_notification
import logging
logger = logging.getLogger(__name__)

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'post', 'rating']
        read_only_fields = ['id']

    def validate_rating(self, value):
        request = self.context["request"]
        logger.debug(f"Validating rating value={value} by user {request.user}")

        if value < 1 or value > 5:
            logger.error(f"user {self.user} try to import Invalid rating value: {value}")
            raise serializers.ValidationError("Rating must be between 1 and 5")

        return value

    def validate_post(self, value):
        if not Post.objects.filter(id=value.id).exists():
            logger.error(f"user {self.user} try to fetch post {id} is not found")
            raise serializers.ValidationError("Post not found")
        return value
        
    def save(self, **kwargs):
        user = self.context['request'].user
        post = self.validated_data.get('post')
        rating_value = self.validated_data.get('rating')
        
        if post.user == user:
            logger.debug(
            f"User {user.username} import rating value {rating_value} on own post {post.id}"
            )
        else:
            logger.debug(
                f"User {user.username} import rating value {rating_value} on post {post.id}  "
            )
            
        if post.user != user:
            if post.user.is_private:
                is_following = Follow.objects.filter(
                    follower=user,
                    following=post.user
                ).exists()

                if not is_following:
                    logger.error(f"user{user.username} is Unauthorized for attempt rating on post={post.id}")
                    raise serializers.ValidationError("Account is private")


        rating_obj, created = Rating.objects.update_or_create(
            user=user,
            post=post,
            defaults={"rating": rating_value}
        )
        
        if post.user == user :
            if created:
                logger.info(
                    f"user {user.username} is successfully created Rating {rating_value} on own post={post.id} "
                )
            else:
                logger.info(
                    f"user {user.username} is successfully updated Rating with value {rating_value} on own post={post.id}"
                )
        else:
            if created:
                logger.info(
                    f"user {user.username} is successfully created Rating {rating_value} on post={post.id} "
                )
            else:
                logger.info(
                    f"user {user.username} is successfully updated Rating with value {rating_value} on post={post.id}"
                )

        
        if post.user != user:
            create_notification(
                user=post.user,
                sender=user,
                type=NotificationType.RATING
            )
            logger.info(
                f"Rating notification sent: from user={user.username} to user={post.user.username}"
            )
        return rating_obj
    
    