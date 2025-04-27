import streamlit as st
import pickle
import pandas as pd
import requests
import os
import py7zr

# Step 1: Extract the 7z archive if needed
def extract_similarity():
    if not os.path.exists('similarity.pkl'):
        st.info('Extracting similarity.pkl from similarity.pkl.7z...')
        with py7zr.SevenZipFile('similarity.pkl.7z', mode='r') as archive:
            archive.extractall()


# Step 2: Load the movie data and similarity matrix
def load_data():
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies_dict, similarity

# Step 3: Fetch Poster Function
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url)
    if data.status_code == 200:  # Check if the request was successful
        data = data.json()
        poster_path = data.get('poster_path')  # Use .get() to avoid KeyError
        if poster_path:  # Check if poster_path exists
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        else:
            st.warning("Poster not found for this movie.")
            return None
    else:
        st.error("Failed to fetch movie data.")
        return None

# Step 4: Recommend Function
def recommend(movie, movies, similarity):
    movie_index = movies[movies['title'] == movie].index[0]
    distance = similarity[movie_index]
    movie_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]

    recommendation = []
    recommendation_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommendation.append(movies.iloc[i[0]].title)
        poster = fetch_poster(movie_id)
        if poster:  # Only append if the poster was successfully fetched
            recommendation_posters.append(poster)
        else:
            recommendation_posters.append(None)  # Append None if no poster found
    return recommendation, recommendation_posters

# Step 5: Main App
st.title("🎬 Movie Recommender System")

# First extract similarity.pkl if not already extracted
extract_similarity()

# Load the data
movies_dict, similarity = load_data()
movies = pd.DataFrame(movies_dict)

# User input
selected_movies_name = st.selectbox("Select your movie", movies['title'].values)

if st.button('Show Recommendation'):
    recommendation, recommendation_posters = recommend(selected_movies_name, movies, similarity)

    col1, col2, col3, col4, col5 = st.columns(5)
    for i in range(5):
        with eval(f'col{i+1}'):  # Dynamically access columns
            if recommendation_posters[i]:  # Check if poster exists
                st.text(recommendation[i])
                st.image(recommendation_posters[i])
            else:
                st.text(recommendation[i])
                st.text("No poster available.")