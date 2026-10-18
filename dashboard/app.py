"""Interactive Plotly Dash dashboard for the airline sentiment data.

Run from the repository root (after 02_cleaning.ipynb has created the cleaned database):

    python dashboard/app.py

Then open http://127.0.0.1:8050 in your browser.
"""

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dash_table, dcc, html
from dash.dash_table.Format import Format, Group, Scheme

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "cleaned_database.sqlite"

# Colors of the US flag. Old Glory Blue is too dark for data marks,
# so it is used for the header, accents and text; marks use a brighter flag blue.
OLD_GLORY_RED = "#B22234"
OLD_GLORY_BLUE = "#3C3B6E"
FLAG_BLUE = "#3C5BA9"
SILVER = "#A7ABBA"

# Sentiment is a polarity: red and blue poles with a neutral silver midpoint
SENTIMENTS = ["negative", "neutral", "positive"]
SENTIMENT_COLORS = {"negative": OLD_GLORY_RED, "neutral": SILVER, "positive": FLAG_BLUE}
SERIES_COLOR = FLAG_BLUE

SURFACE = "#ffffff"
TEXT_PRIMARY = "#1b1a33"
TEXT_SECONDARY = "#55566e"
TEXT_MUTED = "#6b6c84"
GRID = "#e6e7ef"
BASELINE = "#c9cbd8"
# Inter: designed for on-screen legibility, with a plain (unslashed) zero
FONT = 'Inter, system-ui, -apple-system, "Segoe UI", sans-serif'
FONT_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"


def load_data():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"{DB_PATH} not found – run notebooks/02_cleaning.ipynb first (see README)."
        )
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """
        SELECT tweet_id, airline, airline_sentiment, negativereason,
               tweet_created, tweet_location
        FROM Tweets;
        """,
        conn,
    )
    conn.close()
    # "2015-02-24 11:35:52 -0800": keep the tweet's local date, ignore the offset
    df["date"] = pd.to_datetime(df["tweet_created"].str[:10])
    return df


DF = load_data()
# Fixed airline order (by total volume) so the charts never reshuffle when filtering
AIRLINES = DF["airline"].value_counts().index.tolist()
MIN_DATE, MAX_DATE = DF["date"].min().date(), DF["date"].max().date()


# ---------------------------------------------------------------- charts

def base_layout(fig, height=360):
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=16, t=8, b=8),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(family=FONT, color=TEXT_SECONDARY, size=14),
        hoverlabel=dict(bgcolor="white", bordercolor=BASELINE,
                        font=dict(family=FONT, color=TEXT_PRIMARY, size=14)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text="",
                    font=dict(color=TEXT_SECONDARY)),
    )
    fig.update_xaxes(gridcolor=GRID, linecolor=BASELINE, zeroline=False, tickfont_color=TEXT_MUTED,
                     title_font_color=TEXT_SECONDARY)
    fig.update_yaxes(gridcolor=GRID, linecolor=BASELINE, zeroline=False, tickfont_color=TEXT_MUTED,
                     title_font_color=TEXT_SECONDARY)
    return fig


def empty_figure(message="No data for this selection", height=360):
    fig = base_layout(go.Figure(), height)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.add_annotation(text=message, showarrow=False, font=dict(color=TEXT_MUTED, size=15))
    return fig


def sentiment_counts(df):
    return (
        df.groupby(["airline", "airline_sentiment"]).size()
        .unstack(fill_value=0)
        .reindex(index=[a for a in AIRLINES if a in df["airline"].unique()],
                 columns=SENTIMENTS, fill_value=0)
    )


def sentiment_by_airline(df):
    counts = sentiment_counts(df)
    if counts.empty:
        return empty_figure()
    shares = counts.div(counts.sum(axis=1), axis=0) * 100

    fig = go.Figure()
    for sentiment in SENTIMENTS:
        if counts[sentiment].sum() == 0:
            continue
        share = shares[sentiment]
        fig.add_bar(
            name=sentiment.capitalize(),
            y=shares.index,
            x=share,
            orientation="h",
            marker=dict(color=SENTIMENT_COLORS[sentiment], line=dict(color=SURFACE, width=2)),
            # Label only segments wide enough to hold the text
            text=[f"{v:.0f}%" if v >= 8 else "" for v in share],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="white" if sentiment != "neutral" else TEXT_PRIMARY, size=13),
            customdata=counts[sentiment],
            hovertemplate="<b>%{x:.1f}%</b> " + sentiment + " · %{customdata:,} tweets<extra>%{y}</extra>",
        )
    fig = base_layout(fig)
    fig.update_layout(barmode="stack", bargap=0.38, legend_traceorder="normal")
    fig.update_xaxes(ticksuffix="%", range=[0, 100], showgrid=False)
    fig.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(color=TEXT_SECONDARY, size=14))
    return fig


