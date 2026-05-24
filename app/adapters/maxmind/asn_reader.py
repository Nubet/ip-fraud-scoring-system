from ipaddress import ip_address

import geoip2.database
from geoip2.errors import AddressNotFoundError

from app.domain.interfaces import IPNetworkRepository

HOSTING_MARKERS = frozenset(
    {
        "DIGITALOCEAN",
        "AMAZON",
        "AWS",
        "GOOGLE",
        "MICROSOFT",
        "OVH",
        "HETZNER",
        "VULTR",
        "LINODE",
        "ORACLE CLOUD",
        "CLOUDFLARE",
    }
)


class MaxMindASNReader(IPNetworkRepository):
    def __init__(self, db_path: str | None):
        self.db_path = db_path
        self._reader: geoip2.database.Reader | None = None
        if db_path:
            try:
                self._reader = geoip2.database.Reader(db_path)
            except OSError:
                self._reader = None

    async def is_data_center(self, ip: str) -> bool:
        if self._reader is None:
            return False

        try:
            ip_address(ip)
            asn_response = self._reader.asn(ip)
            org = (asn_response.autonomous_system_organization or "").upper()
        except (ValueError, AddressNotFoundError):
            return False

        return any(marker in org for marker in HOSTING_MARKERS)
