import logging
import logging.config


def setup_logging(default_level=logging.INFO, log_config: dict = None):
    if log_config:
        logging.config.dictConfig(log_config)
    else:
        logging.basicConfig(level=default_level)


# logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "standard",
            "level": "DEBUG",
            "filename": "/logs_output/app.log",
        },
    },
    "loggers": {
        "Database": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "MessageBroker": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "AuthEndpoints": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "TasksEndpoints": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "RemindEndpoints": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    }
}

database_logger = logging.getLogger("Database")
auth_logger = logging.getLogger("AuthEndpoints")
tasks_logger = logging.getLogger("TasksEndpoints")
reminder_logger = logging.getLogger("RemindEndpoints")
message_broker_logger = logging.getLogger("RemindEndpoints")
