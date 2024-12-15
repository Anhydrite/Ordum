from typing import Dict, List, Optional
from pydantic import BaseModel


class Project(BaseModel):
    project_id: str
    name: str
    status: str
    path: str
    auto_close: bool
    scene_height: int
    scene_width: int
    show_grid: bool
    show_interface_labels: bool
    show_layers: bool
    snap_to_grid: bool
    supplier: Optional[str]
    type: Optional[str] = None
    zoom: float


class ProjectsResponse(BaseModel):
    projects: List[Project]


class LoadProjectResponse(BaseModel):
    project_id: str
    name: Optional[str]
    path: Optional[str]
    filename: Optional[str]
    auto_close: bool
    auto_open: bool
    auto_start: bool
    drawing_grid_size: Optional[int]
    grid_size: Optional[int]
    scene_width: int
    scene_height: int
    show_grid: bool
    show_interface_labels: bool
    show_layers: bool
    snap_to_grid: bool
    status: str
    supplier: Optional[Dict]
    variables: Optional[List]
    zoom: int
