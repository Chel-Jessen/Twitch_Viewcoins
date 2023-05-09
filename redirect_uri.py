import flask
import requests
from flask import Flask, redirect, request


# Change to the values from your Twitch App
CLIENT_ID = "<<client_id>>"
CLIENT_SECRET = "<<client_secret>>"
# Redirect URI has to be https
REDIRECT_URI = ""

BROADCASTER_ID = ""

app = Flask(__name__)

@app.route("/")
def index():
    return flask.send_file("./connect.html")

@app.route("/twitchauth")
def on_auth_receive():
    url_params = request.args
    if "error" in url_params.keys():
        # Redirect to profile page and display error message
        return redirect("/profile", 400)
    # Store tokens, username and if needed subscription in DB associated with the user
    tokens = get_access_token_from_auth_code(url_params["code"])
    user_id = get_userid_from_token(tokens["access_token"])
    is_sub = is_subscribed(user_id, tokens["access_token"])
    return redirect("/profile", 200)


def get_access_token_from_auth_code(auth_code:str) -> dict:
    # API reference: https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#use-the-authorization-code-to-get-a-token
    # Users access and refresh tokens should be saved in case a user changes his Twitch name
    url = "https://id.twitch.tv/oauth2/token"
    params = {"client_id": CLIENT_ID,
              "client_secret": CLIENT_SECRET,
              "code": auth_code,
              "redirect_uri": REDIRECT_URI,
              "grant_type": "authorization_code"}
    r = requests.post(url, params=params).json()
    # sample response: {
    #   "access_token": "rfx2uswqe8l4g1mkagrvg5tv0ks3",
    #   "expires_in": 14124,
    #   "refresh_token": "5b93chm6hdve3mycz05zfzatkfdenfspp1h1ar2xxdalen01",
    #   "scope": [
    #     "channel:moderate",
    #     "chat:edit",
    #     "chat:read"
    #   ],
    #   "token_type": "bearer"
    # }

    token = {
        "access_token": r["access_token"],
        "refresh_token": r["refresh_token"]
    }
    return token


def get_userid_from_token(access_token:str) -> str:
    # API reference: https://dev.twitch.tv/docs/api/reference#get-users
    url = "https://api.twitch.tv/helix/users"
    headers = {"Client-Id": CLIENT_ID,
               "Authorization": "Bearer " + access_token}
    r = requests.get(url, headers=headers)
    # sample response: {
    #   "data": [
    #     {
    #       "id": "141981764",
    #       "login": "twitchdev",
    #       "display_name": "TwitchDev",
    #       "type": "",
    #       "broadcaster_type": "partner",
    #       "description": "Supporting third-party developers building Twitch integrations from chatbots to game integrations.",
    #       "profile_image_url": "https://static-cdn.jtvnw.net/jtv_user_pictures/8a6381c7-d0c0-4576-b179-38bd5ce1d6af-profile_image-300x300.png",
    #       "offline_image_url": "https://static-cdn.jtvnw.net/jtv_user_pictures/3f13ab61-ec78-4fe6-8481-8682cb3b0ac2-channel_offline_image-1920x1080.png",
    #       "view_count": 5980557,
    #       "email": "not-real@email.com",
    #       "created_at": "2016-12-14T20:32:28Z"
    #     }
    #   ]
    # }

    if r.status_code != 200:
        # TODO: Implement error handling here
        pass
    return r.json()["data"][0]["id"]


def is_subscribed(user_id:str, access_token:str) -> bool:
    # API reference: https://dev.twitch.tv/docs/api/reference#check-user-subscription
    url = f"https://api.twitch.tv/helix/subscriptions/user?broadcaster_id={BROADCASTER_ID}&user_id={user_id}"
    headers = {"Client-Id": CLIENT_ID,
               "Authorization": "Bearer " + access_token}
    r = requests.get(url, headers=headers)
    # sample response: {
    #   "data": [
    #     {
    #       "broadcaster_id": "149747285",
    #       "broadcaster_name": "TwitchPresents",
    #       "broadcaster_login": "twitchpresents",
    #       "is_gift": false,
    #       "tier": "1000"
    #     }
    #   ]
    # }

    if r.status_code != 200:
        # TODO: Implement error handling here
        pass
    if "tier" in r.json().keys():
        return True
    return False