def negative_reasons(df):
    reasons = df["negativereason"].dropna().value_counts().sort_values()
    if reasons.empty:
        return empty_figure("No negative tweets in this selection")
    share = reasons / reasons.sum() * 100
    fig = go.Figure(go.Bar(
        y=reasons.index,
        x=reasons.values,
        orientation="h",
        # Emphasis: the top reason in red, the rest in blue
        marker=dict(color=[OLD_GLORY_RED if r == reasons.index[-1] else SERIES_COLOR for r in reasons.index],
                    line=dict(color=SURFACE, width=2)),
        text=[f"{s:.0f}%" for s in share],
        textposition="outside",
        textfont=dict(color=TEXT_SECONDARY),
        customdata=share,
        hovertemplate="<b>%{x:,} tweets</b> · %{customdata:.1f}%<extra>%{y}</extra>",
        cliponaxis=False,
    ))
    fig = base_layout(fig)
    fig.update_layout(bargap=0.3)
    fig.update_xaxes(title_text="Negative tweets", range=[0, reasons.max() * 1.15])
    fig.update_yaxes(showgrid=False, tickfont=dict(color=TEXT_SECONDARY))
    return fig


def tweets_over_time(df):
    daily = (
        df.groupby(["date", "airline_sentiment"]).size()
        .unstack(fill_value=0)
        .reindex(columns=SENTIMENTS, fill_value=0)
    )
    if daily.empty:
        return empty_figure()
    fig = go.Figure()
    for sentiment in SENTIMENTS:
        if daily[sentiment].sum() == 0:
            continue
        fig.add_scatter(
            name=sentiment.capitalize(),
            x=daily.index,
            y=daily[sentiment],
            mode="lines+markers",
            line=dict(color=SENTIMENT_COLORS[sentiment], width=2),
            marker=dict(size=8, line=dict(color=SURFACE, width=2)),
            hovertemplate="<b>%{y:,}</b> " + sentiment + "<extra></extra>",
        )
    fig = base_layout(fig)
    fig.update_layout(hovermode="x unified")

    # Selective direct label: the busiest day of the leading series
    lead = "negative" if daily["negative"].sum() else daily.sum().idxmax()
    peak_day = daily[lead].idxmax()
    fig.add_annotation(
        x=peak_day, y=daily.loc[peak_day, lead],
        text=f"<b>Peak</b> · {daily.loc[peak_day, lead]:,} on {peak_day:%b %d}",
        showarrow=True, arrowhead=0, arrowcolor=BASELINE, ax=0, ay=-28,
        font=dict(color=TEXT_PRIMARY, size=13), bgcolor="white", bordercolor=BASELINE, borderpad=4,
    )
    fig.update_xaxes(showgrid=False, tickformat="%b %d", dtick="D1", showspikes=True,
                     spikemode="across", spikethickness=1, spikecolor=BASELINE, spikedash="solid")
    fig.update_yaxes(title_text="Tweets per day", rangemode="tozero")
    return fig


def top_locations(df, n=10):
    locations = df["tweet_location"].dropna().value_counts().head(n).sort_values()
    if locations.empty:
        return empty_figure()
    fig = go.Figure(go.Bar(
        y=locations.index,
        x=locations.values,
        orientation="h",
        marker=dict(color=SERIES_COLOR, line=dict(color=SURFACE, width=2)),
        text=[f"{v:,}" for v in locations.values],
        textposition="outside",
        textfont=dict(color=TEXT_SECONDARY),
        hovertemplate="<b>%{x:,} tweets</b><extra>%{y}</extra>",
        cliponaxis=False,
    ))
    fig = base_layout(fig)
    fig.update_layout(bargap=0.3)
    fig.update_xaxes(title_text="Tweets", range=[0, locations.max() * 1.15])
    fig.update_yaxes(showgrid=False, tickfont=dict(color=TEXT_SECONDARY))
    return fig


def summary_table(df):
    counts = sentiment_counts(df)
    counts["total"] = counts.sum(axis=1)
    counts["negative_share"] = (counts["negative"] / counts["total"] * 100).round(1)
    return counts.reset_index().to_dict("records")


# ---------------------------------------------------------------- insights

