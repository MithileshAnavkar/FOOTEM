
import streamlit as st
import pandas as pd
import joblib

@st.cache_resource
def load_model():
    return joblib.load("footem_rating_model.pkl")

def show_prediction(df):
    saved = load_model()
    model = saved["model"]
    features = saved["features"]
    target = saved["target"]

    missing = [col for col in features if col not in df.columns]

    if missing:
        st.error("Some required model features are missing from the dataset.")
        st.write(missing)
        return

    names = "short_name" if "short_name" in df.columns else (
        "long_name" if "long_name" in df.columns else None
    )

    if names is None:
        st.error("Player name column not found.")
        return

    players = df[names].fillna("Unknown").astype(str).tolist()
    selected = st.selectbox("Choose a player", players)

    row = df[df[names].fillna("Unknown").astype(str) == selected].iloc[0]

    X = row[features].to_frame().T.apply(pd.to_numeric, errors="coerce")
    X = X.fillna(df[features].apply(pd.to_numeric, errors="coerce").median())

    predicted = float(model.predict(X)[0])

    st.subheader(selected)
    c1, c2 = st.columns(2)

    with c1:
        st.metric("Predicted Rating", round(predicted, 1))

    with c2:
        if target in row.index and pd.notna(row[target]):
            st.metric("Actual Rating", round(float(row[target]), 1))
        else:
            st.info("Actual rating unavailable.")

    st.caption(
        "Predictions are estimates from a Random Forest model, "
        "not official player ratings."
    )
