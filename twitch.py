import time
import requests

# This code uses the broadcasters User Token to get all viewers in chat
# The broadcaster has to connect with the App before this code can work
BROADCASTER = ""
BROADCASTER_ID = ""  # The User ID

# Go to "https://dev.twitch.tv/console/apps/" and create an App
# Get the Client ID and Secret from your App
# Scope needed is:
#   user:read:subscriptions
#   moderator:read:chatters   This is only relevant for the Broadcaster
CLIENT_ID = "<<client_id>>"
CLIENT_SECRET = "<<client_secret>>"

# Since Twitch's rate limiting is applied per minute there should never be a rate limit issue


def get_app_token() -> str:
    # API reference: https://dev.twitch.tv/docs/authentication/getting-tokens-oauth#client-credentials-grant-flow
    # Instead of requesting an access token for every app request store the token in a DB and just request if status_code == 401
    url = "https://id.twitch.tv/oauth2/token"
    params = {"client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials"}
    r = requests.post(url, params=params)
    # sample response:
    # {
    #   "access_token": "jostpf5q0uzmxmkba9iyug38kjtgh",
    #   "expires_in": 5011271,
    #   "token_type": "bearer"
    # }

    return r.json()["access_token"]


def refresh_token(refresh_token) -> dict:
    # API reference: https://dev.twitch.tv/docs/authentication/refresh-tokens#how-to-use-a-refresh-token
    # refresh token has to be URL encoded
    url = "https://id.twitch.tv/oauth2/token"
    params = {"client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": requests.utils.quote(refresh_token)
    }
    r = requests.post(url, params=params)
    # sample response: {
    #   "access_token": "0123456789abcdefghijABCDEFGHIJ",
    #   "refresh_token": "eyJfaWQmNzMtNGCJ9%6VFV5LNrZFUj8oU231/3Aj",
    #   "expires_in": 3600,
    #   "scope": "channel:read:subscriptions",
    #   "token_type": "bearer"
    # }

    if "error" in r.json().keys():
        # Implement your way of error handling here
        pass
    token = {
        "access_token": r.json()["access_token"],
        "refresh_token": r.json()["refresh_token"]
    }
    return token


def get_broadcaster_user_token() -> str:
    # TODO
    # This function should select the User Token from the Database
    pass


def get_viewer_list(cursor=None) -> dict:
    # API reference: https://dev.twitch.tv/docs/api/reference#get-chatters
    # Because the moderator ID has to match the user ID of the UserToken, the broadcasters ID is used
    # If there are more than 1000 viewers in chat pagination is used. THIS IS CURRENTLY NOT IMPLEMENTED!!!
    url = f"https://api.twitch.tv/helix/chat/chatters?broadcaster_id={BROADCASTER_ID}&moderator_id={BROADCASTER_ID}&first=1000"
    if cursor is not None:
        url += f"&after={cursor}"
    headers = {"Client-Id": CLIENT_ID,
              "Authorization": "Bearer " + get_broadcaster_user_token()}
    r = requests.get(url, headers=headers)
    # sample response: {
    #   "data": [
    #     {
    #       "user_id": "128393656",
    #       "user_login": "smittysmithers",
    #       "user_name": "smittysmithers"
    #     },
    #     ...
    #   ],
    #   "pagination": {
    #     "cursor": "eyJiIjpudWxsLCJhIjp7Ik9mZnNldCI6NX19"
    #   },
    #   "total": 8
    # }

    if r.status_code != 200:
        # TODO: Implement error handling here
        # 401 errors need a new user token
        pass
    return r.json()


def is_live(game_name="Just Chatting"):
    # API reference: https://dev.twitch.tv/docs/api/reference#get-streams
    url = f"https://api.twitch.tv/helix/streams?user_id={BROADCASTER_ID}"
    headers = {"Client-Id": CLIENT_ID,
               "Authorization": "Bearer " + get_app_token()}
    r = requests.get(url, headers=headers)
    # sample response: {
    #   "data": [
    #     {
    #       "id": "41375541868",
    #       "user_id": "459331509",
    #       "user_login": "auronplay",
    #       "user_name": "auronplay",
    #       "game_id": "494131",
    #       "game_name": "Little Nightmares",
    #       "type": "live",
    #       "title": "hablamos y le damos a Little Nightmares 1",
    #       "viewer_count": 78365,
    #       "started_at": "2021-03-10T15:04:21Z",
    #       "language": "es",
    #       "thumbnail_url": "https://static-cdn.jtvnw.net/previews-ttv/live_user_auronplay-{width}x{height}.jpg",
    #       "tag_ids": [
    #         "d4bb9c58-2141-4881-bcdc-3fe0505457d1"
    #       ],
    #       "is_mature": false
    #     },
    #     ...
    #   ],
    #   "pagination": {
    #     "cursor": "eyJiIjp7IkN1cnNvciI6ImV5SnpJam8zT0RNMk5TNDBORFF4TlRjMU1UY3hOU3dpWkNJNlptRnNjMlVzSW5RaU9uUnlkV1Y5In0sImEiOnsiQ3Vyc29yIjoiZXlKeklqb3hOVGs0TkM0MU56RXhNekExTVRZNU1ESXNJbVFpT21aaGJITmxMQ0owSWpwMGNuVmxmUT09In19"
    #   }
    # }

    if r.status_code != 200:
        # TODO: Implement error handling here
        # 401 errors need a new app token
        pass
    is_live = r.json()["data"][0]["type"] == "live"
    if r.json()["data"][0]["game_name"] != game_name:
        return False
    return is_live


def add_coins(user_id:str, coins:int=10, multiplier:float=1.0):
    # TODO: Needs checking if the user_id even exists in DB
    # coins is the amount given per interval and can be used with multiplier in example for Subscribers
    pass


def tick():
    # TODO: This needs some modifications if pagination handling is required
    for viewer in get_viewer_list()["data"]:
        add_coins(viewer["user_id"])


def main(interval:int=500):
    # Interval in seconds
    while 1:
        if is_live():
            tick()
            time.sleep(interval)


if __name__ == '__main__':
    main()