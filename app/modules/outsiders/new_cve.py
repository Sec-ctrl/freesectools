from bs4 import BeautifulSoup
import requests


class CyberCVEFetcher:
    def __init__(self):
        self.host = "https://www.tenable.com/cve/newest"

    def get_CVE(self):
        try:
            response = requests.get(self.host)
            response.raise_for_status()
            content = response.content

            soup = BeautifulSoup(content, "html.parser")

            posts = soup.find_all("tr")
            cve_items = []

            for post in posts:
                # Find CVE Title
                title_tag = post.find("td", class_="cve-id")
                title = title_tag.get_text(strip=True) if title_tag else None

                # Find the Link
                link_tag = title_tag.find("a") if title_tag else None
                link = link_tag["href"] if link_tag else None

                # Find Description
                desc_tag = (
                    post.find_all("td")[1] if len(post.find_all("td")) > 1 else None
                )
                desc = desc_tag.get_text(strip=True) if desc_tag else None

                # Find the Severity
                severity_tag = post.find("span", class_="badge")
                severity = severity_tag.get_text(strip=True) if severity_tag else None

                # Map severity to CSS classes
                severity_class = "text-secondary"  # Default class
                if severity:
                    severity_lower = severity.lower()
                    if severity_lower == "low":
                        severity_class = "text-success"
                    elif severity_lower == "medium":
                        severity_class = "text-warning"
                    elif severity_lower == "high":
                        severity_class = "text-danger"
                    elif severity_lower == "critical":
                        severity_class = "text-danger font-weight-bold"

                if title and desc:
                    cve_items.append(
                        {
                            "title": title,
                            "link": link,
                            "desc": desc,
                            "severity": severity,
                            "severity_class": severity_class,
                        }
                    )
            return cve_items

        except requests.RequestException as e:
            print(f"An error occurred while fetching CVE data: {e}")
            return []
