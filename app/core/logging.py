import logging
import sys
import json
from datetime import datetime
from contextvars import ContextVar
from app.core.config import settings

# Context variable pour stocker le correlation_id
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


class JSONFormatter(logging.Formatter):
    """Formateur de logs en JSON"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "level": record.levelname,
            "message": record.getMessage(),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Ajouter correlation_id si présent dans le contexte
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id
        
        # Ajouter des champs supplémentaires passés via extra={}
        # Ces champs sont stockés dans record.__dict__
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName", "relativeCreated",
                "thread", "threadName", "exc_info", "exc_text", "stack_info"
            ]:
                extra_fields[key] = value
        
        if extra_fields:
            log_data.update(extra_fields)
        
        # Ajouter le nom du logger si nécessaire
        if record.name != "root":
            log_data["logger"] = record.name
        
        return json.dumps(log_data)


def setup_logging():
    """Configure le logging avec format JSON"""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Supprimer les handlers existants
    root_logger.handlers = []
    
    # Créer un handler avec le formateur JSON
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)

