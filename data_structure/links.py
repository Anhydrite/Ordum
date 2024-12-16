from typing import List
from pydantic import BaseModel


class LinkNode(BaseModel):
    node_id: str
    adapter_number: int
    port_number: int


class LinkRequest(BaseModel):
    nodes: List[LinkNode]


class LinkResponse(BaseModel):
    link_id: str
    project_id: str
    nodes: List[LinkNode]
