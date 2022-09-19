import requests
import config

username = config.pythonanywhere_username
token = config.pythonanywhere_token

response2 = requests.get(
    'https://www.pythonanywhere.com/api/v0/user/{username}/always_on/'.format(
        username=username
    ),
    headers={'Authorization': 'Token {token}'.format(token=token)}
)

print(response2.content)

response2 = requests.post(
    'https://www.pythonanywhere.com/api/v0/user/{username}/always_on/58864/restart/'.format(
        username=username
    ),
    headers={'Authorization': 'Token {token}'.format(token=token)}
)

# guideline: https://www.pythonanywhere.com/forums/topic/23549/