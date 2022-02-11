from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import requests
from requests_oauthlib import OAuth1
import json
import re
import os
import pandas as pd
import numpy as np
import datetime

# TODO: ファイル名にID入れる


API_KEY = os.environ["API_KEY"]
API_KEY_SECRET = os.environ["API_KEY_SECRET"]
BEARER_TOKEN = os.environ["BEARER_TOKEN"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]
mycreds = os.environ["mycreds"]
dir_id = os.environ["dir_id"]
clients_secrets = os.environ["dir_id"]
with open("client_secrets.json", "w") as f:
    f.write(clients_secrets)


class Twitter():
    def __init__(self):
        self.OAuth = OAuth1(API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        
    def search_query_by_request(self, query, max_results=10000, next_token=None):
        url = 'https://api.twitter.com/2/tweets/search/recent'
        #query += " exclude:nativeretweets filter:media"
        params = {'query': query, 'max_results': max_results, 'next_token': next_token}
        request = requests.get(url, params=params, auth=self.OAuth)
        requestJson = json.loads(request.text)
        return requestJson
    
    def search_query(self, query, max_results=10000):
        data = []
        next_token = None
        while len(data) < max_results:
            res = self.search_query_by_request(query, next_token=next_token)
            data += res['data']
            if 'next_token' not in res['meta']: break
            next_token = res['meta']['next_token']
        return {'data': data, 'meta': res['meta']}
            
def parse_colors(text):
    p, s = "^^**", "**$$"
    text = text\
    .replace("⬛️", f"{p}W{s}")\
    .replace("⬛", f"{p}W{s}")\
    .replace("⬜", f"{p}W{s}")\
    .replace("\U0001f7e8",  f"{p}Y{s}")\
    .replace("\U0001f7e9", f"{p}G{s}")\
    .replace("\n", "")
    match = re.search("\^\^\*\*.*\*\*\$\$", text)
    if match is None: return None
    sub_text = re.sub("[\^\*\$]", "", match.group())
    if len([None for s in sub_text.strip() if re.match("[^WYG]", s)]) !=0: return None
    return sub_text

def wordle_id():
    d = datetime.date.today() -  datetime.date(2022, 2, 11)
    return 237 + d.days


# ツイート取得
t = Twitter()

wordle_id = wordle_id()
res = t.search_query(f'"#Wordle {wordle_id}"')

colors = []
colors_by_score = {}
for d in res['data']:
    color = parse_colors(d['text'])
    if color is not None and len(color) % 5 == 0: 
        colors.append(list(color))
        score = str(len(color))
        colors_by_score[score] = [color] if score not in colors_by_score else colors_by_score[score] + [color]

# ファイル出力
pd.DataFrame(colors).to_csv(f"./csv/{wordle_id}_colors.csv")
for key, value in colors_by_score.items():
    pd.DataFrame(value).to_csv(f"./csv/{wordle_id}_colors_{key}.csv")


# Googleドライブにアップロード    
gauth = GoogleAuth()

with open("mycreds.txt", "w") as f:
    f.write(mycreds)

gauth.LoadCredentialsFile("mycreds.txt")

if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()
gauth.SaveCredentialsFile("mycreds.txt") 
drive = GoogleDrive(gauth)


files = drive.ListFile({'q': "'{}' in parents and trashed=false".format(dir_id)}).GetList()
for file in files:
    file.Delete()

path = "./csv"
for fname in os.listdir(path):
    f = drive.CreateFile({'title': fname,'parents': [{'id': dir_id}]})
    f.SetContentFile(f"{path}/{fname}")
    f.Upload()
    
f = None