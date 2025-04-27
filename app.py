import streamlit as st
import pickle
import pandas as pd
import requests
import py7zr
import os
if not os.path.exists('pkl_file'):
    os.makedirs('pkl_file')

# Extract the 7z file
with py7zr.SevenZipFile('similarity.pkl.7z', mode='r') as archive:
    archive.extractall(path=os.path.join(os.getcwd(), 'pkl_file'))  # Full path to pkl_file directory

# Now try loading the file again
similarity = pickle.load(open(os.path.join(os.getcwd(), 'pkl_file', 'similarity.pkl'), 'rb'))

# --- Step 2: Load your files ---
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
# similarity = pickle.load(open('pkl_file/similarity.pkl', 'rb'))  # Load from extracted location

# --- Step 3: Define functions ---
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

movies = pd.DataFrame(movies_dict)

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distance = similarity[movie_index]
    movie_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]
    recommendation = []
    recommendation_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommendation.append(movies.iloc[i[0]].title)
        recommendation_posters.append(fetch_poster(movie_id))
    return recommendation, recommendation_posters

# --- Step 4: Streamlit app ---
st.title("Recommender System")

selected_movies_name = st.selectbox("Select your movie", movies['title'].values)

if st.button('Show Recommendation'):
    recommendation, recommendation_posters = recommend(selected_movies_name)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(recommendation[0])
        st.image(recommendation_posters[0])
    with col2:
        st.text(recommendation[1])
        st.image(recommendation_posters[1])
    with col3:
        st.text(recommendation[2])
        st.image(recommendation_posters[2])
    with col4:
        st.text(recommendation[3])
        st.image(recommendation_posters[3])
    with col5:
        st.text(recommendation[4])
        st.image(recommendation_posters[4])
