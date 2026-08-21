import sys
import structlog
from structlog.stdlib import add_log_level, add_logger_name
from structlog.processors import TimeStamper, JSONRenderer, CallsiteParameterAdder
from structlog.contextvars import merge_contextvars


def configure_logging():
    structlog.configure(
        processors=[
            merge_contextvars,
            add_logger_name,
            add_log_level,
            TimeStamper(fmt="iso", utc=True),
            CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                ]
            ),
            structlog.processors.format_exc_info,
            JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(20),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None):
    return structlog.get_logger(name)