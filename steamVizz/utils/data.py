import streamlit as st
import pandas as pd
import numpy as np
import json
from pathlib import Path

DATA_FILE_PATH = Path("data/games.json")
st.write("DATA PATH:", DATA_FILE_PATH)
st.write("EXISTS:", DATA_FILE_PATH.exists())

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

