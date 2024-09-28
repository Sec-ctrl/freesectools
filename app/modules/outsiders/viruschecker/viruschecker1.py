import hashlib
import requests
import os
from datetime import datetime
import time

class VirusChecker:
    def __init__(self, malwarebazaar_api_key, malshare_api_key=None, hash_algorithms=None):
        """
        Initializes the VirusChecker with API keys for MalwareBazaar and MalShare.

        :param malwarebazaar_api_key: The API key for MalwareBazaar.
        :param malshare_api_key: The API key for MalShare (optional).
        :param hash_algorithms: A list of hash algorithms to use (e.g., ['sha256', 'md5']). Defaults to ['sha256'].
        """
        if not malwarebazaar_api_key:
            raise ValueError("MalwareBazaar API key must be provided")
        
        self.malwarebazaar_api_key = malwarebazaar_api_key
        self.malshare_api_key = malshare_api_key
        self.hash_algorithms = hash_algorithms or ['sha256']
        self.cache = {}  # In-memory cache for hash lookups

    def _hash_file(self, file_path, algorithm):
        """
        Calculates the hash of a file using the specified algorithm.

        :param file_path: The path to the file.
        :param algorithm: The hash algorithm to use.
        :return: The hash as a hexadecimal string.
        """
        try:
            hash_func = hashlib.new(algorithm)
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    hash_func.update(byte_block)
            return hash_func.hexdigest()
        except (OSError, IOError, ValueError):
            return None

    def calculate_hashes(self, file_path):
        """
        Calculates the specified hashes of a file.

        :param file_path: The path to the file.
        :return: A dictionary of algorithm names to hash values.
        """
        if not os.path.isfile(file_path):
            return {}

        hashes = {}
        for algorithm in self.hash_algorithms:
            file_hash = self._hash_file(file_path, algorithm)
            if file_hash:
                hashes[algorithm] = file_hash
        return hashes

    def get_file_metadata(self, file_path):
        """
        Collects file metadata such as size, creation date, and file type.

        :param file_path: The path to the file.
        :return: A dictionary containing metadata of the file.
        """
        try:
            file_stats = os.stat(file_path)
            return {
                "file_size": file_stats.st_size,
                "creation_date": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                "last_modified_date": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                "file_type": self.get_file_type(file_path)
            }
        except Exception as e:
            return {"error": f"Unable to retrieve file metadata: {e}"}

    def get_file_type(self, file_path):
        """
        Determines the file type based on its extension.

        :param file_path: The path to the file.
        :return: A string indicating the file type.
        """
        return os.path.splitext(file_path)[-1].lower()

    def check_hash_malwarebazaar(self, file_hash):
        """
        Checks the file hash against the MalwareBazaar database.

        :param file_hash: The hash of the file.
        :return: A dictionary with the result of the check.
        """
        if file_hash in self.cache:
            return self.cache[file_hash]

        url = "https://mb-api.abuse.ch/api/v1/"
        data = {
            "query": "get_info",
            "hash": file_hash
        }
        headers = {
            "API-KEY": self.malwarebazaar_api_key
        }

        try:
            response = requests.post(url, data=data, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result['query_status'] == 'ok':
                analysis_result = {
                    "status": "known",
                    "service": "MalwareBazaar",
                    "malware_family": result['data'][0].get('signature', 'Unknown'),
                    "first_seen": result['data'][0].get('first_seen', 'Unknown'),
                    "file_type": result['data'][0].get('file_type', 'Unknown')
                }
                self.cache[file_hash] = analysis_result
                return analysis_result
            elif result['query_status'] == 'hash_not_found':
                return {"status": "unknown", "service": "MalwareBazaar"}
            else:
                return {"status": "error", "message": "Unexpected response format"}

        except requests.RequestException as e:
            return {"status": "error", "message": f"Request failed: {e}"}

    def check_hash_malshare(self, file_hash, retries=3):
        """
        Checks the file hash against the MalShare database using the correct action 'details'.

        :param file_hash: The hash of the file.
        :param retries: Number of retry attempts for the request (default is 3).
        :return: A dictionary with the result of the check.
        """
        if not self.malshare_api_key:
            return {"status": "error", "message": "MalShare API key not provided"}

        url = f"https://malshare.com/api.php?api_key={self.malshare_api_key}&action=details&hash={file_hash}"

        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=10)
                
                # Handle 404 Not Found separately
                if response.status_code == 404:
                    return {"status": "unknown", "service": "MalShare"}

                response.raise_for_status()
                result = response.json()  # Assuming the output format is JSON for 'details'

                if result and "ERROR" not in result:
                    return {
                        "status": "known",
                        "service": "MalShare",
                        "details": result
                    }
                else:
                    return {"status": "unknown", "service": "MalShare"}

            except requests.RequestException as e:
                if attempt == retries - 1:
                    return {"status": "error", "message": f"MalShare service is currently unavailable: {e}"}
                time.sleep(2 ** attempt)  # Exponential backoff

    def analyze_file(self, file_path):
        """
        Analyzes a file by calculating its hashes and checking them against MalwareBazaar and MalShare.

        :param file_path: The path to the file to be analyzed.
        :return: A dictionary with the analysis results for each hash.
        """
        if not os.path.exists(file_path):
            return {"status": "error", "message": "File does not exist"}

        # Get file metadata
        metadata = self.get_file_metadata(file_path)
        analysis_results = {
            "file_metadata": metadata,
            "hash_results": {}
        }
        hashes = self.calculate_hashes(file_path)
        
        for algorithm, file_hash in hashes.items():
            analysis_results["hash_results"][algorithm] = {
                "MalwareBazaar": self.check_hash_malwarebazaar(file_hash),
                "MalShare": self.check_hash_malshare(file_hash)
            }

        return analysis_results

