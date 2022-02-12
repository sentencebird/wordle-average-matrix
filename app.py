import streamlit as st
import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
import sqlalchemy.orm

st.title("Wordle Average Matrix")

st.markdown("<li><a href='https://www.powerlanguage.co.uk/wordle/'>Wordle</a></li>", unsafe_allow_html=True)
st.markdown(f"<li><a href='https://twitter.com/search?q=%22%23Wordle%20{237}%22&src=typed_query&f=live'>Recent tweets</a></li>", unsafe_allow_html=True) # TODO: wordleのID

db_url = os.environ["db_url"]
scores = list(range(1, 7))

@st.cache
def set_dataframe_per_score():
    engine = create_engine(db_url)
    res = engine.execute('SELECT * FROM colors').fetchall()
    df = pd.DataFrame(res)
    df_by_score = {"All": df}
    for score in scores:
        df_by_score[f"{score} times"] = filter_dataframe_by_score(df, score)
    return df_by_score
    
def filter_dataframe_by_score(df, score):
    if score == 6: 
        return df[df["29"]=="G"]
    else:
        char_len = score * 5
        return df[df[f"{char_len-1}"] == "G"][df[f"{char_len}"].isin([None]) & df["29"].isin([None])]    

with st.spinner("Loading ..."):
    df_by_score = set_dataframe_per_score()


score = st.selectbox("Score", ["All"] + [f"{score} times" for score in scores])
df = df_by_score[score]

chars = [v for v in list(df.mode().values[0]) if isinstance(v, str)]
arry = np.array([c for c in chars]).reshape(-1, 5)

def highlight(v):
    if v is None: return None
    codes = {"G": "78B15A", "Y": "FBCB59", "W": "E6E7E8"}
    return f'color: #{codes[v]}; background-color: #{codes[v]}; width: 200;'

df_colored = pd.DataFrame(arry).style.applymap(highlight)
st.text(f"Average Matrix ({df.size} results)")
st.dataframe(df_colored)