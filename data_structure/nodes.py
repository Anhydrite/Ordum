from typing import List, Optional
from pydantic import BaseModel


class Label(BaseModel):
    rotation: int
    style: Optional[str]
    text: str
    x: Optional[int]
    y: Optional[int]


class Port(BaseModel):
    adapter_number: int
    data_link_types: dict
    link_type: str
    name: str
    port_number: int
    short_name: str


class Node(BaseModel):
    command_line: Optional[str]
    compute_id: str
    console: Optional[int]
    console_auto_start: bool
    console_host: str
    console_type: Optional[str]
    custom_adapters: List[dict]
    first_port_name: Optional[str]
    height: int
    label: Label
    locked: bool
    name: str
    node_directory: Optional[str]
    node_id: str
    node_type: str
    port_name_format: str
    port_segment_size: int
    ports: List[Port]
    project_id: str
    properties: dict
    status: str
    symbol: Optional[str]
    template_id: Optional[str]
    width: int
    x: int
    y: int
    z: int


class NodesResponse(BaseModel):
    nodes: List[Node]
