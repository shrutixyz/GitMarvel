import requests

def fetch_profile_info(username, access_token):
    response = requests.get(f"https://api.github.com/users/{username}", headers={'Authorization': f'Bearer {access_token}'} )
    return response.json()