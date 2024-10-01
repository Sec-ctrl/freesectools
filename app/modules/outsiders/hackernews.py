import requests
from bs4 import BeautifulSoup


class CyberNewsFetcher:
    def __init__(self):
        self.host = "https://thehackernews.com/"

    def get_news(self):
        try:
            response = requests.get(self.host)
            response.raise_for_status()
            content = response.content

            soup = BeautifulSoup(content, "html.parser")

            posts = soup.find_all("div", class_="body-post clear")
            news_items = []

            for post in posts:
                # Find the Title, ensure it's not None before accessing .text
                title_tag = post.find("h2", class_="home-title")
                title = title_tag.text.strip() if title_tag else None

                # Find the Link, ensure it's not None before accessing ['href']
                link_tag = post.find("a", class_="story-link")
                link = link_tag["href"] if link_tag else None

                # Find the Date, ensure it's not None before accessing .text
                date_tag = post.find("span", class_="h-datetime")
                date = date_tag.text.strip() if date_tag else None
                cleaned_date = (
                    "".join(
                        char
                        for char in date
                        if char.isalnum() or char.isspace() or char in ".,"
                    )
                    if date
                    else None
                )

                # Find the Image (Handle lazy-loaded images)
                image_tag = post.find("img", class_="home-img-src")
                image_url = None

                if image_tag:
                    # Attempt to get the real image URL from various possible attributes
                    if "data-src" in image_tag.attrs:
                        image_url = image_tag["data-src"]
                    elif "data-original" in image_tag.attrs:
                        image_url = image_tag["data-original"]
                    elif "src" in image_tag.attrs:
                        image_url = image_tag["src"]  # Fallback to 'src'

                # Only append the news item if title, link, and date are all present
                if title and link and date:
                    news_items.append(
                        {
                            "title": title,
                            "link": link,
                            "date": cleaned_date,
                            "image": image_url,  # Add image URL if it exists
                        }
                    )

            return news_items

        except requests.RequestException as e:
            print(f"An error occurred while fetching news: {e}")
            return []
