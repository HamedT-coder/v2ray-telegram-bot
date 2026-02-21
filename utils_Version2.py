import json
import re
from typing import Dict, Any, Tuple, Optional
from logger import setup_logger

logger = setup_logger(__name__)


class JSONValidator:
    """Utility class for JSON validation and formatting"""
    
    @staticmethod
    def is_valid_json(json_string: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if string is valid JSON
        
        Args:
            json_string: String to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            json.loads(json_string)
            return True, None
        except json.JSONDecodeError as e:
            return False, str(e)
    
    @staticmethod
    def format_json(json_string: str, indent: int = 2) -> str:
        """
        Format JSON string with proper indentation
        
        Args:
            json_string: JSON string to format
            indent: Number of spaces for indentation
        
        Returns:
            Formatted JSON string
        
        Raises:
            json.JSONDecodeError: If JSON is invalid
        """
        obj = json.loads(json_string)
        return json.dumps(obj, indent=indent)
    
    @staticmethod
    def minify_json(json_string: str) -> str:
        """
        Minify JSON (remove whitespace)
        
        Args:
            json_string: JSON string to minify
        
        Returns:
            Minified JSON string
        
        Raises:
            json.JSONDecodeError: If JSON is invalid
        """
        obj = json.loads(json_string)
        return json.dumps(obj, separators=(',', ':'))


class StringValidator:
    """Utility class for string validation"""
    
    @staticmethod
    def is_valid_domain(domain: str) -> bool:
        """
        Validate domain name format
        
        Args:
            domain: Domain name to validate
        
        Returns:
            True if valid, False otherwise
        """
        domain_pattern = r'^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$'
        return bool(re.match(domain_pattern, domain.lower()))
    
    @staticmethod
    def is_valid_ip(ip_address: str) -> bool:
        """
        Validate IPv4 or IPv6 address
        
        Args:
            ip_address: IP address to validate
        
        Returns:
            True if valid, False otherwise
        """
        # IPv4 pattern
        ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        
        # IPv6 pattern (simplified)
        ipv6_pattern = r'^(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4})$'
        
        return bool(re.match(ipv4_pattern, ip_address)) or bool(re.match(ipv6_pattern, ip_address))
    
    @staticmethod
    def is_valid_hostname(hostname: str) -> bool:
        """
        Validate hostname (domain or IP)
        
        Args:
            hostname: Hostname to validate
        
        Returns:
            True if valid, False otherwise
        """
        return StringValidator.is_valid_domain(hostname) or StringValidator.is_valid_ip(hostname)
    
    @staticmethod
    def is_valid_uuid(uuid_string: str) -> bool:
        """
        Validate UUID format
        
        Args:
            uuid_string: UUID string to validate
        
        Returns:
            True if valid, False otherwise
        """
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, uuid_string.lower()))
    
    @staticmethod
    def is_valid_port(port: int) -> bool:
        """
        Validate port number
        
        Args:
            port: Port number to validate
        
        Returns:
            True if valid, False otherwise
        """
        return isinstance(port, int) and 1 <= port <= 65535
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 100) -> str:
        """
        Sanitize string by removing unwanted characters
        
        Args:
            text: String to sanitize
            max_length: Maximum allowed length
        
        Returns:
            Sanitized string
        """
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        # Limit length
        return text[:max_length].strip()


class ConfigAnalyzer:
    """Utility class for analyzing V2Ray configurations"""
    
    @staticmethod
    def extract_protocol(config: Dict[str, Any]) -> Optional[str]:
        """
        Extract protocol from configuration
        
        Args:
            config: Configuration dictionary
        
        Returns:
            Protocol string or None
        """
        protocol = config.get("protocol", "").lower()
        return protocol if protocol else None
    
    @staticmethod
    def get_required_fields(protocol: str) -> list:
        """
        Get required fields for a specific protocol
        
        Args:
            protocol: Protocol name
        
        Returns:
            List of required field names
        """
        required_fields = {
            "vless": ["protocol", "uuid", "address", "port"],
            "vmess": ["protocol", "uuid", "address", "port"],
            "trojan": ["protocol", "password", "address", "port"],
            "ss": ["protocol", "method", "password", "address", "port"],
            "shadowsocks": ["protocol", "method", "password", "address", "port"],
            "hy": ["protocol", "authString", "address", "port"],
            "hysteria": ["protocol", "authString", "address", "port"],
            "hy2": ["protocol", "password", "address", "port"],
            "hysteria2": ["protocol", "password", "address", "port"],
        }
        return required_fields.get(protocol.lower(), [])
    
    @staticmethod
    def validate_required_fields(config: Dict[str, Any], protocol: str) -> Tuple[bool, list]:
        """
        Check if all required fields are present in configuration
        
        Args:
            config: Configuration dictionary
            protocol: Protocol name
        
        Returns:
            Tuple of (is_valid, missing_fields)
        """
        required = ConfigAnalyzer.get_required_fields(protocol)
        missing = [field for field in required if field not in config]
        return len(missing) == 0, missing
    
    @staticmethod
    def get_config_summary(config: Dict[str, Any]) -> str:
        """
        Generate a summary of configuration
        
        Args:
            config: Configuration dictionary
        
        Returns:
            Summary string
        """
        protocol = config.get("protocol", "unknown").upper()
        address = config.get("address", "N/A")
        port = config.get("port", "N/A")
        
        return f"{protocol} - {address}:{port}"


class RateLimiter:
    """Simple rate limiter for user requests"""
    
    def __init__(self):
        self.user_requests: Dict[int, list] = {}
    
    def add_request(self, user_id: int) -> None:
        """
        Record a user request with timestamp
        
        Args:
            user_id: Telegram user ID
        """
        import time
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        self.user_requests[user_id].append(time.time())
    
    def is_rate_limited(self, user_id: int, max_requests: int = 30, time_window: int = 60) -> bool:
        """
        Check if user is rate limited
        
        Args:
            user_id: Telegram user ID
            max_requests: Maximum requests allowed
            time_window: Time window in seconds
        
        Returns:
            True if rate limited, False otherwise
        """
        import time
        current_time = time.time()
        
        if user_id not in self.user_requests:
            return False
        
        # Clean old requests
        cutoff_time = current_time - time_window
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if req_time > cutoff_time
        ]
        
        # Check if exceeded
        is_limited = len(self.user_requests[user_id]) >= max_requests
        return is_limited
    
    def cleanup_old_users(self, max_users: int = 1000) -> None:
        """
        Cleanup old users to prevent memory leak
        
        Args:
            max_users: Maximum users to keep in memory
        """
        if len(self.user_requests) > max_users:
            import time
            current_time = time.time()
            # Remove users with no recent requests
            self.user_requests = {
                uid: reqs for uid, reqs in self.user_requests.items()
                if any(req > current_time - 3600 for req in reqs)  # Keep if any request in last hour
            }