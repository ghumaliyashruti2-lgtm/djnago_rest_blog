from celery import shared_task
from apps.posts.models import Post
import time
from blog.blog.services.openrouter import OpenRouterClient
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def generate_summary(self, post_id):
    try:
        post = Post.objects.get(id=post_id)

        post.status = "processing"
        post.save()

        client = OpenRouterClient()

        summary = client.summarize_post(
            title=post.title,
            content=post.content
        )

        post.summary = summary
        post.status = "completed"
        post.save()

    except Exception as e:
        logger.error(f"OpenRouter error: {str(e)}")

        post.status = "failed"
        post.save()

        raise self.retry(exc=e, countdown=10)