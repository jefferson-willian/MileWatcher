import requests
from bs4 import BeautifulSoup

def extract_posts_passageiro_de_primeira_url():
    """
    Extracts titles and links of posts within the element with data-term="promocoes"
    directly from the Passageiro de Primeira URL, using the h1.article--title structure.
    """
    url = 'https://passageirodeprimeira.com/categorias/promocoes/'
    base_url = "https://passageirodeprimeira.com" # For relative links

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print(f"Accessing URL: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        posts = []

        # 1. Find the element with the data-term="promocoes" attribute (main promotions section)
        # We keep this search as posts might be contained within it.
        promotions_section = soup.find('div', {'data-term': 'promocoes'})

        if not promotions_section:
            print("Section 'promocoes' (data-term=\"promocoes\") not found in HTML. Searching in the entire document.")
            # If the main section is not found, we try to search for titles in the entire document.
            # This might happen if the page structure has changed and the 'data-term' section no longer encloses all posts.
            target_scope = soup
        else:
            target_scope = promotions_section
            print("Section 'promocoes' found. Searching for posts...")


        # 2. Within the scope (promotions section or entire document), look for the post elements.
        # Now, we look for the <h1 class="article--title"> structure you indicated.
        h1_titles = target_scope.find_all('h1', class_='article--title')

        if not h1_titles:
            print("No <h1 class=\"article--title\"> elements found. Please check the page structure.")
            # In case the h1.article--title structure is no longer there, we could try the previous one
            # or re-investigate the page.
            return []

        for h1_tag in h1_titles:
            link_tag = h1_tag.find('a', href=True) # Find the <a> tag inside the <h1>

            if link_tag:
                link = link_tag.get('href')
                title = link_tag.get_text(strip=True) # The title is the text within the <a> tag

                # Ensures relative links become absolute
                if link and not link.startswith(('http://', 'https://')):
                    link = base_url + link

                # Avoids posts with empty or generic titles if there's any parsing error
                if title and title.strip() != '':
                    posts.append({'title': title, 'link': link})

        return posts

    except requests.exceptions.RequestException as e:
        print(f"HTTP request error for {url}: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during extraction: {e}")
        return []

if __name__ == "__main__":
    found_posts = extract_posts_passageiro_de_primeira_url()

    if found_posts:
        print(f"\nFound {len(found_posts)} posts in the promotions section of Passageiro de Primeira (from URL):")
        for i, post in enumerate(found_posts):
            print(f"{i+1}. Title: {post['title']}\n   Link: {post['link']}\n")
    else:
        print("No posts found in the promotions section or an issue occurred during URL extraction.")
