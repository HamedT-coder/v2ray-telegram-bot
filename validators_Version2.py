from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
import uuid
from logger import setup_logger

logger = setup_logger(__name__)

class VLESSConfig(BaseModel):
    """VLESS protocol configuration"""
    uuid: str = Field(..., alias="id")
    address: str
    port: int
    protocol: str = "vless"
    encryption: str = "none"
    flow: Optional[str] = None
    tls: Optional[str] = None
    sni: Optional[str] = None
    alpn: Optional[str] = None
    network: Optional[str] = "tcp"
    path: Optional[str] = None
    host: Optional[str] = None
    header_type: Optional[str] = Field(None, alias="headerType")
    
    @validator("uuid")
    def validate_uuid(cls, v):
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid UUID format: {v}")
    
    @validator("port")
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError(f"Port must be between 1 and 65535, got {v}")
        return v
    
    class Config:
        allow_population_by_field_name = True


class VMESSConfig(BaseModel):
    """VMess protocol configuration"""
    uuid: str = Field(..., alias="id")
    address: str
    port: int
    protocol: str = "vmess"
    aid: int = 0
    cipher: str = "auto"
    tls: Optional[str] = None
    sni: Optional[str] = None
    network: Optional[str] = "tcp"
    path: Optional[str] = None
    host: Optional[str] = None
    
    @validator("uuid")
    def validate_uuid(cls, v):
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid UUID format: {v}")
    
    @validator("port")
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError(f"Port must be between 1 and 65535, got {v}")
        return v
    
    @validator("aid")
    def validate_aid(cls, v):
        if not (0 <= v <= 65535):
            raise ValueError(f"AlterId must be between 0 and 65535, got {v}")
        return v
    
    class Config:
        allow_population_by_field_name = True


class TROJANConfig(BaseModel):
    """Trojan protocol configuration"""
    password: str
    address: str
    port: int
    protocol: str = "trojan"
    tls: Optional[str] = "tls"
    sni: Optional[str] = None
    alpn: Optional[str] = None
    network: Optional[str] = "tcp"
    path: Optional[str] = None
    host: Optional[str] = None
    
    @validator("password")
    def validate_password(cls, v):
        if len(v) < 4:
            raise ValueError("Password must be at least 4 characters")
        return v
    
    @validator("port")
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError(f"Port must be between 1 and 65535, got {v}")
        return v
    
    class Config:
        allow_population_by_field_name = True


class ShadowsocksConfig(BaseModel):
    """Shadowsocks protocol configuration"""
    method: str
    password: str
    address: str
    port: int
    protocol: str = "ss"
    
    @validator("method")
    def validate_method(cls, v):
        valid_methods = [
            "aes-128-gcm", "aes-256-gcm", "chacha20-poly1305",
            "aes-128-ctr", "aes-192-ctr", "aes-256-ctr",
            "aes-128-cfb", "aes-192-cfb", "aes-256-cfb",
            "chacha20-ietf-poly1305"
        ]
        if v not in valid_methods:
            raise ValueError(f"Invalid method. Supported: {', '.join(valid_methods)}")
        return v
    
    @validator("password")
    def validate_password(cls, v):
        if len(v) < 4:
            raise ValueError("Password must be at least 4 characters")
        return v
    
    @validator("port")
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError(f"Port must be between 1 and 65535, got {v}")
        return v
    
    class Config:
        allow_population_by_field_name = True


class Hysteria1Config(BaseModel):
    """Hysteria 1 protocol configuration"""
    protocol: str = "hy"
    auth_string: str = Field(..., alias="authString")
    address: str
    port: int
    tls: Optional[str] = "tls"
    sni: Optional[str] = None
    alpn: Optional[str] = "h2"
    protocol_string: Optional[str] = Field(None, alias="protocolString")
    
    @validator("port")
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError(f"Port must be between 1 and 65535, got {v}")
        return v
    
    class Config:
        allow_population_by_field_name = True


class Hysteria2Config(BaseModel):
    """Hysteria 2 protocol configuration"""
    protocol: str = "hy2"
    password: str
    address: str
    port: int
    tls: Optional[str] = "tls"
    sni: Optional[str] = None
    alpn: Optional[str] = "h3"
    obfs: Optional[str] = None
    obfs_password: Optional[str] = Field(None, alias="obfsPassword")
    
    @validator("password")
    def validate_password(cls, v):
        if len(v) < 4:
            raise ValueError("Password must be at least 4 characters")
        return v
    
    @validator("port")
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError(f"Port must be between 1 and 65535, got {v}")
        return v
    
    class Config:
        allow_population_by_field_name = True