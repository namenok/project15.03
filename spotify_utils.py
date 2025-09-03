import base64
import requests
from django.conf import settings
import time
from mainapp.models import SpotifyToken
from django.utils import timezone

# for app
def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()).decode()
    }
    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        token = response.json()['access_token']
        return token
    else:
        print("Error getting token:", response.json())
        return None



def search_spotify_track(query, limit=5):
    token = get_spotify_token()
    if not token:
        return []

    url = "https://api.spotify.com/v1/search"
    params = {"q": query, "type": "track", "limit": limit}
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print("Error searching track:", response.json())
        return []

    data = response.json()
    results = []
    for item in data.get("tracks", {}).get("items", []):
        results.append({
            "id": item["id"],
            "name": item["name"],
            "artists": [artist["name"] for artist in item["artists"]],
            "url": item["external_urls"]["spotify"]
        })
    return results


# for user
def get_token_from_code(code):
   
    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error exchanging code:", response.json())
        return None


def refresh_access_token(refresh_token):
   
    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error refreshing token:", response.json())
        return None


def get_user_spotify_token(user):
  
    token_obj = SpotifyToken.objects.filter(user=user).first()
    if not token_obj:
        return None
    
    headers = {"Authorization": f"Bearer {token_obj.access_token}"}
    r = requests.get("https://api.spotify.com/v1/me", headers=headers)
    if r.status_code != 200:
        return None
    
    # Check if expired
    if token_obj.is_expired():
        data = refresh_access_token(token_obj.refresh_token)
        if data:
            token_obj.access_token = data["access_token"]
            token_obj.refresh_token = data.get("refresh_token", token_obj.refresh_token)
            token_obj.expires_in = data["expires_in"]
            token_obj.created_at = timezone.now()
            token_obj.save()
        else:
            return None

    return token_obj.access_token


def is_premium_user(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    if response.status_code == 200:
        return response.json().get("product") == "premium"
    return False
