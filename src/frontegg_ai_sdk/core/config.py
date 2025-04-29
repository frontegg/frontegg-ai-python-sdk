from dataclasses import dataclass, field
from typing import Optional, Callable
from .enums import Environment

@dataclass
class FronteggAiClientConfig:
    environment: Environment
    agent_id: str
    client_id: str
    client_secret: str 
