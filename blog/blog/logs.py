import logging.config
import logging
from django.conf import settings
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {pathname} [lineno:{lineno}]  {message} ",
            "style": "{",
        },
    },

    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": str(settings.BASE_DIR / "loggings.log"),
            "formatter": "verbose",
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
        },
    },

    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },
}

logging.config.dictConfig(LOGGING)

'''
    "formatters": {
        "standard": {
            "format": "{levelname} {name} {lineno} {pathname} {funcname} {filename} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {lineno} {asctime} {module} {message}",
            "style": "{",
        },
    },
'''