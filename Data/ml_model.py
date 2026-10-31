
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Load FIFA dataset
df = pd.read_csv("players_fifa23.csv")

# Clean column names
df.columns = df.columns.str.strip()

print("Dataset loaded successfully!")
print("Number of players:", len(df))
print("\nAvailable columns:")
print(df.columns.tolist())

# Find the overall rating column
possible_targets = ["overall", "Overall", "overall_rating", "OVR"]

target = next(
    (col for col in possible_targets if col in df.columns),
    None
)

if target is None:
    print("\nCould not automatically find the overall rating column.")
    print("Check the column names printed above.")
    raise SystemExit

# Use numeric columns as features, excluding rating and leakage-prone fields
numeric_df = df.select_dtypes(include=np.number).copy()

excluded_words = [
    "overall", "potential", "value", "wage", "release_clause",
    "id", "sofifa_id", "player_id"
]

feature_cols = [
    col for col in numeric_df.columns
    if col != target
    and not any(word in col.lower() for word in excluded_words)
]

# Remove rows without the target rating
data = numeric_df[feature_cols + [target]].dropna(subset=[target])

# Keep only useful features with enough data
feature_cols = [
    col for col in feature_cols
    if data[col].notna().sum() >= 0.7 * len(data)
]

X = data[feature_cols].fillna(data[feature_cols].median())
y = data[target]

if len(feature_cols) == 0:
    raise ValueError("No suitable numeric features were found.")

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train machine learning model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# Evaluate model
predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
r2 = r2_score(y_test, predictions)

print("\n--- FOOTEM ML MODEL RESULTS ---")
print("Target rating column:", target)
print("Features used:", len(feature_cols))
print("Mean Absolute Error (MAE):", round(mae, 2))
print("Root Mean Squared Error (RMSE):", round(rmse, 2))
print("R-squared score:", round(r2, 3))

# Save the trained model and its feature list
import joblib

joblib.dump(
    {"model": model, "features": feature_cols, "target": target},
    "footem_rating_model.pkl"
)

print("\nModel saved as footem_rating_model.pkl")
