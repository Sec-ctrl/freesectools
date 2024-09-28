import requests
import re
from typing import Optional

class MACAddressLookup:
    def __init__(self, api_url: str = "https://api.macvendors.com/"):
        self.api_url = api_url

    def _validate_mac(self, mac_address: str) -> Optional[str]:
        """
        Validate and normalize the MAC address.
        Returns the normalized MAC address in uppercase without separators if valid, else None.
        """
        # Remove common MAC address separators
        mac_address = re.sub(r'[-:.]', '', mac_address).upper()

        # Validate the MAC address (should be 12 hex digits)
        if re.match(r'^[0-9A-F]{12}$', mac_address):
            return mac_address
        return None

    def _get_mac_type(self, mac_address: str) -> dict:
        """
        Get additional information about the MAC address:
        - Unicast or Multicast
        - Universally or Locally Administered
        """
        first_octet = int(mac_address[:2], 16)
        is_multicast = (first_octet & 1) == 1
        is_locally_administered = (first_octet & 2) == 2

        return {
            "unicast_multicast": "Multicast" if is_multicast else "Unicast",
            "local_universal": "Locally Administered" if is_locally_administered else "Universally Administered"
        }

    def lookup(self, mac_address: str) -> dict:
        """
        Look up the manufacturer information and additional details for a given MAC address using an online API.
        Returns a dictionary with all the data.
        """
        normalized_mac = self._validate_mac(mac_address)
        if not normalized_mac:
            return {"error": "Invalid MAC address format."}

        # Get unicast/multicast and local/universal information
        mac_info = self._get_mac_type(normalized_mac)

        # Make a request to the MAC vendors API
        try:
            response = requests.get(f"{self.api_url}/{normalized_mac}")
            if response.status_code == 200:
                mac_info["manufacturer"] = response.text
            elif response.status_code == 404:
                mac_info["manufacturer"] = "Manufacturer not found."
            else:
                mac_info["error"] = f"Error: Unable to fetch data (Status Code: {response.status_code})"
        except requests.RequestException as e:
            mac_info["error"] = f"Error: {e}"

        return mac_info

# Usage example:
# Create an instance of the lookup class
mac_lookup = MACAddressLookup()

# Perform a lookup
result = mac_lookup.lookup('04-D1-3A-41-92-50')
print(result)  # Output will include additional MAC address information
