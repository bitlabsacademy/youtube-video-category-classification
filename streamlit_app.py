import os

import emoji
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

import config as c


def demojize(text):
    list_emoji = [e for e in emoji.UNICODE_EMOJI.get("en")]
    for em in list_emoji:
        if em in text:
            em_text = emoji.demojize(em)
            text = text.replace(em, " " + em_text + " ")
    return text


@st.cache
def get_category_dict(category_file):
    category = pd.read_json(category_file, orient="records")
    category = pd.DataFrame(category["items"].values.tolist())

    return {
        cat.id: cat.snippet.get("title")
        for cat in category.itertuples(index=False)
    }


@st.cache(allow_output_mutation=True)
def get_model(model_path: str):
    """Get model."""
    if not os.path.exists(model_path):
        st.error(f"Model ({model_path}) not found")

    model = joblib.load(model_path)
    return model


model = get_model(c.MODEL_PATH)
logo = Image.open(c.LOGO_PATH)
dict_category = get_category_dict(c.CATEGORY_PATH)
list_category_name = [
    dict_category.get(str(label))
    for label in model.classes_
]

st.title("YouTube Video Category Classification")
st.subheader("based on Title and Description")
st.image(logo)

text = st.text_area("Put your title and/or description here:")
text = demojize(text)

run_model = st.button("Classify")
if run_model:
    prediction = model.predict([text])
    probs = pd.DataFrame(model.predict_proba([text]),
                         columns=list_category_name)
    probs.index = ["probability"]
    category = dict_category.get(str(prediction[0]), "Unknown Category")
    st.write("Video category:", category)
    st.bar_chart(probs.T, width=20)
