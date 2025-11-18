import os
import pickle
import streamlit as st
import requests
import random
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Function to fetch poster
def fetch_poster(movie_id):
    try:
        if not movie_id or pd.isna(movie_id):
            return "https://via.placeholder.com/150"
        url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        poster_path = data.get('poster_path', '')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    except Exception:
        # Any issue (network, parsing, missing id) -> fallback placeholder
        return "https://via.placeholder.com/150"
    return "https://via.placeholder.com/150"

# Function to recommend movies
def recommend(movie):
    # Guard against missing data
    if similarity.size == 0 or movie not in movies['title'].values:
        return [], []
    try:
        index = movies[movies['title'] == movie].index[0]
    except Exception:
        return [], []
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        try:
            movie_id = movies.iloc[i[0]].movie_id
        except Exception:
            movie_id = None
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters


# Streamlit App
st.set_page_config(page_title="Movie Recommender", layout="wide", initial_sidebar_state="expanded")

# Add a banner image
st.image("https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/f562aaf4-5dbb-4603-a32b-6ef6c2230136/dh0w8qv-9d8ee6b2-b41a-4681-ab9b-8a227560dc75.jpg/v1/fill/w_1280,h_720,q_75,strp/the_netflix_login_background__canada__2024___by_logofeveryt_dh0w8qv-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9NzIwIiwicGF0aCI6IlwvZlwvZjU2MmFhZjQtNWRiYi00NjAzLWEzMmItNmVmNmMyMjMwMTM2XC9kaDB3OHF2LTlkOGVlNmIyLWI0MWEtNDY4MS1hYjliLThhMjI3NTYwZGM3NS5qcGciLCJ3aWR0aCI6Ijw9MTI4MCJ9XV0sImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl19.LOYKSxIDqfPwWHR0SSJ-ugGQ6bECF0yO6Cmc0F26CQs", use_column_width=True)

st.title("Movie Recommender System")
st.markdown("""
Welcome to the **Movie Recommender System**!  
Select a movie from the dropdown or search for it to get personalized recommendations.
""")

# Load data (try pickles first; if not available, build from CSV in the repo)
data_dir = os.path.dirname(__file__)
movie_list = []
try:
    movies = pickle.load(open(os.path.join(data_dir, 'movie_list.pkl'), 'rb'))
    similarity = pickle.load(open(os.path.join(data_dir, 'similarity.pkl'), 'rb'))
    # If movies is a dict-like with 'title' key (previous implementation), keep compatibility
    if hasattr(movies, 'columns'):
        movie_list = movies['title'].values
    else:
        movie_list = movies['title'].values
except Exception:
    # Fallback: build minimal dataset from tmdb_5000_movies.csv included in the repo
    try:
        df = pd.read_csv(os.path.join(data_dir, 'tmdb_5000_movies.csv'))
        df['overview'] = df['overview'].fillna('')
        # Create a movies DataFrame compatible with the rest of the code
        movies = df.rename(columns={'id': 'movie_id'})[['movie_id', 'title', 'overview']]
        # Build a simple similarity matrix using the movie overviews
        cv = CountVectorizer(stop_words='english')
        vectors = cv.fit_transform(movies['overview'])
        similarity = cosine_similarity(vectors)
        movie_list = movies['title'].values
    except FileNotFoundError:
        # No data available — keep empty lists and show helpful message in UI
        movies = pd.DataFrame(columns=['movie_id', 'title', 'overview'])
        similarity = np.array([[]])
        movie_list = []

# If no data was loaded, show a helpful message and stop further UI rendering
if len(movie_list) == 0:
    st.sidebar.warning("No movie data found. Place 'tmdb_5000_movies.csv' or precomputed 'movie_list.pkl' and 'similarity.pkl' in the project root.")
    st.warning("No movie data available. The app cannot provide recommendations until data files are available.")
    st.stop()

# Sidebar for user input
st.sidebar.title("Search and Recommend")
selected_movie = st.sidebar.selectbox("Type or select a movie:", movie_list)

# Show recommendations button
if st.sidebar.button('Show Recommendations'):
    with st.spinner("Fetching recommendations..."):
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    st.markdown("### Recommended Movies")
    cols = st.columns(5)  # Display recommendations in 5 columns
    for idx, col in enumerate(cols):
        with col:
            # If recommendations are shorter than 5, guard index access
            if idx < len(recommended_movie_posters):
                st.image(recommended_movie_posters[idx], caption=recommended_movie_names[idx], use_container_width=True)

    # Add ratings and genres (placeholder values for now)
    st.markdown("### Details for Recommended Movies")
    for idx, name in enumerate(recommended_movie_names):
        with st.expander(f"Details for {name}"):
            st.write(f"**Genre:** Action/Adventure | **Rating:** 8.{idx+1}/10")
            st.write("**Description:** A thrilling story of...")

# Random Movie Button
if st.sidebar.button("Random Movie"):
    if movie_list:
        random_movie = random.choice(movie_list)
        st.sidebar.markdown(f"🎥 How about trying **{random_movie}**?")
    else:
        st.sidebar.markdown("No movies available to pick from.")

# Footer
st.markdown("---")
st.markdown("💡 **Pro Tip**: Use the search bar in the sidebar for quick access to movies!")
