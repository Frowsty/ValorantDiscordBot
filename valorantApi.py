import requests
import json
import urllib.parse

class ValorantAPI(object):
  access_token = None
  cookies = None
  entitlements_token = None

  def __init__(self, username, password, region):
    self.username = username
    self.password = password
    self.region = region

    self.cookies = self.get_cookies()

    self.access_token = self.get_access_token()

    self.entitlements_token = self.get_entitlements_token()

    self.user_info, self.game_name = self.get_user_info()

  def get_cookies(self):
    data = {
    'client_id': 'play-valorant-web-prod',
    'nonce': '1',
    'redirect_uri': 'https://playvalorant.com/',
    'response_type': 'token id_token',
    'scope': 'account openid',
    }
    r = requests.post('https://auth.riotgames.com/api/v1/authorization', json=data)

    cookies = r.cookies

    return cookies

  def get_access_token(self):
    data = {
      'type': 'auth',
      'username': self.username,
      'password': self.password
    }
    r = requests.put('https://auth.riotgames.com/api/v1/authorization', json=data, cookies=self.cookies)
    if r.json()['type'] != 'auth':
      uri = r.json()['response']['parameters']['uri']
      jsonUri = urllib.parse.parse_qs(uri)
      access_token = jsonUri['https://playvalorant.com/#access_token'][0]
    else:
      access_token = 'Error'

    return access_token

  def get_entitlements_token(self):
    headers = {
      'Authorization': f'Bearer {self.access_token}',
    }
    r = requests.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={}, cookies=self.cookies)
    if 'entitlements_token' in r.json():
      entitlements_token = r.json()['entitlements_token']
    else:
      entitlements_token = 'Error'
    return entitlements_token

  def get_user_info(self):
    headers = {
      'Authorization': f'Bearer {self.access_token}',
    }
    r = requests.post('https://auth.riotgames.com/userinfo', headers=headers, json={}, cookies=self.cookies)
    if len(r.json()) > 0:
      jsonData = r.json()
      user_info = jsonData['sub']
      name = jsonData['acct']['game_name']
      tag  = jsonData['acct']['tag_line']
      game_name = name + ' #' +  tag
    else:
      user_info = 'Error'
      game_name = 'Error'

    return user_info, game_name

  def get_match_history(self):
    headers = {
      'Authorization': f'Bearer {self.access_token}',
      'X-Riot-Entitlements-JWT': f'{self.entitlements_token}',
      'X-Riot-ClientPlatform': 'ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9'
    }
    r = requests.get(f'https://pd.{self.region}.a.pvp.net/mmr/v1/players/{self.user_info}/competitiveupdates?startIndex=0&endIndex=20', headers=headers, cookies=self.cookies)
    if 'Subject' in r.json():
      jsonData = r.json()
    else:
      jsonData = 'Error'

    return jsonData