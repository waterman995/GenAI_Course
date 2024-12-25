import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://openaccess.thecvf.com/CVPR2024?day=2024-06-19'  # Ensure this is the correct URL for CVPR 2024 papers

# Send a GET request to the website with headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.content, 'lxml')

papers = soup.find_all('dt', class_='ptitle')
if not papers:
    print("No papers found. Please check the class name or the website structure.")
    print("Response status code:", response.status_code)
    print("Response headers:", response.headers)
    print("Response content snippet:", response.content[:500])
    exit()

data = []

for paper in papers:
    a_tag = paper.find('a')
    if a_tag:
        title = a_tag.text.strip()
        link = a_tag['href']
        
        # Navigate to the paper's page
        paper_url = f'https://openaccess.thecvf.com{link}'
        paper_response = requests.get(paper_url)
        paper_soup = BeautifulSoup(paper_response.content, 'html.parser')
        
        # Extract authors
        authors = [meta['content'] for meta in paper_soup.find_all('meta', {'name': 'citation_author'})]
        
        # Extract abstract
        abstract_div = paper_soup.find('div', id='abstract')
        abstract = abstract_div.text.strip() if abstract_div else 'N/A'
        
        # Extract PDF URL
        pdf_url_meta = paper_soup.find('meta', {'name': 'citation_pdf_url'})
        pdf_url = pdf_url_meta['content'] if pdf_url_meta else 'N/A'
        
        data.append({
            'title': title,
            'authors': ', '.join(authors),
            'abstract': abstract,
            'pdf_url': pdf_url
        })

df = pd.DataFrame(data)

save_path = input("Please enter the path where you want to save the dataset (e.g., 'papers.csv'): ")

df.to_csv(save_path, index=False)

print(f"Data has been successfully scraped and saved to {save_path}.")
