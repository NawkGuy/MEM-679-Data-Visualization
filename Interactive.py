import panel as pn
import numpy as np
from matplotlib.figure import Figure
import hvplot.pandas
import pandas as pd

pn.extension("tabulator")

ACCENT = "#db0000"

styles = {
    "box-shadow": "rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px",
    "border-radius": "4px",
    "padding": "10px",
}

# Load Data
@pn.cache()  
def get_data():
    return pd.read_csv(r'C:/Users/Admin/OneDrive/Documents/Drexel/MEM679/Homework3/netflix_titles.csv')
source_data = get_data()

# Data Processing
min_year = int(source_data['release_year'].min())
max_year = int(source_data['release_year'].max())

source_data["country"] = source_data["country"].fillna("") # Replace NaN values with an empty string
source_data["rating"] = source_data["rating"].fillna("")
source_data["listed_in"] = source_data["listed_in"].fillna("")

source_data = source_data[source_data['country'] != ''] # Exclude data with blank values
source_data = source_data[source_data['rating'] != '']
source_data = source_data[source_data['listed_in'] != '']

source_data['regions'] = source_data['country'].str.split(", ") # Split columns with multiple category entries into list
source_data['genres'] = source_data['listed_in'].str.split(", ") 

regions_exploded = source_data.explode('regions') # Explode lists to create a row for each genre
genres_exploded = source_data.explode('genres')

# Filters
fil_format = pn.widgets.Select(
    name = "Format",
    value = "Movie",
    options=["Any", "Movie", "TV Show"],
    description="Available Movies or TV Shows",
)
fil_country = pn.widgets.Select(
    name = "Country",
    value = "United States",
    options=["Any"] + sorted(regions_exploded["regions"].unique().tolist()),  
    description="Country of Production",
)
fil_rating = pn.widgets.Select(
    name = "Rating",
    value = "Any",
    options=["Any"] + sorted(source_data["rating"].unique().tolist()), 
    description="MPAA Film Rating",
)
fil_genre = pn.widgets.Select(
    name = "Genre",
    value = "Action & Adventure",
    options=["Any"] + sorted(genres_exploded["genres"].unique().tolist()), 
    description="Movie or TV Show Category",
)
r_year = pn.widgets.IntSlider(name="Year", value=max_year, start=min_year, end=max_year)

# Function to filter data based on widget values
def filter_data(format, country, rating, genre, r_year):
    filtered_data = source_data[
        ((source_data['type'] == format) | (format == "Any")) &
        ((source_data['country'].str.contains(country)) | (country == "Any")) &
        ((source_data['rating'] == rating) | (rating == "Any")) &
        ((source_data['listed_in'].apply(lambda x: genre in x)) | (genre == "Any")) &
        (source_data['release_year'] == r_year)
    ]
    return filtered_data[['title', 'description']].values.tolist()

# Create a Panel layout to display the filtered movie titles
filtered_titles = pn.bind(filter_data, fil_format, fil_country, fil_rating, fil_genre, r_year)
titles_panel = pn.Column(
    pn.pane.Markdown("# Search Results"),
    pn.bind(lambda titles: pn.pane.Markdown("\n".join([f"## {title}\n{description}" for title, description in titles])), filtered_titles)
)
image = pn.pane.JPG(r'C:/Users/Admin/OneDrive/Documents/Drexel/MEM679/Homework3/BrandAssets_Logos_01-Wordmark.jpg', width = 300)

pn.template.FastListTemplate(
    title="Netflix Movie and TV Show Listings",
    sidebar=[image, fil_format, fil_country, fil_rating, fil_genre, r_year],
    main=[titles_panel],
    main_layout=None,
    header_background="#000000",
    header_color=ACCENT,
    accent=ACCENT,
).servable()