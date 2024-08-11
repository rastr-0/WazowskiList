import logging
import logging.config


# class SensitiveDataFilter(logging.Filter):
#    def __init__(self, sensitive_words):
#        super().__init__()
#        self.sensitive_words = sensitive_words

#    def filter(self, record: LogRecord):
#        message = record.getMessage()
#        for word in self.sensitive_words:
#            message = message.replace(word, "*" * len(word))
#        record.msg = message


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
            "filename": "app.log",
        },
    },
    "loggers": {
        "Database": {
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
    }
}

database_logger = logging.getLogger("Database")
auth_logger = logging.getLogger("AuthEndpoints")
tasks_logger = logging.getLogger("TasksEndpoints")
