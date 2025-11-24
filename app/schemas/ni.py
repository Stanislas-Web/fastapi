from pydantic import BaseModel
from typing import Optional, Dict, Any


class NIRequest(BaseModel):
    card_id: str
    action: str
    metadata: Optional[Dict[str, Any]] = None


class NIResponse(BaseModel):
    success: bool
    status: str
    details: Optional[Dict[str, Any]] = None

