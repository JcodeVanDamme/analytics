import streamlit as st
import pandas as pd
import numpy as np
import json
import os

current_dir = os.path.abspath(os.path.dirname(__file__))
repo_root = os.path.dirname(current_dir)
DATA_FILE_PATH = os.path.join(repo_root, "data/games.json")

st.write("Current dir:", current_dir)
st.write("Data path:", DATA_FILE_PATH)
st.write("Exists:", os.path.exists(DATA_FILE_PATH))

@st.cache_data(show_spinner=True)
def load_data():
    with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame.from_dict(data, orient="index")

    df.reset_index(inplace=True)
    df.rename(columns={"index": "game_id"}, inplace=True)

    return df

@st.cache_data
def stringify(df):
    df = df.copy()

    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
            df[col] = df[col].apply(
                lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x
            )

    return df

