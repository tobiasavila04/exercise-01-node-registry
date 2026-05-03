"""
Pydantic schemas for request/response validation.

NodeCreate: for POST body (name, host, port — all required)
NodeUpdate: for PUT body (host, port — optional)
NodeResponse: for API responses (includes id, status, timestamps)
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class NodeCreate(BaseModel):
    name: str
    host: str
    port: int

    @field_validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name must not be empty')
        return v

    @field_validator('host')
    def validate_host(cls, v):
        if not v or not v.strip():
            raise ValueError('Host must not be empty')
        return v

    @field_validator('port')
    def validate_port(cls, v):
        if v < 1 or v > 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v

class NodeUpdate(BaseModel):
    host: Optional[str] = None
    port: Optional[int] = None

    @field_validator('host')
    def validate_host(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Host must not be empty')
        return v

    @field_validator('port')
    def validate_port(cls, v):
        if v is not None and (v < 1 or v > 65535):
            raise ValueError('Port must be between 1 and 65535')
        return v

class NodeResponse(BaseModel):
    id: int
    name: str
    host: str
    port: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
