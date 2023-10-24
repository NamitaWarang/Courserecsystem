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

st.markdown(
    """
    <style>
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        background-color: #f0f0f0;
    }
    .header {
        text-align: center;
        color: purple;
        padding: px 0;
    }
    .subheader {
        text-align: left;
        color: #b153ea;
        padding-top: 0px;
        
    }

        
        .card {
            border: 1px solid #ccc;
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        width: 550px;}
  

.card:hover {
  border: 1px solid #a789b9;
  transform: scale(1.05);
}

.card:active {
  transform: scale(0.95) rotateZ(1.7deg);
}
   

    .card h3 {
        color: ##b153ea;
    }
    .card a {
        color: ##b153ea;
    }
    .button {
        background-color: #b153ea;
        color: white;
        padding: 8px 16px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .button:hover {
        
        background-color: #b153ea;
    }
    
    .thumbnail img {
    width: 500px;
  height: 250px;
  object-fit: cover;
    border-radius: 10px; /* Optional: Add border-radius to the image */
}
    </style>
    """,
    unsafe_allow_html=True
)


# Initialize session state
if 'interested_courses' not in st.session_state:
    st.session_state.interested_courses = []


# if user_id is not None:
#     st.write(f"User ID from URL: {user_id}")

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


@st.cache_data
def search_term_if_not_found(search_term, df):
    search_results = df[df['subject'].str.contains(search_term, case=False) | df['course_title'].str.contains(search_term, case=False)]
    return search_results


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
        st.markdown(
            f"""
            <div class="card">
                <div class="price-row"> 
                <div class="price-col"> 
                <div class="thumbnail">
                    <img src="{row['img']}" alt="Thumbnail">
                </div>
                <div class="card_content">
                    <h3>{row['course_title']}</h3>
                    <p><strong>Link:</strong> <a href="{row['url']}">{row['url']}</a></p>
                    <p><strong>Is paid?:</strong> {row['is_paid']}</p>
                    <p><strong>Level:</strong> {row['level']}</p>
                    <p><strong>Subject:</strong> {row['subject']}</p>
                    <p><strong>Language:</strong> {row['language']}</p>
                    </div>
                    </div>
                    </div>
            </div>
            """, unsafe_allow_html=True
        )
        
        
        # st.write(f"**Course Title:** {row['course_title']}")
        # st.write(f"**Link:** [{row['url']}]({row['url']})")
        # st.write(f"**Is paid?:** {row['is_paid']}")
        # st.write(f"**Level:** {row['level']}")
        # st.write(f"**Subject:** {row['subject']}")
        # st.write(f"**Language:** {row['language']}")
        button_key = f"interested_button_{idx}_{random.randint(1, 100000)}"
        # Use functools.partial to pass the course title to the on_click function
        on_click = functools.partial(on_interested_button_click, row['course_title'])
        if st.button('Interested', key=button_key, on_click=on_click):
            # Do not append the course title here, it's done in on_interested_button_click
            pass
        st.write("----")



def app():
    st.markdown("<h1 style='text-align: center; color: #6f07bb;'>Course Dekho</h1>", unsafe_allow_html=True)
    
    choice = option_menu(None,["Home", "Search"],
                         icons=['house','search'],orientation='horizontal')
   
   
    df = load_data("data/course_data.csv")
    
    if choice == "Home":
        
        st.markdown("<h3 style='text-align: left; color: #b153ea;'>Recommended Courses:</h>", unsafe_allow_html=True)
         
       
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
                    # st.write("Course Titles for user_id:", user_id)
                    for title in course_titles:
                        # st.write(title)
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








