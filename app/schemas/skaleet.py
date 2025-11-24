from pydantic import BaseModel
from typing import Optional, Dict, Any


class SkaleetCardRequest(BaseModel):
    card_id: str
    action: str
    parameters: Optional[Dict[str, Any]] = None


class SkaleetCardResponse(BaseModel):
    success: bool
    card_id: Optional[str] = None
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

