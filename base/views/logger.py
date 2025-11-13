# logging_config.py
import logging
import logging.config
import os

os.makedirs("logs", exist_ok=True)

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
        },
    },
    "handlers": {
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": "logs/base.log",
            "maxBytes": 10000,
            "backupCount": 3,
        },
    },
    "loggers": {
        "base": {
            "level": "DEBUG",
            "handlers": ["stderr", "file"],
            "propagate": False
        },
        "": {
            "level": "WARNING",
            "handlers": ["stderr"]
        }
    },
}


logging.config.dictConfig(logging_config)

logger = logging.getLogger("base")
