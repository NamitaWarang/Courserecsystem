
import streamlit as st
# Load EDA
import pandas as pd 
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
# Add numpy import
import numpy as np
import pyrebase
from datetime import datetime
import json
import functools
import requests
import random
from streamlit_option_menu import option_menu

#Configuration key
firebaseConfig = {
    'apiKey': "AIzaSyCZPtwe0V9lMRTqUEqDcPKFALHwlefAmho",
    'authDomain': "courserecsystem-9a84c.firebaseapp.com",
    'projectId': "courserecsystem-9a84c",
    'databaseURL': "https://courserecsystem-9a84c-default-rtdb.europe-west1.firebasedatabase.app/",
    'storageBucket': "courserecsystem-9a84c.appspot.com",
    'messagingSenderId': "149618883518",
    'appId': "1:149618883518:web:0d6c9b123973bf5e1cd7ef",
    'measurementId': "G-YCFDDD2VLR"
}


firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

st.set_page_config(initial_sidebar_state="collapsed")
query_params = st.experimental_get_query_params()
user_id = query_params['user_id'][0] if 'user_id' in query_params else None

# Initialize session state
if 'interested_courses' not in st.session_state:
    st.session_state.interested_courses = []

# Initialize courses variable
if 'courses' not in st.session_state:
    st.session_state.courses = []

# Load your dataset
def load_data(data):
    df = pd.read_csv(data)
    return df

def vectorize_text_to_cosine_mat(data):
    count_vect = CountVectorizer()
    data.fillna("", inplace=True)
    cv_mat = count_vect.fit_transform(data['course_title'])
    cosine_sim_mat = cosine_similarity(cv_mat)
    return cosine_sim_mat

def get_recommendation(title, cosine_sim_mat, df, num_of_rec=10):
    specific_course_index = df[df['course_title'] == title].index[0]
    sim_scores = cosine_sim_mat[specific_course_index]
    sorted_indices = list(reversed(sim_scores.argsort()))
    recommended_indices = [idx for idx in sorted_indices if idx != specific_course_index]
    recommended_courses = df.iloc[recommended_indices]
    return recommended_courses.head(num_of_rec)

def search_term_if_not_found(search_term, df):
    search_results = df[df['subject'].str.contains(search_term, case=False) | df['course_title'].str.contains(search_term, case=False)]
    return search_results

def fb(course_title):
    ref = db.child('history').push({
        "user_id": user_id,
        "course_title": course_title
    })

def display_course_cards(data, key):
    for idx, row in data.iterrows():
        st.write(f"**Course Title:** {row['course_title']}")
        st.write(f"**Link:** [{row['url']}]({row['url']})")
        st.write(f"**Is paid?:** {row['is_paid']}")
        st.write(f"**Level:** {row['level']}")
        st.write(f"**Subject:** {row['subject']}")
        st.write(f"**Language:** {row['language']}")
        button_key = f"interested_button_{idx}_{key}"
        on_click = lambda course_title=row['course_title'], key=key: on_interested_button_click(course_title, key)
        if st.button('Interested', key=button_key, on_click=on_click):
            pass

def on_interested_button_click(course_title, key):
    st.session_state.interested_courses.append(course_title)
    # Update the courses variable with the interested course
    st.session_state.courses.append(course_title)
    fb(course_title)

def app():
    st.markdown("<h1 style='text-align: center; color: purple;'>Course Dekho</h1>", unsafe_allow_html=True)

    menu = option_menu(None, ["Home", "Search"], 
    icons=['house','search'], 
    menu_icon="cast", orientation="horizontal")
    
    df = load_data("data/course_data.csv")

    if menu == "Home":
        st.subheader("Home")
        st.markdown("<h3 style='text-align: left; color: purple;'>Recommended Courses:</h3>", unsafe_allow_html=True)
        recommendations_placeholder = st.empty()

        if user_id:
            url = f"{firebaseConfig['databaseURL']}/history.json"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                course_titles = []

                for key, value in data.items():
                    if "user_id" in value and value["user_id"] == user_id and "course_title" in value:
                        course_titles.append(value["course_title"])

                if course_titles:
                    for title in course_titles:
                        st.write(title)
                        cosine_sim_mat = vectorize_text_to_cosine_mat(df)
                        recommendations = get_recommendation(title, cosine_sim_mat, df, 3)
                        key = title.replace(" ", "_").replace(":", "").replace("/", "")
                        display_course_cards(recommendations, key)

                else:
                    st.write("Please search for a wide variety of courses on Course Dekho from the dropdown!")

            else:
                st.write("Failed to retrieve data from the Firebase Realtime Database.")

    if menu == "Search":
        st.markdown("<h3 style='text-align: left; color: purple;'>Search for courses</h3>", unsafe_allow_html=True)

        search_term = st.text_input("Search")
        if st.button("Search"):
            if search_term is not None:
                st.info("Suggested Options include")

                result_df = search_term_if_not_found(search_term, df)
                if not result_df.empty:
                    display_course_cards(result_df, search_term)
                else:
                    st.write("No matching courses found.")

if __name__ == '__main__':
    app()