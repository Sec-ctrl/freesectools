import requests
import ipaddress


class IPGeolocationLookup:
    def __init__(self):
        """
        Initialize the IP Geolocation Lookup tool using freegeoip.app (no API key needed).
        """
        self.base_url = "https://freegeoip.app/json/"

    def valid_ip(self, ip_address):
        """
        Validates if the provided IP address is valid (IPv4 or IPv6) and not private or reserved.
        """
        try:
            ip_obj = ipaddress.ip_address(ip_address)
            if ip_obj.is_private or ip_obj.is_reserved or ip_obj.is_loopback:
                return False
            return True
        except ValueError:
            return False

    def lookup(self, ip_address):
        """
        Perform a precise IP geolocation lookup using the freegeoip.app API.
        Returns a dictionary with detailed geolocation data if successful, or an error message.
        """
        if not self.valid_ip(ip_address):
            return {"Error": "Invalid or restricted IP address."}

        url = f"{self.base_url}{ip_address}"

        try:
            response = requests.get(url, timeout=5)  # Timeout after 5 seconds
            if response.status_code == 200:
                return self._format_response(response.json())
            else:
                return {
                    "Error": f"Failed to retrieve data for {ip_address}. Status code: {response.status_code}"
                }
        except requests.Timeout:
            return {"Error": "The request timed out."}
        except requests.RequestException as e:
            return {"Error": f"An error occurred during the request: {e}"}

    def _format_response(self, data):
        """
        Format the geolocation data to make it more readable.
        """
        return {
            "IP": data.get("ip", "N/A"),
            "Country": data.get("country_name", "N/A"),
            "Region": data.get("region_name", "N/A"),
            "City": data.get("city", "N/A"),
            "Latitude": data.get("latitude", "N/A"),
            "Longitude": data.get("longitude", "N/A"),
            "Timezone": data.get("time_zone", "N/A"),
            "Postal Code": data.get("zip_code", "N/A"),
            "Metro Code": data.get("metro_code", "N/A"),
        }
