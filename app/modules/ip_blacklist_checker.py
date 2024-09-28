import socket
import dns.resolver

class IPBlacklistChecker:
    def __init__(self, blacklist_providers=None):
        """
        Initializes the IPBlacklistChecker with a list of DNSBL providers.
        These are commonly used DNS-based blacklists to check if an IP is blacklisted.
        """
        if blacklist_providers is None:
            self.blacklist_providers = [
                'zen.spamhaus.org',
                'bl.spamcop.net',
                'b.barracudacentral.org',
                'dnsbl.sorbs.net',
                'list.dsbl.org'
            ]
        else:
            self.blacklist_providers = blacklist_providers

    def is_blacklisted(self, ip_address):
        """
        Checks if the given IP address is listed in any of the blacklists.
        Returns a dictionary with the status for each blacklist.
        """
        result = {}
        try:
            reversed_ip = self._reverse_ip(ip_address)
            for provider in self.blacklist_providers:
                lookup = f"{reversed_ip}.{provider}"
                try:
                    dns.resolver.resolve(lookup, 'A')
                    result[provider] = 'Blacklisted'
                except dns.resolver.NXDOMAIN:
                    result[provider] = 'Not Listed'
                except dns.resolver.Timeout:
                    result[provider] = 'Timeout'
                except Exception as e:
                    result[provider] = f'Error: {str(e)}'
        except ValueError as e:
            return {"Error": f"Invalid IP address: {str(e)}"}
        return result

    def _reverse_ip(self, ip_address):
        """
        Reverses the IP address for DNSBL lookup.
        For example, 192.168.1.1 becomes 1.1.168.192.
        """
        try:
            socket.inet_aton(ip_address)
        except socket.error:
            raise ValueError("Invalid IP address format.")
        
        return '.'.join(reversed(ip_address.split('.')))
