import json
import logging
import os
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class GeoLookup:
    """Geolocation lookup for IP addresses using geo_ranges.json data."""
    
    def __init__(self):
        self._ip_cache: Dict[str, Dict] = {}
        self._ranges: Dict = {}
        self._private_ranges: Dict = {}
        self._load_geo_data()
    
    def _load_geo_data(self) -> None:
        """Load geo data from JSON file."""
        try:
            data_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data',
                'geo_ranges.json'
            )
            with open(data_file, 'r') as f:
                data = json.load(f)
                self._ranges = data.get('ranges', {})
                self._private_ranges = data.get('private_ranges', {})
                logger.info(f"Loaded {len(self._ranges)} IP range mappings")
        except Exception as e:
            logger.error(f"Failed to load geo data: {e}")
            self._ranges = {}
            self._private_ranges = {}
    
    def lookup(self, ip_address: str) -> Optional[Dict]:
        """Look up geolocation for an IP address."""
        if not ip_address:
            return None
        
        if ip_address in self._ip_cache:
            return self._ip_cache[ip_address]
        
        private_result = self._get_private_ip_result(ip_address)
        if private_result:
            self._ip_cache[ip_address] = private_result
            return private_result
        
        result = self._lookup_by_first_octet(ip_address)
        if result:
            self._ip_cache[ip_address] = result
            return result
        
        logger.warning(f"No geo data found for IP: {ip_address}")
        return None
    
    def _get_private_ip_result(self, ip: str) -> Optional[Dict]:
        """Check if IP is private and return result."""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return None
            
            first = int(parts[0])
            second = int(parts[1])
            
            if first == 10:
                return {'country': 'Private', 'country_name': 'Private Network', 'lat': 0.0, 'lon': 0.0}
            if first == 172 and 16 <= second <= 31:
                return {'country': 'Private', 'country_name': 'Private Network', 'lat': 0.0, 'lon': 0.0}
            if first == 192 and second == 168:
                return {'country': 'Private', 'country_name': 'Private Network', 'lat': 0.0, 'lon': 0.0}
            if first == 127:
                return {'country': 'Local', 'country_name': 'Localhost', 'lat': 0.0, 'lon': 0.0}
            
            return None
        except Exception:
            return None
    
    def _lookup_by_first_octet(self, ip: str) -> Optional[Dict]:
        """Look up country by first octet of IP."""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return None
            
            first_octet = parts[0]
            
            if first_octet in self._ranges:
                data = self._ranges[first_octet]
                return {
                    'country': data.get('country', 'XX'),
                    'country_name': data.get('country_name', 'Unknown'),
                    'lat': data.get('lat', 0.0),
                    'lon': data.get('lon', 0.0),
                }
            
            return None
        except Exception:
            return None


_geo_lookup_instance: Optional[GeoLookup] = None


def get_geo_lookup() -> GeoLookup:
    """Get singleton GeoLookup instance."""
    global _geo_lookup_instance
    if _geo_lookup_instance is None:
        _geo_lookup_instance = GeoLookup()
    return _geo_lookup_instance


def lookup_ip(ip_address: str) -> Optional[Dict]:
    """Convenience function to lookup IP."""
    return get_geo_lookup().lookup(ip_address)