# Airline Sentiment Analysis

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge&logo=plotly&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-4C72B0?style=for-the-badge&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly%20Dash-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)
![Status](https://img.shields.io/badge/status-work%20in%20progress-yellow?style=for-the-badge)

![Dataset Cover](assets/dataset-cover.jpg)

A data analysis project exploring customer sentiment toward major US airlines, based on tweets. The project covers data exploration, cleaning, and visualization using Python, pandas, and SQLite, plus an interactive Plotly Dash dashboard.

## Dataset

Source: [Airline Sentiment (Kaggle)](https://www.kaggle.com/datasets/welkin10/airline-sentiment)

The dataset contains tweets directed at six US airlines between **February 16 and 24, 2015**, each labeled with a sentiment (`positive`, `neutral`, or `negative`) and, where applicable, a reason for negative feedback. Kaggle ships it as `Tweets.csv` with 14,640 rows; after removing duplicate tweets, **14,485 tweets** remain.

**Airlines covered:** Delta, United, Southwest, US Airways, Virgin America, American

**Key columns:**

| Column | Description |
|---|---|
| `tweet_id` | Unique tweet identifier |
| `airline_sentiment` | Sentiment label (positive / neutral / negative) |
| `airline_sentiment_confidence` | Confidence score for the sentiment label |
| `negativereason` | Reason for negative sentiment (if applicable) |
| `negativereason_confidence` | Confidence score for the negative reason |
| `airline` | Airline the tweet refers to |
| `name` | Twitter username |
| `retweet_count` | Number of retweets |
| `text` | Tweet content |
| `tweet_coord` | Tweet geo-coordinates |
| `tweet_created` | Timestamp of the tweet |
| `tweet_location` | User-provided location |
| `user_timezone` | User-provided timezone |

## Project Structure

```
├── assets/
│   └── dataset-cover.jpg              # README cover image
├── data/
│   ├── raw/
│   │   └── database.sqlite            # Original, unprocessed dataset
│   └── processed/
│       └── cleaned_database.sqlite    # Cleaned dataset
├── dashboard/
│   ├── app.py                         # Interactive Plotly Dash dashboard
│   ├── build_static.py                # Builds the static version in docs/
│   └── assets/style.css               # Dashboard styling
├── docs/                              # Static dashboard for GitHub Pages
│   ├── index.html
│   ├── app.js                         # Filters, charts and insights in the browser
│   ├── data.js                        # Aggregated counts (generated)
│   └── style.css / static.css
├── notebooks/
│   ├── 01_exploration.ipynb           # Initial data exploration
│   ├── 02_cleaning.ipynb              # Data cleaning
│   └── 03_visualize.ipynb             # Visualization and insights
├── requirements.txt
└── README.md
```

## Workflow

### 1. Exploration (`01_exploration.ipynb`)
Initial look at the raw dataset: shape, columns, data types, missing values, duplicates, and a first breakdown of tweet volume by airline and negative reason.

### 2. Cleaning (`02_cleaning.ipynb`)
- Normalized `tweet_location`: trimmed whitespace, standardized casing, removed trailing US states and countries, and merged common aliases (e.g. `"Boston, MA"` → `"Boston"`, `"NYC"` / `"Brooklyn"` → `"New York"`, `"Washington DC"` → `"Washington, D.C."`)
- Treated empty strings as missing values (`NaN`)
- Removed duplicate tweets (same `tweet_id`)
- Exported the cleaned data to `data/processed/cleaned_database.sqlite`

### 3. Visualization (`03_visualize.ipynb`)
- Overall sentiment distribution across all tweets
- Negative tweet volume by airline
- Top 5 reasons behind negative sentiment
- Top 3 tweet locations by volume

### 4. Dashboard (`dashboard/app.py`)
An interactive Plotly Dash dashboard on top of the cleaned database:
- **Filters** for date range, airlines, and sentiment that apply to every element on the page
- **Key figures:** tweet count, negative share, top complaint, most negative airline
- **Key insights:** plain-language takeaways that are recalculated whenever a filter changes
- **Charts:** sentiment mix by airline, reasons for negative tweets (top reason highlighted), tweets per day (peak day labeled), and top 10 locations
- **Table view** with the numbers behind the charts, sortable by any column
- **Design:** colors of the US flag (red = negative, blue = positive, silver = neutral) and the highly legible [Inter](https://rsms.me/inter/) typeface

### 5. Static dashboard for GitHub Pages (`docs/`)
GitHub Pages can only serve static files, not a Python server. `docs/` therefore contains a static version of the dashboard with the same filters, key figures, insights, charts, and table, built with [Plotly.js](https://plotly.com/javascript/) and running entirely in the browser.

`dashboard/build_static.py` aggregates the cleaned database into `docs/data.js`. It only exports counts per day, airline, sentiment, reason, and location – no tweet texts or user names. Re-run it whenever the cleaned data changes.

## Key Findings

- **Most tweets are complaints:** 62.7% of all tweets are negative, suggesting customers primarily turn to social media to voice problems rather than praise.
- **US Airways draws the most criticism:** 78% of its tweets are negative, followed by American (72%) and United (69%).
- **Virgin America keeps passengers happiest**, with the highest share of positive tweets (30%).
- **Customer service is complaint #1:** customer service issues (32%) and late flights (18%) together account for half of all negative feedback.
- **Complaints spiked on February 22** with 2,261 negative tweets, 2.2× the daily average.
- **New York** is the most common user location (806 tweets), ahead of Washington, D.C. (355) and Boston (254).

## Tech Stack

- Python
- pandas
- SQLite
- matplotlib / seaborn
- Plotly Dash

## Getting Started

### Data setup

The data files are not part of this repository (see `.gitignore`). Download `Tweets.csv` from the [Kaggle dataset](https://www.kaggle.com/datasets/welkin10/airline-sentiment), save it in the repository root, and convert it into the SQLite database the notebooks expect:

```bash
python -c "import pandas as pd, sqlite3, pathlib; pathlib.Path('data/raw').mkdir(parents=True, exist_ok=True); pd.read_csv('Tweets.csv').to_sql('Tweets', sqlite3.connect('data/raw/database.sqlite'), if_exists='replace', index=False)"
```

`02_cleaning.ipynb` then creates `data/processed/cleaned_database.sqlite`, which `03_visualize.ipynb` and the dashboard use.

### Installation and usage

```bash
# Clone the repository
git clone https://github.com/TranceMeli/Airline.git
cd Airline

# Install dependencies
pip install -r requirements.txt

# Run the notebooks in order (01 → 02 → 03)
jupyter notebook notebooks/01_exploration.ipynb

# Start the dashboard (after running 02_cleaning.ipynb)
python dashboard/app.py
# then open http://127.0.0.1:8050

# Rebuild the static dashboard in docs/
python dashboard/build_static.py

# Preview the static dashboard locally, then open http://127.0.0.1:8060
python -m http.server 8060 --directory docs
```

### Publishing on GitHub Pages

1. Commit `docs/` (including the generated `docs/data.js`) and push it to the `main` branch.
2. On GitHub, open **Settings → Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**, select `main` and the `/docs` folder, then click **Save**.
4. After a minute or two the dashboard is live at `https://trancemeli.github.io/Airline/`.
