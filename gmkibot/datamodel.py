import uuid
import hashlib
from datetime import datetime
from typing import Any, Callable, Dict, List, Literal, Optional, Union
from pydantic.dataclasses import dataclass
from dataclasses import asdict, field
from enum import Enum

@dataclass
class Member(object):
    """Data model for Members"""

    id: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    timestamp: Optional[str] = None

    tags: Optional[List[str]] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def dict(self):
        result = asdict(self)
        return result

