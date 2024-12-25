import sqlite3
import pandas as pd
import plotly.express as px
import logging
import os
import sys
from typing import List
from dash import Dash, dcc, html, Input, Output

# Add the parent directory of 'database_admin' to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_admin.sqlite_manager import SQLiteDatabase  # To manage sqlite operations
from database_admin.sqlite_manager import load_queries_from_json  # Run list of queries from json file

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def fetch_data_from_sqlite(db_path: str, query_path: str) -> pd.DataFrame:
    """
    Fetch data from an SQLite database.

    :param db_path: Path to the SQLite database file.
    :param query: SQL query to execute.
    :return: A Pandas DataFrame with the query results.
    """
    db = SQLiteDatabase(db_path)
    
    try:
        # Running queries
        query_list = load_queries_from_json(query_path)
            
        data = db.execute_query(query_list[2]["query"]) # Execute select

        # Convert to DataFrame
        df = pd.DataFrame(data, columns=['text_post', 'created_at', 'author', 'uri', 'has_images', 'reply_to'])

        return df
    except Exception as e:
        logging.error("Error occurred during load: %s", e)
        raise
    finally:
        db.close()

def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the data for visualization.

    :param data: The raw data as a Pandas DataFrame.
    :return: Preprocessed data with additional columns.
    """
    data["created_at"] = pd.to_datetime(data["created_at"], errors="coerce", utc=True)
    data["date"] = data["created_at"].dt.date  # Extract date
    data["hashtags"] = data["text_post"].apply(extract_hashtags)
    return data

def extract_hashtags(text: str) -> List[str]:
    """
    Extract hashtags from a text post.

    :param text: The text of the post.
    :return: A list of hashtags in the text.
    """
    return [word for word in str(text).split() if word.startswith("#")]

def create_dashboard(data: pd.DataFrame) -> Dash:
    """
    Create a Dash app for visualizing the data with a date filter.

    :param data: The preprocessed data as a Pandas DataFrame.
    :return: A Dash app instance.
    """
    app = Dash(__name__)

    # List of unique dates for the dropdown
    unique_dates = data["date"].sort_values().unique()

    # Dash App Layout
    app.layout = html.Div([
        html.H1("Bluesky Posts Dashboard"),
        html.Div([
            html.Label("Select a Date:"),
            dcc.Dropdown(
                id="date-filter",
                options=[{"label": str(date), "value": str(date)} for date in unique_dates],
                placeholder="Select a date",
                value=None  # Default to no filtering
            ),
        ]),
        dcc.Graph(id="posts-per-day"),
        dcc.Graph(id="top-authors"),
        dcc.Graph(id="top-topics"),
    ])

    # Callback to update the visualizations based on the selected date
    @app.callback(
        [
            Output("posts-per-day", "figure"),
            Output("top-authors", "figure"),
            Output("top-topics", "figure"),
        ],
        [Input("date-filter", "value")]
    )
    def update_visualizations(selected_date: str):
        """
        Update visualizations based on the selected date.

        :param selected_date: The selected date as a string.
        :return: Updated figures for the dashboard.
        """
        if selected_date:
            filtered_data = data[data["date"] == pd.to_datetime(selected_date).date()]
        else:
            filtered_data = data

        # Posts Per Day
        posts_per_day = filtered_data.groupby("date").size().reset_index(name="post_count")
        posts_per_day_fig = px.line(
            posts_per_day, x="date", y="post_count",
            labels={"date": "Date", "post_count": "Posts"},
            title="Posts Per Day"
        )

        # Top Authors
        top_authors = filtered_data["author"].value_counts().head(10)
        top_authors_fig = px.bar(
            x=top_authors.index, y=top_authors.values,
            labels={"x": "Author", "y": "Post Count"},
            title="Top Authors by Number of Posts"
        )

        # Top Topics Per Day
        topics_per_day = (
            filtered_data.explode("hashtags")
            .dropna(subset=["hashtags"])
            .groupby(["date", "hashtags"])
            .size()
            .reset_index(name="count")
        )
        top_topics_fig = px.treemap(
            topics_per_day, path=["date", "hashtags"], values="count",
            title="Top Topics Per Day"
        )

        return posts_per_day_fig, top_authors_fig, top_topics_fig

    return app

if __name__ == "__main__":
    # Compute the absolute path to the JSON file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    query_file_path = os.path.join(
        script_dir, "../database_admin/query_files/bluesky_daily.json"
    )
    if not os.path.exists(query_file_path):
        raise FileNotFoundError(f"The file was not found at {query_file_path}")

    database_path = os.path.join(
        script_dir, "../database_admin/database_files/bluesky_posts.db"
    )
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"The file was not found at {database_path}")

    logging.info("Running dashboard")
    raw_data = fetch_data_from_sqlite(database_path, query_file_path)
    preprocessed_data = preprocess_data(raw_data)

    # Create and run the dashboard
    dashboard_app = create_dashboard(preprocessed_data)

    logging.debug("Starting the Dash app on port 8050...")
    if not dashboard_app.layout:
        logging.error("Dash layout is not set. The server cannot render any pages.")
    else:
        dashboard_app.run(host='127.0.0.1', port='8050', proxy=None, debug=True)