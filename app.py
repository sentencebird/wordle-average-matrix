import streamlit as st
import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
import sqlalchemy.orm
import datetime

db_url = os.environ["db_url"]
scores = list(range(1, 7))

@st.cache
def wordle_id():
    d = datetime.date.today() -  datetime.date(2022, 2, 11)
    return 237 + d.days

@st.cache
def set_dataframe_per_score():
    engine = create_engine(db_url)
    res = engine.execute('SELECT * FROM colors').fetchall()
    df = pd.DataFrame(res)
    df_by_score = {"All": df}
    for score in scores:
        df_by_score[f"{score}/6"] = filter_dataframe_by_score(df, score)
    return df_by_score
    
def filter_dataframe_by_score(df, score):
    if score == 6: 
        return df[df["29"]=="G"]
    else:
        char_len = score * 5
        return df[df[f"{char_len-1}"] == "G"][df[f"{char_len}"].isin([None]) & df["29"].isin([None])]    
    
def prob_dataframe_by_color(df, color):
    arry = np.array(['{:.2f}'.format(df[i].value_counts().get(color, 0) / df.shape[0]) for i in df.columns])
    return pd.DataFrame(arry.reshape(-1, 5))    
    
st.set_page_config(page_title="Wordle Average Matrix", page_icon="favicon.png")
st.title("Wordle Average Matrix")    
st.header(f"Wordle {wordle_id()}")
st.markdown("<li><a href='https://www.powerlanguage.co.uk/wordle/' target='_blank'>Wordle</a></li>", unsafe_allow_html=True)
st.markdown(f"<li><a href='https://twitter.com/search?q=%22%23Wordle%20{wordle_id()}%22&src=typed_query&f=live' target='_blank'>Recent tweets of #Wordle {wordle_id()}</a></li>", unsafe_allow_html=True)    

with st.spinner("Loading ..."):
    try:
        df_by_score = set_dataframe_per_score()
    except:
        st.error("Loading failed")
        st.stop()

score = st.selectbox("Score", ["All"] + [f"{score}/6" for score in scores])
df = df_by_score[score]

chars = [v for v in list(df.mode().values[0]) if isinstance(v, str)]
arry = np.array([c for c in chars]).reshape(-1, 5)
score_i = arry.shape[0]

def highlight_color(v):
    if v is None: return None
    codes = {"G": "78B15A", "Y": "FBCB59", "W": "E6E7E8"}
    return f'color: #{codes[v]}; background-color: #{codes[v]};'

st.text(f"Average Matrix ({df.shape[0]} results)")
df_colored = pd.DataFrame(arry).style.applymap(highlight_color)
st.dataframe(df_colored)
    
def highlight_white(v): return f'background-color: rgba(230,231,232,{v});'
def highlight_yellow(v): return f'background-color: rgba(251,203,89,{v});'
def highlight_green(v): return f'background-color: rgba(120,177,90,{v});'

st.text(f"Probability of each character by color")
for color in ["W", "Y", "G"]:
    df_prob = prob_dataframe_by_color(df, color)[0:score_i]
    if color == "W":
        df_opacity = df_prob.style.applymap(highlight_white)
    elif color == "Y":
        df_opacity = df_prob.style.applymap(highlight_yellow)
    elif color == "G":
        df_opacity = df_prob.style.applymap(highlight_green)
    st.dataframe(df_opacity)
