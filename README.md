# Airline Sentiment Analysis

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge&logo=plotly&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-4C72B0?style=for-the-badge&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)

![Dataset Cover](assets/dataset-cover.jpg)

A data analysis project exploring customer sentiment toward major US airlines, based on tweets. The project covers data exploration, cleaning, and visualization using Python, pandas, and SQLite.

## Dataset

Source: [Airline Sentiment (Kaggle)](https://www.kaggle.com/datasets/welkin10/airline-sentiment)

The dataset contains **14,485 tweets** directed at six US airlines, each labeled with a sentiment (`positive`, `neutral`, or `negative`) and, where applicable, a reason for negative feedback.

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
├── data/
│   ├── raw/
│   │   └── database.sqlite            # Original, unprocessed dataset
│   └── processed/
│       └── cleaned_database.sqlite    # Cleaned dataset
├── notebooks/
│   ├── 01_exploration.ipynb           # Initial data exploration
│   ├── 02_cleaning.ipynb              # Data cleaning
│   └── 03_visualize.ipynb             # Visualization and insights
└── README.md
```

## Workflow

### 1. Exploration (`01_exploration.ipynb`)
Initial look at the raw dataset: shape, columns, data types, missing values, duplicates, and a first breakdown of tweet volume by airline and negative reason.

### 2. Cleaning (`02_cleaning.ipynb`)
- Trimmed whitespace and standardized casing in `tweet_location`
- Consolidated inconsistent location spellings (e.g. `"New York, NY"`, `"New York City"` → `"New York"`)
- Verified the dataset contains no missing values or duplicate rows
- Exported the cleaned data to `data/processed/cleaned_database.sqlite`

### 3. Visualization (`03_visualize.ipynb`)
- Overall sentiment distribution across all tweets
- Negative tweet volume by airline
- Top 5 reasons behind negative sentiment
- Top 3 tweet locations by volume

## Key Findings

- The dataset is dominated by **negative sentiment**, suggesting customers primarily turn to social media to voice complaints rather than praise.
- The leading causes of negative sentiment are **customer service issues** and **flight delays**, together accounting for a large share of all negative feedback.

## Tech Stack

- Python
- pandas
- SQLite
- matplotlib / seaborn

## Getting Started

```bash
# Clone the repository
git clone https://github.com/TranceMeli/<repo-name>.git

# Install dependencies
pip install pandas matplotlib seaborn

# Run the notebooks in order
jupyter notebook notebooks/01_exploration.ipynb
```

## Author

**Mel** ([@TranceMeli](https://github.com/TranceMeli))