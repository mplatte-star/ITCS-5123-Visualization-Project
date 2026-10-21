# LLM Prompt: Analyze the dataset and identify necessary cleaning

import pandas as pd
from pathlib import Path

# Locate project directory
project_root = Path.cwd()

if not (project_root / "data" / "netflix_titles.csv").exists():
    project_root = project_root.parent

# Define file paths
input_path = project_root / "data" / "netflix_titles.csv"
output_path = project_root / "data" / "netflix_cleaned.csv"

# Load dataset
df = pd.read_csv(input_path)

# Remove extra whitespace from text columns
for col in df.select_dtypes(include="object"):
    df[col] = df[col].str.strip()

# Fix durations accidentally placed in rating
mask = df["rating"].str.contains(r"^\d+ min$", na=False)
df.loc[mask, "duration"] = df.loc[mask, "rating"]
df.loc[mask, "rating"] = "Unknown"

# Fill missing categorical values
for col in ["director", "cast", "country", "rating"]:
    df[col] = df[col].fillna("Unknown")

# Convert dates
df["date_added"] = pd.to_datetime(
    df["date_added"], errors="coerce"
)

df["year_added"] = df["date_added"].dt.year
df["month_added"] = df["date_added"].dt.month

# Separate duration into numeric columns
df["duration_number"] = pd.to_numeric(
    df["duration"].str.extract(r"(\d+)")[0],
    errors="coerce"
)

df["duration_minutes"] = df["duration_number"].where(
    df["type"] == "Movie"
)

df["seasons"] = df["duration_number"].where(
    df["type"] == "TV Show"
)

# Remove verified duplicate entry
df = df[df["show_id"] != "s6530"]

# Save cleaned dataset
df.to_csv(output_path, index=False)
