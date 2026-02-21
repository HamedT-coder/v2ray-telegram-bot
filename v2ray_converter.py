import base64
import json
from typing import Dict, Any, Optional
from urllib.parse import urlencode, quote
from validators import (
    VLESSConfig, VMESSConfig, TROJANConfig, 
    ShadowsocksConfig, Hysteria1Config, Hysteria2Config
)
from logger import setup_logger

logger = setup_logger(__name__)


class V2RayConverter:
    """Convert JSON configurations to V2Ray protocol URIs"""
    
    def __init__(self):
        self.protocol_handlers = {
            "vless": self.convert_vless,
            "vmess": self.convert_vmess,
            "trojan": self.convert_trojan,
            "ss": self.convert_shadowsocks,
            "shadowsocks": self.convert_shadowsocks,
            "hy": self.convert_hysteria1,
            "hysteria": self.convert_hysteria1,
            "hy2": self.convert_hysteria2,
            "hysteria2": self.convert_hysteria2,
        }
    
    def convert(self, json_config: str, name: str = "V2Ray Server") -> str:
        """
        Convert JSON configuration to V2Ray URI
        
        Args:
            json_config: JSON string containing protocol configuration
            name: Name/remark for the server
        
        Returns:
            V2Ray URI string
        
        Raises:
            ValueError: If protocol is unsupported or config is invalid
            json.JSONDecodeError: If JSON is malformed
        """
        try:
            config = json.loads(json_config)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            raise ValueError(f"Invalid JSON format: {e}")
        
        protocol = config.get("protocol", "").lower()
        
        if protocol not in self.protocol_handlers:
            raise ValueError(
                f"Unsupported protocol: {protocol}. "
                f"Supported: {', '.join(self.protocol_handlers.keys())}"
            )
        
        try:
            handler = self.protocol_handlers[protocol]
            uri = handler(config, name)
            logger.info(f"Successfully converted {protocol} config")
            return uri
        except Exception as e:
            logger.error(f"Conversion error for {protocol}: {e}")
            raise ValueError(f"Configuration validation error: {e}")
    
    def convert_vless(self, config: Dict[str, Any], name: str) -> str:
        """Convert VLESS JSON to vless:// URI"""
        try:
            vless_config = VLESSConfig(**config)
            
            # Build userinfo: UUID
            userinfo = vless_config.uuid
            
            # Build server part: address:port
            server = f"{vless_config.address}:{vless_config.port}"
            
            # Build query parameters
            params = {
                "encryption": vless_config.encryption,
                "type": vless_config.network or "tcp",
            }
            
            if vless_config.tls:
                params["security"] = vless_config.tls
            
            if vless_config.sni:
                params["sni"] = vless_config.sni
            
            if vless_config.flow:
                params["flow"] = vless_config.flow
            
            if vless_config.alpn:
                params["alpn"] = vless_config.alpn
            
            if vless_config.path:
                params["path"] = vless_config.path
            
            if vless_config.host:
                params["host"] = vless_config.host
            
            if vless_config.header_type:
                params["headerType"] = vless_config.header_type
            
            query_string = urlencode(params)
            uri = f"vless://{userinfo}@{server}?{query_string}#{quote(name)}"
            
            return uri
        except Exception as e:
            logger.error(f"VLESS conversion error: {e}")
            raise
    
    def convert_vmess(self, config: Dict[str, Any], name: str) -> str:
        """Convert VMess JSON to vmess:// URI (base64 encoded)"""
        try:
            vmess_config = VMESSConfig(**config)
            
            vmess_obj = {
                "v": "2",
                "ps": name,
                "add": vmess_config.address,
                "port": vmess_config.port,
                "id": vmess_config.uuid,
                "aid": vmess_config.aid,
                "net": vmess_config.network or "tcp",
                "type": vmess_config.header_type or "none",
                "tls": vmess_config.tls or "",
                "sni": vmess_config.sni or "",
            }
            
            if vmess_config.path:
                vmess_obj["path"] = vmess_config.path
            
            if vmess_config.host:
                vmess_obj["host"] = vmess_config.host
            
            if vmess_config.cipher:
                vmess_obj["cipher"] = vmess_config.cipher
            
            json_str = json.dumps(vmess_obj, separators=(',', ':'))
            encoded = base64.b64encode(json_str.encode()).decode()
            
            return f"vmess://{encoded}"
        except Exception as e:
            logger.error(f"VMess conversion error: {e}")
            raise
    
    def convert_trojan(self, config: Dict[str, Any], name: str) -> str:
        """Convert Trojan JSON to trojan:// URI"""
        try:
            trojan_config = TROJANConfig(**config)
            
            # Build userinfo: password
            userinfo = trojan_config.password
            
            # Build server part: address:port
            server = f"{trojan_config.address}:{trojan_config.port}"
            
            # Build query parameters
            params = {
                "type": trojan_config.network or "tcp",
            }
            
            if trojan_config.tls:
                params["security"] = trojan_config.tls
            
            if trojan_config.sni:
                params["sni"] = trojan_config.sni
            
            if trojan_config.alpn:
                params["alpn"] = trojan_config.alpn
            
            if trojan_config.path:
                params["path"] = trojan_config.path
            
            if trojan_config.host:
                params["host"] = trojan_config.host
            
            query_string = urlencode(params)
            uri = f"trojan://{userinfo}@{server}?{query_string}#{quote(name)}"
            
            return uri
        except Exception as e:
            logger.error(f"Trojan conversion error: {e}")
            raise
    
    def convert_shadowsocks(self, config: Dict[str, Any], name: str) -> str:
        """Convert Shadowsocks JSON to ss:// URI"""
        try:
            ss_config = ShadowsocksConfig(**config)
            
            # Build userinfo: method:password (base64 encoded)
            userinfo_plain = f"{ss_config.method}:{ss_config.password}"
            userinfo = base64.b64encode(userinfo_plain.encode()).decode()
            
            # Build server part: address:port
            server = f"{ss_config.address}:{ss_config.port}"
            
            uri = f"ss://{userinfo}@{server}#{quote(name)}"
            
            return uri
        except Exception as e:
            logger.error(f"Shadowsocks conversion error: {e}")
            raise
    
    def convert_hysteria1(self, config: Dict[str, Any], name: str) -> str:
        """Convert Hysteria 1 JSON to hysteria:// URI"""
        try:
            hy_config = Hysteria1Config(**config)
            
            # Build userinfo: auth_string
            userinfo = quote(hy_config.auth_string)
            
            # Build server part: address:port
            server = f"{hy_config.address}:{hy_config.port}"
            
            # Build query parameters
            params = {}
            
            if hy_config.tls:
                params["tls"] = "1"
            
            if hy_config.sni:
                params["sni"] = hy_config.sni
            
            if hy_config.alpn:
                params["alpn"] = hy_config.alpn
            
            if hy_config.protocol_string:
                params["protocol"] = hy_config.protocol_string
            
            query_string = urlencode(params) if params else ""
            uri = f"hysteria://{userinfo}@{server}"
            if query_string:
                uri += f"?{query_string}"
            uri += f"#{quote(name)}"
            
            return uri
        except Exception as e:
            logger.error(f"Hysteria 1 conversion error: {e}")
            raise
    
    def convert_hysteria2(self, config: Dict[str, Any], name: str) -> str:
        """Convert Hysteria 2 JSON to hy2:// URI"""
        try:
            hy2_config = Hysteria2Config(**config)
            
            # Build userinfo: password
            userinfo = quote(hy2_config.password)
            
            # Build server part: address:port
            server = f"{hy2_config.address}:{hy2_config.port}"
            
            # Build query parameters
            params = {}
            
            if hy2_config.tls:
                params["tls"] = "1"
            
            if hy2_config.sni:
                params["sni"] = hy2_config.sni
            
            if hy2_config.alpn:
                params["alpn"] = hy2_config.alpn
            
            if hy2_config.obfs:
                params["obfs"] = hy2_config.obfs
            
            if hy2_config.obfs_password:
                params["obfs-password"] = hy2_config.obfs_password
            
            query_string = urlencode(params) if params else ""
            uri = f"hy2://{userinfo}@{server}"
            if query_string:
                uri += f"?{query_string}"
            uri += f"#{quote(name)}"
            
            return uri
        except Exception as e:
            logger.error(f"Hysteria 2 conversion error: {e}")
            raise