import requests

def fetch_market_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()  # Adjust parsing based on API structure
    else:
        return None