# Example usage with detailed reporting
if __name__ == "__main__":
    malwarebazaar_api_key = "12c8e30d8b9ab0db9252b1811a2bb730"  # Replace with your MalwareBazaar API key
    malshare_api_key = "a4a41dc35c4ab4fbf104408387e5bb8a83def7dc7984ade358b255849b5c839b"  # Replace with your MalShare API key

    try:
        virus_checker = VirusChecker(malwarebazaar_api_key, malshare_api_key, hash_algorithms=['sha256', 'md5'])
    except ValueError as e:
        print(f"Initialization error: {e}")
    else:
        file_path = "test.dll"  # Replace with your file path
        result = virus_checker.analyze_file(file_path)

        # Print detailed report
        if "file_metadata" in result:
            print("\n=== File Metadata ===")
            for key, value in result["file_metadata"].items():
                print(f"{key}: {value}")

        if "hash_results" in result:
            print("\n=== Hash Analysis Results ===")
            for algo, services in result["hash_results"].items():
                print(f"\nHash Type: {algo.upper()}")
                for service, res in services.items():
                    print(f"[{service}] Status: {res.get('status')}")
                    if res.get('status') == 'known':
                        if 'malware_family' in res:
                            print(f"  - Malware Family: {res['malware_family']}")
                        if 'first_seen' in res:
                            print(f"  - First Seen: {res['first_seen']}")
                        if 'file_type' in res:
                            print(f"  - File Type: {res['file_type']}")
                        if 'details' in res:
                            print(f"  - Details: {res['details']}")
                    elif res.get('status') == 'unknown':
                        print("  - Not found in the database.")
                    elif res.get('status') == 'error':
                        print(f"  - Error: {res.get('message', 'No details available')}")

# API KEY malwarebazar 12c8e30d8b9ab0db9252b1811a2bb730
# API KEY malshare a4a41dc35c4ab4fbf104408387e5bb8a83def7dc7984ade358b255849b5c839b 