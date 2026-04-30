from celery import shared_task
from apps.posts.models import Post
from apps.posts.constants import PostStatus
from blog.services.openrouter import OpenRouterClient
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def generate_summary(self, post_id):
    try:
        post = Post.objects.get(id=post_id)

        post.status = PostStatus.PROCESSING
        post.save()

        client = OpenRouterClient()

        summary = client.summarize_post(
            title=post.title,
            content=post.content
        )

        post.summary = summary
        post.status = PostStatus.COMPLETE
        post.save()

    except Exception as e:
        logger.error(f"OpenRouter error: {str(e)}")

        post.status = PostStatus.FAILED
        post.save()

        raise self.retry(exc=e, countdown=10)