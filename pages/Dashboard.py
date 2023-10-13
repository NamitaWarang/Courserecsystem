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



# st.set_page_config(initial_sidebar_state="collapsed")
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
auth = firebase.auth()  

db = firebase.database()
storage = firebase.storage()


st.set_page_config(initial_sidebar_state="collapsed") 
query_params = st.experimental_get_query_params()
user_id = query_params['user_id'][0] if 'user_id' in query_params else None
# user = query_params['user'][0] if 'user' in query_params else None

# Initialize session state
if 'interested_courses' not in st.session_state:
    st.session_state.interested_courses = []


if user_id is not None:
    st.write(f"User ID from URL: {user_id}")

# Load your dataset
def load_data(data):
    df = pd.read_csv(data)
    return df

def vectorize_text_to_cosine_mat(data, title):
    count_vect = CountVectorizer()

    # Replace np.nan values with empty strings
    data.fillna("", inplace=True)

    cv_mat = count_vect.fit_transform(data['course_title'])

    # Compute the cosine similarity between all courses
    cosine_sim_mat = cosine_similarity(cv_mat)

    return cosine_sim_mat

# Function to get recommendations using cosine similarity
def get_recommendation(title, cosine_sim_mat, df, num_of_rec=10):
    # Get the index of the specific course
    specific_course_index = df[df['course_title'] == title].index[0]

    # Get the cosine similarity scores for the specific course
    sim_scores = cosine_sim_mat[specific_course_index]

    # Sort the courses by similarity score in descending order and exclude the specific course
    sorted_indices = np.argsort(sim_scores)[::-1]
    recommended_indices = [idx for idx in sorted_indices if idx != specific_course_index]
    recommended_courses = df.iloc[recommended_indices]

    return recommended_courses.head(num_of_rec)

    # Get the dataframe & title
    # result_df = df.iloc[selected_course_indices]
    # result_df['similarity_score'] = selected_course_scores
    # final_recommended_courses = result_df[['course_title', 'similarity_score', 'url']]
    # return final_recommended_courses



# Function to get recommendations using cosine similarity
# def get_recommendation(title, cosine_sim_mat, df, num_of_rec=10):
#     # indices of the course
#     course_indices = pd.Series(df.index, index=df['course_title']).drop_duplicates()
#     # Index of course
#     idx = course_indices[title]

#     # Look into the cosine matrix for that index
#     sim_scores = list(enumerate(cosine_sim_mat[idx]))
#     sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
#     selected_course_indices = [i[0] for i in sim_scores[1:num_of_rec + 1]]
#     selected_course_scores = [i[1] for i in sim_scores[1:num_of_rec + 1]]

#     # Get the dataframe & title
#     result_df = df.iloc[selected_course_indices]
#     result_df['similarity_score'] = selected_course_scores
#     final_recommended_courses = result_df[['course_title', 'similarity_score', 'url']]
#     return final_recommended_courses.head(num_of_rec)


@st.cache_data
# def search_term_if_not_found(term,df):
# 	result_df = df[df['subject'].str.contains(term, case=False) | df['course_title'].str.contains(term, case=False)]
#     # df[df['course_title'].str.contains(term)]
# 	return result_df
def search_term_if_not_found(search_term, df):
    search_results = df[df['subject'].str.contains(search_term, case=False) | df['course_title'].str.contains(search_term, case=False)]
    if not search_results.empty:
        return search_results
    else:
        return pd.DataFrame()

def fb(course_title):     
        ref = db.child('history').push({
        "user_id": user_id,
        "course_title": course_title
        })

# Create a custom function to handle the "Interested" button click
def on_interested_button_click(course_title):
    st.session_state.interested_courses.append(course_title)
    fb(course_title)

# Function to display course recommendations as cards
def display_course_cards(data):
    for idx, row in data.iterrows():
        st.write(f"**Course Title:** {row['course_title']}")
        st.write(f"**Link:** [{row['url']}]({row['url']})")
        st.write(f"**Is paid?:** {row['is_paid']}")
        st.write(f"**Level:** {row['level']}")
        st.write(f"**Subject:** {row['subject']}")
        st.write(f"**Language:** {row['language']}")
        button_key = f"interested_button_{idx}_{random.randint(1, 100000)}"
        # Use functools.partial to pass the course title to the on_click function
        on_click = functools.partial(on_interested_button_click, row['course_title'])
        if st.button('Interested', key=button_key, on_click=on_click):
            # Do not append the course title here, it's done in on_interested_button_click
            pass
        st.write("----")



def app():
    st.markdown("<h1 style='text-align: center; color: purple;'>Course Dekho</h1>", unsafe_allow_html=True)
    
    menu = ["Home", "Search"]
    choice = st.selectbox("Menu", menu)
    df = load_data("data/course_data.csv")
    
    if choice == "Home":
        st.subheader("Home")
        st.markdown("<h3 style='text-align: left; color: purple;'>Recommended Courses:</h>", unsafe_allow_html=True)
         
       
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
                    st.write("Course Titles for user_id:", user_id)
                    for title in course_titles:
                        st.write(title)
                        cosine_sim_mat = vectorize_text_to_cosine_mat(df,title)   
                        recommendations = get_recommendation(title,cosine_sim_mat,df,5)
                        display_course_cards(recommendations)

                else:
                    st.write("No course titles found for user_id:", user_id)
            else:
                st.write("Failed to retrieve data from the Firebase Realtime Database.")
   


        
    if choice == "Search":
        st.markdown("<h3 style='text-align: left; color: purple;'>Search for courses</h>", unsafe_allow_html=True)
       
        search_term = st.text_input("Search")
        if st.button("Search"):
            if search_term is not None:
                try:
                    st.info("Suggested Options include")

                    result_df = search_term_if_not_found(search_term, df)
                    # Display searched courses on the Recommended page
                    display_course_cards(result_df)
                    

                    # st.subheader("Recommended Courses:")
                    # results = get_recommendation(search_term,cosine_sim_mat,df)
                except:
                    st.write("Kuch to gadbad hai")
                    display_course_cards(result_df)

                    

if __name__ == '__main__':
    app()








