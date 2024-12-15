from optparse import Option
from typing import List, Optional
from pydantic import BaseModel


class Template(BaseModel):
    template_id: str
    name: str
    category: str
    compute_id: Optional[str]
    default_name_format: str
    template_type: str
    builtin: bool
    image_type: Optional[str] = None


class TemplatesResponse(BaseModel):
    templates: List[Template]
