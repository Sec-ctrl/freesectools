from bs4 import BeautifulSoup
import requests

class CyberNewsFetcher:
    def __init__(self):
        self.host = 'https://thehackernews.com/'

    def get_news(self):
        try:
            response = requests.get(self.host)
            response.raise_for_status()
            content = response.content

            soup = BeautifulSoup(content, 'html.parser')

            posts = soup.find_all('div', class_='body-post clear')
            news_items = []

            for post in posts:
                # Find the Title
                title = post.find('h2', class_="home-title").text.strip()

                # Find the Link
                link = post.find('a', class_="story-link")['href']

                # Find the Date
                date = post.find('span', class_="h-datetime").text.strip()
                cleaned_date = "".join(char for char in date if char.isalnum() or char.isspace() or char in '.,')

                # Find the Image (Handle lazy-loaded images)
                image_tag = post.find('img', class_='home-img-src')
                image_url = None

                if image_tag:
                    # Attempt to get the real image URL from various possible attributes
                    if 'data-src' in image_tag.attrs:
                        image_url = image_tag['data-src']
                    elif 'data-original' in image_tag.attrs:
                        image_url = image_tag['data-original']
                    elif 'src' in image_tag.attrs:
                        image_url = image_tag['src']  # Fallback to 'src'

                if title and link and date:
                    news_items.append({
                        'title': title,
                        'link': link,
                        'date': cleaned_date,
                        'image': image_url  # Add image URL if it exists
                    })

            return news_items

        except requests.RequestException as e:
            print(f"An error occurred while fetching news: {e}")
            return []

# Test the CyberNewsFetcher class
if __name__ == '__main__':
    news_fetcher = CyberNewsFetcher()
    news_items = news_fetcher.get_news()

    if news_items:
        print("Successfully fetched news articles:\n")
        for i, news in enumerate(news_items, 1):
            print(f"{i}. {news['date']} - {news['title']}")
            print(f"   Link: {news['link']}")
            if news['image']:
                print(f"   Image: {news['image']}")
            print()
    else:
        print("No news articles found.")
