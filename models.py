from dataclasses import dataclass, field
from typing import List, Optional

# Use dataclass decorator to generate boilerplate code for the class
@dataclass
class LinkedImage:
    image_path: str
    link_url: Optional[str] = None
    alt_text: Optional[str] = None
    
@dataclass
class NewsletterSection:
    heading: str
    subheading: Optional[str] = None
    body: str = ""
    anchor_id: str = ""
    images: List[LinkedImage] = field(default_factory=list)