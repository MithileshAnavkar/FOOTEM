
# ⚽ FOOTEM — Football Analytics Dashboard

FOOTEM is a football analytics web application built with Python and Streamlit. It uses FIFA 23 player data to explore player statistics, compare players, discover similar players, identify potential prospects, and demonstrate machine-learning-based rating prediction.

## 🚀 Features

- **Player Explorer:** Search players and view their profiles and attributes.
- **Similar Player Finder:** Find players with similar football attributes.
- **Player Comparison:** Compare two players side by side.
- **Leaderboard:** Rank players using their overall ratings.
- **ML Rating Prediction:** Estimate player ratings using a trained Random Forest model.
- **Scouting Insights:** Filter young players by potential and development gap.
- **CSV Downloads:** Export leaderboard, similar-player results, and scouting reports.

## 🛠️ Tech Stack

- Python
- Streamlit
- Pandas
- NumPy
- Scikit-learn
- Joblib
- FIFA 23 player CSV dataset

## 📁 Project Structure

FOOTEM/
├── app.py
├── ml_model.py
├── players_fifa23.csv
├── footem_rating_model.pkl
└── README.md

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd FOOTEM
```

### 2. Install dependencies

```bash
pip install streamlit pandas numpy scikit-learn joblib
```

### 3. Train the machine learning model

```bash
python ml_model.py
```

This creates `footem_rating_model.pkl`.

### 4. Launch the application

```bash
streamlit run app.py
```

Streamlit will provide a local URL to open the dashboard in your browser.

## 🤖 Machine Learning

The project uses a Random Forest regression model to estimate a player's overall rating from selected numerical attributes.

The training script reports:
- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- R-squared score

These metrics help evaluate the model's performance on a held-out test set.

## 📊 Dataset

The application uses a FIFA 23 player CSV dataset. Keep the dataset in the project folder and ensure its column names match the model-training script.

## ⚠️ Limitations

- FIFA ratings are not a guarantee of real-world player performance.
- Similarity scores depend on the selected attributes.
- Model predictions depend on dataset quality and feature selection.
- Dataset licensing and redistribution permissions should be checked before publishing the CSV.

## 🔮 Future Improvements

- Add advanced filters for leagues and positions.
- Improve player similarity with position-specific attributes.
- Add interactive charts and scouting filters.
- Deploy the dashboard online.
- Evaluate additional machine-learning models.

## 👨‍💻 Author

Add your name, GitHub profile, and contact details here.
