import hashlib
import requests


class DataBreachChecker:
    def __init__(
        self, hibp_passwords_api_url: str = "https://api.pwnedpasswords.com/range/"
    ):
        self.hibp_passwords_api_url = hibp_passwords_api_url

    def _get_sha1_hash(self, password: str) -> str:
        """
        Hash the password using SHA-1.
        """
        sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        return sha1

    def check_password_breach(self, password: str) -> int:
        """
        Check if the given password has been part of any data breaches.
        Returns the count of times the password has been found in breaches.
        """
        # Get the SHA-1 hash of the password
        sha1_hash = self._get_sha1_hash(password)
        prefix, suffix = sha1_hash[:5], sha1_hash[5:]

        try:
            # Make a request to the HIBP API using the first 5 characters of the hash
            response = requests.get(f"{self.hibp_passwords_api_url}{prefix}")
            if response.status_code == 200:
                # Search for the hash suffix in the response
                hashes = (line.split(":") for line in response.text.splitlines())
                for hash_suffix, count in hashes:
                    if hash_suffix == suffix:
                        return int(
                            count
                        )  # Return the count of how many times the password was found
                return 0  # Password not found
            else:
                raise Exception(
                    f"Error: Unable to fetch data (Status Code: {response.status_code})"
                )
        except requests.RequestException as e:
            raise Exception(f"Error: {e}")
