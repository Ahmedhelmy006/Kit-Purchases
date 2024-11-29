from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import os
import json
import requests

load_dotenv(dotenv_path="enviroment_variables.env")

ID = os.getenv('KIT_OAUTH2_ID')
SECRET = os.getenv('KIT_OAUTH2_SECRET')
authorization_base_url = "https://api.kit.com/oauth/authorize"
token_url = "https://api.kit.com/oauth/token"
redirect_uri = "https://localhost"

oauth = OAuth2Session(ID, redirect_uri=redirect_uri)
authorization_url, state = oauth.authorization_url(authorization_base_url)
print("Visit this URL to authorize:", authorization_url)

authorization_response = input("Paste the full redirect URL here: ")

try:
    token = oauth.fetch_token(
        token_url,
        authorization_response=authorization_response,
        client_secret=SECRET
    )
    print("Access token fetched successfully.")
except Exception as e:
    print("Error during token exchange:", e)
    exit()

headers = {
    "Authorization": f"Bearer {token['access_token']}",
    "Accept": "application/json"
}

next_page_url = "https://api.kit.com/v4/purchases"
all_purchases = []
records_to_fetch = 100000
total_records = 0

while next_page_url and total_records < records_to_fetch:
    response = requests.get(next_page_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        
        purchases = data.get("purchases", [])
        if not purchases:
            print("No more purchases found in this page.")
            break
        
        all_purchases.extend(purchases)
        total_records += len(purchases)

        pagination = data.get("pagination", {})
        if pagination.get("has_next_page") and total_records < records_to_fetch:
            end_cursor = pagination.get("end_cursor")
            next_page_url = f"https://api.kit.com/v4/purchases?after={end_cursor}"
        else:
            next_page_url = None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        break

# Save data to a JSON file
if all_purchases:
    with open("purchases.json", "w") as json_file:
        json.dump(all_purchases[:records_to_fetch], json_file, indent=4)
    print(f"Successfully fetched {len(all_purchases[:records_to_fetch])} purchases.")
else:
    print("No purchases were retrieved.")