def insight(icon, title, body, tone):
    return html.Div(className=f"insight insight-{tone}", children=[
        html.Div(icon, className="insight-icon", **{"aria-hidden": "true"}),
        html.Div([html.Div(title, className="insight-title"), html.P(body)]),
    ])


def build_insights(df):
    """Plain-language takeaways that update with the filters."""
    if df.empty:
        return [insight("★", "No data", "Widen the filters to see insights.", "blue")]

    boxes = []
    counts = sentiment_counts(df)
    shares = counts.div(counts.sum(axis=1), axis=0) * 100
    negative = df[df["airline_sentiment"] == "negative"]

    if not negative.empty and len(shares) > 1:
        worst = shares["negative"].idxmax()
        overall = len(negative) / len(df) * 100
        boxes.append(insight(
            "▼", f"{worst} draws the most criticism",
            [html.B(f"{shares.loc[worst, 'negative']:.0f}%"), " of its tweets are negative – ",
             html.B(f"{shares.loc[worst, 'negative'] - overall:.0f} points"), f" above the average of {overall:.0f}%."],
            "red",
        ))

    reasons = negative["negativereason"].dropna().value_counts()
    if len(reasons) >= 2:
        top_share = reasons.iloc[0] / reasons.sum() * 100
        both_share = reasons.iloc[:2].sum() / reasons.sum() * 100
        boxes.append(insight(
            "⚑", f"{reasons.index[0]} is complaint #1",
            [html.B(f"{top_share:.0f}%"), " of all complaints. Together with ", reasons.index[1],
             " it accounts for ", html.B(f"{both_share:.0f}%"), "."],
            "red",
        ))

    if not negative.empty and negative["date"].nunique() > 1:
        per_day = negative.groupby("date").size()
        peak = per_day.idxmax()
        boxes.append(insight(
            "▲", f"Complaints spiked on {peak:%b %d}",
            [html.B(f"{per_day.max():,}"), " negative tweets – ",
             html.B(f"{per_day.max() / per_day.mean():.1f}×"), " the daily average."],
            "blue",
        ))

    if counts["positive"].sum() and len(shares) > 1:
        best = shares["positive"].idxmax()
        boxes.append(insight(
            "★", f"{best} keeps passengers happiest",
            ["The highest positive share: ", html.B(f"{shares.loc[best, 'positive']:.0f}%"),
             f" of its tweets are positive."],
            "blue",
        ))

    return boxes or [insight("★", "Not enough data", "Select more airlines or sentiments.", "blue")]


# ---------------------------------------------------------------- layout

def stat_tile(label, value_id, tone):
    return html.Div(className=f"tile tile-{tone}", children=[
        html.Div(label, className="tile-label"),
        html.Div(id=value_id, className="tile-value"),
    ])


def card(title, subtitle, graph_id):
    return html.Div(className="card", children=[
        html.H2(title),
        html.P(subtitle, className="card-subtitle"),
        dcc.Graph(id=graph_id, config={"displayModeBar": False}),
    ])


app = Dash(__name__, title="Airline Sentiment Dashboard", external_stylesheets=[FONT_URL])

