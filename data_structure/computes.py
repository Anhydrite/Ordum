from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ComputeInput(BaseModel):
    compute_id: Optional[str]
    host: str
    name: Optional[str]
    password: Optional[str]
    port: int
    protocol: str
    user: Optional[str]


class ComputeOutput(BaseModel):
    capabilities: Dict[str, Any]
    compute_id: str
    connected: bool
    cpu_usage_percent: Optional[float]
    host: str
    last_error: Optional[str]
    memory_usage_percent: Optional[float]
    name: str
    port: int
    protocol: str
    user: Optional[str]


class ComputesResponse(BaseModel):
    computes: List[ComputeOutput]
