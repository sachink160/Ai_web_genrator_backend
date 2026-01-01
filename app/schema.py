from pydantic import BaseModel
from typing import Dict, Optional


class GeneratePromptsRequest(BaseModel):
    description: str

class PromptsResponse(BaseModel):
    prompts: Dict[str, str]

class GenerateImagesRequest(BaseModel):
    prompts: Optional[Dict[str, str]] = None

class ImagesResponse(BaseModel):
    images: Dict[str, str]

class GenerateHTMLRequest(BaseModel):
    description: str
    images: Dict[str, str]
    template: Optional[str] = None

class HTMLResponse(BaseModel):
    html: str
    css: str

class EditHTMLRequest(BaseModel):
    html: str
    css: str
    edit_request: str

class EditHTMLResponse(BaseModel):
    html: str
    css: str


# New schemas for LangGraph workflow

class GenerateWebsiteRequest(BaseModel):
    description: str

class WebsitePlanResponse(BaseModel):
    plan: Dict
    status: str
    progress: int
    progress_message: str

class WebsiteGenerationResponse(BaseModel):
    pages: Dict[str, Dict[str, str]]  # page_name -> {html: str, css: str}
    image_urls: Dict[str, str]  # section_name -> image_url
    plan: Dict
    status: str
    progress: int
    progress_message: str
