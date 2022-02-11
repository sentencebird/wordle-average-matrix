import streamlit as st
import pandas as pd
import numpy as np
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import os

st.title("Wordle Average Matrix")

st.markdown("<a href='https://www.powerlanguage.co.uk/wordle/'>Wordle</a>", unsafe_allow_html=True)
st.markdown(f"<a href='https://twitter.com/search?q=%22%23Wordle%20{237}%22&src=typed_query&f=live'>Recent tweets</a>", unsafe_allow_html=True) # TODO: wordleのID

# TODO: 手元にファイルがあるかで分岐ダウンロード部分を

dir_id = os.environ["dir_id"]
client_secrets = os.environ["client_secrets"]
with open("/tmp/client_secrets.json", "w") as f:
    f.write(client_secrets)
mycreds = os.environ["mycreds"]
with open("/tmp/mycreds.text", "w") as f:
    f.write(mycreds)    

@st.cache
def fetch_csv_files():
    gauth = GoogleAuth()
    GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = '/tmp/client_secrets.json'
    GoogleAuth.DEFAULT_SETTINGS['save_credentials_file'] = '/tmp/mycreds.txt'
    gauth.LoadCredentials(backend="file")
    gauth.LoadCredentialsFile("/tmp/mycreds.txt")

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("/tmp/mycreds.txt") 
    drive = GoogleDrive(gauth)

    files = drive.ListFile({'q': "'{}' in parents and trashed=false".format(dir_id)}).GetList()
    for file in files:
        f = drive.CreateFile({'id': file['id']})
        f.GetContentFile(file['title'])
        
    return [file['title'] for file in files]

df_by_score = {}
with st.spinner("Loading ..."):
    csv_files = fetch_csv_files()
for file in csv_files:
    if file == "colors.csv": 
        score = "all"
    else:
        score = int(file.split("_")[-1].split(".csv")[0]) / 5
        if score > 6: continue
        score = f"{int(score)} times"
    df_by_score[score] = pd.read_csv(file, index_col=0)

scores = ["all", "1 times", "2 times", "3 times", "4 times", "5 times", "6 times"]    
score = st.selectbox("Score", scores)
df = df_by_score[score]

chars = list(df.mode().values[0])[0]
arry = np.array([c for c in chars]).reshape(-1, 5)

def highlight(v):
    if v is None: return None
    codes = {"G": "78B15A", "Y": "FBCB59", "W": "E6E7E8"}
    return f'color: #{codes[v]}; background-color: #{codes[v]}; width: 200;'

df = pd.DataFrame(arry).style.applymap(highlight)
st.text("Average Matrix")
st.dataframe(df)