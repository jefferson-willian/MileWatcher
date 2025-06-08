import requests
from bs4 import BeautifulSoup

def extract_article_text_from_url(url):
    """
    Extracts article text from a URL, specifically looking for the
    <article class="single-content"> tag.

    Args:
        url (str): The URL of the HTML page.

    Returns:
        str: The extracted article text, or a message if not found or an error occurs.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an exception for HTTP errors

        soup = BeautifulSoup(response.text, 'html.parser')
        article_tag = soup.find('article', class_='single-content')

        if article_tag:
            return article_tag.get_text(separator='\n', strip=True)
        else:
            return "The <article class='single-content'> tag was not found on the page."
    except requests.exceptions.RequestException as e:
        return f"Error accessing the URL: {e}"
    except Exception as e:
        return f"An error occurred: {e}"

# Example URL
url = 'https://passageirodeprimeira.com/exemplo/'
article_text = extract_article_text_from_url(url)
print(article_text)
