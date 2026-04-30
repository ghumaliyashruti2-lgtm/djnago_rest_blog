class PostStatus:
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    COMPLETE = "complete"

    CHOICES = [
        (PROCESSING, "Processing"),
        (PUBLISHED, "Published"),
        (FAILED, "Failed"),
        (COMPLETE, "Complete")
    ]