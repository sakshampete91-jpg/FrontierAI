import ipaddress
import socket
from urllib.parse import urlparse


class URLSecurity:
    """Basic SSRF protection for FrontierAI web requests."""

    ALLOWED_SCHEMES = {
        "http",
        "https",
    }

    BLOCKED_HOSTNAMES = {
        "localhost",
        "localhost.localdomain",
    }

    def validate(self, url: str) -> None:
        url = url.strip()

        if not url:
            raise ValueError(
                "URL cannot be empty."
            )

        parsed = urlparse(url)

        if parsed.scheme.lower() not in self.ALLOWED_SCHEMES:
            raise ValueError(
                "Only HTTP and HTTPS URLs are allowed."
            )

        hostname = parsed.hostname

        if not hostname:
            raise ValueError(
                "URL must contain a hostname."
            )

        hostname = hostname.lower()

        if hostname in self.BLOCKED_HOSTNAMES:
            raise ValueError(
                "Localhost URLs are blocked."
            )

        if hostname == "localhost":
            raise ValueError(
                "Localhost URLs are blocked."
            )

        if self._is_ip_address(hostname):
            ip = ipaddress.ip_address(hostname)

            if self._is_private_or_local(ip):
                raise ValueError(
                    "Private or local IP addresses are blocked."
                )

            return

        try:
            addresses = socket.getaddrinfo(
                hostname,
                None,
            )
        except socket.gaierror as exc:
            raise ValueError(
                "Hostname could not be resolved."
            ) from exc

        for address in addresses:
            ip_text = address[4][0]

            try:
                ip = ipaddress.ip_address(
                    ip_text
                )
            except ValueError:
                continue

            if self._is_private_or_local(ip):
                raise ValueError(
                    "Hostname resolves to a private or local IP."
                )

    def _is_ip_address(
        self,
        hostname: str,
    ) -> bool:
        try:
            ipaddress.ip_address(
                hostname
            )
            return True
        except ValueError:
            return False

    def _is_private_or_local(
        self,
        ip: ipaddress.IPv4Address
        | ipaddress.IPv6Address,
    ) -> bool:
        return any(
            [
                ip.is_private,
                ip.is_loopback,
                ip.is_link_local,
                ip.is_reserved,
                ip.is_multicast,
                ip.is_unspecified,
            ]
        )