app.layout = html.Div([
    html.Header(className="hero", children=[
        html.Div(className="hero-inner", children=[
            html.Div("★ ★ ★", className="hero-stars", **{"aria-hidden": "true"}),
            html.H1("US Airline Sentiment"),
            html.P(f"How {len(DF):,} travelers talked about six US airlines on Twitter · "
                   f"{MIN_DATE:%b %d} – {MAX_DATE:%b %d, %Y}"),
        ]),
    ]),
    html.Div(className="stripes", **{"aria-hidden": "true"}),

    html.Main(className="page", children=[
        # One filter row that scopes everything below it
        html.Div(className="filters", children=[
            html.Div(className="filter", children=[
                html.Label("Date range", htmlFor="date-range"),
                dcc.DatePickerRange(
                    id="date-range",
                    min_date_allowed=MIN_DATE, max_date_allowed=MAX_DATE,
                    start_date=MIN_DATE, end_date=MAX_DATE,
                    display_format="MMM D, YYYY",
                ),
            ]),
            html.Div(className="filter filter-wide", children=[
                html.Label("Airlines", htmlFor="airline-filter"),
                dcc.Dropdown(
                    id="airline-filter",
                    options=[{"label": a, "value": a} for a in AIRLINES],
                    value=AIRLINES, multi=True, placeholder="All airlines",
                ),
            ]),
            html.Div(className="filter", children=[
                html.Label("Sentiment"),
                dcc.Checklist(
                    id="sentiment-filter",
                    options=[{"label": s.capitalize(), "value": s} for s in SENTIMENTS],
                    value=SENTIMENTS, inline=True, className="checklist",
                ),
            ]),
        ]),

        html.Div(className="tiles", children=[
            stat_tile("Tweets", "kpi-tweets", "blue"),
            stat_tile("Negative share", "kpi-negative", "red"),
            stat_tile("Top complaint", "kpi-reason", "blue"),
            stat_tile("Most negative airline", "kpi-airline", "red"),
        ]),

        html.Section(className="insights-section", children=[
            html.H2("Key insights", className="section-title"),
            html.Div(id="insights", className="insights"),
        ]),

        html.Div(className="grid", children=[
            card("Sentiment mix by airline", "Share of each airline's tweets", "chart-sentiment"),
            card("Why passengers complain", "Reasons given in negative tweets", "chart-reasons"),
            card("Tweets per day", "Daily volume by sentiment", "chart-time"),
            card("Where tweets come from", "Top 10 user locations", "chart-locations"),
        ]),

        html.Div(className="card", children=[
            html.H2("The numbers behind the charts"),
            html.P("Tweets by airline and sentiment – click a header to sort", className="card-subtitle"),
            dash_table.DataTable(
                id="summary-table",
                columns=[
                    {"name": "Airline", "id": "airline"},
                    {"name": "Negative", "id": "negative", "type": "numeric", "format": Format().group(Group.yes)},
                    {"name": "Neutral", "id": "neutral", "type": "numeric", "format": Format().group(Group.yes)},
                    {"name": "Positive", "id": "positive", "type": "numeric", "format": Format().group(Group.yes)},
                    {"name": "Total", "id": "total", "type": "numeric", "format": Format().group(Group.yes)},
                    {"name": "Negative share (%)", "id": "negative_share", "type": "numeric",
                     "format": Format(precision=1, scheme=Scheme.fixed)},
                ],
                sort_action="native",
                style_as_list_view=True,
                style_cell={"fontFamily": FONT, "padding": "10px 14px", "textAlign": "right",
                            "backgroundColor": SURFACE, "color": TEXT_PRIMARY, "fontSize": "15px",
                            "border": f"1px solid {GRID}", "fontVariantNumeric": "tabular-nums"},
                style_cell_conditional=[{"if": {"column_id": "airline"}, "textAlign": "left",
                                         "fontWeight": "600"}],
                style_header={"fontWeight": "600", "color": "white", "backgroundColor": OLD_GLORY_BLUE,
                              "border": f"1px solid {OLD_GLORY_BLUE}"},
                style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "#f6f7fb"}],
            ),
        ]),

        html.Footer("Data: Airline Sentiment (Kaggle) · Built with Plotly Dash"),
    ]),
])


@app.callback(
    Output("kpi-tweets", "children"),
    Output("kpi-negative", "children"),
    Output("kpi-reason", "children"),
    Output("kpi-airline", "children"),
    Output("insights", "children"),
    Output("chart-sentiment", "figure"),
    Output("chart-reasons", "figure"),
    Output("chart-time", "figure"),
    Output("chart-locations", "figure"),
    Output("summary-table", "data"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("airline-filter", "value"),
    Input("sentiment-filter", "value"),
)
def update(start_date, end_date, airlines, sentiments):
    airlines = airlines or AIRLINES  # an empty dropdown means "all airlines"
    df = DF[
        DF["date"].between(pd.Timestamp(start_date or MIN_DATE), pd.Timestamp(end_date or MAX_DATE))
        & DF["airline"].isin(airlines)
        & DF["airline_sentiment"].isin(sentiments or [])
    ]

    total = len(df)
    negative = df["airline_sentiment"].eq("negative")
    reasons = df["negativereason"].dropna()
    by_airline = negative.groupby(df["airline"]).mean()

    kpi_tweets = f"{total:,}"
    kpi_negative = f"{negative.mean() * 100:.1f}%" if total else "–"
    kpi_reason = reasons.value_counts().index[0] if not reasons.empty else "–"
    kpi_airline = (f"{by_airline.idxmax()} ({by_airline.max() * 100:.0f}%)"
                   if negative.any() else "–")

    return (
        kpi_tweets, kpi_negative, kpi_reason, kpi_airline,
        build_insights(df),
        sentiment_by_airline(df), negative_reasons(df), tweets_over_time(df), top_locations(df),
        summary_table(df),
    )


if __name__ == "__main__":
    app.run(debug=False)
