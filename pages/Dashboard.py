import streamlit as st
import pandas as pd
# Load EDA
import pandas as pd 
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
# Add numpy import
import numpy as np
from streamlit_option_menu import option_menu

st.set_page_config(initial_sidebar_state="collapsed") 

# Load your dataset
def load_data(data):
    df = pd.read_csv(data)
    return df

def vectorize_text_to_cosine_mat(data):
    count_vect = CountVectorizer()
    
    # Replace np.nan values with empty strings
    data.fillna("", inplace=True)
    
    cv_mat = count_vect.fit_transform(data)
    # Get the cosine
    cosine_sim_mat = cosine_similarity(cv_mat)
    return cosine_sim_mat

# Function to recommend courses based on 'subject' or 'course_title' containing the search term
def recommend_courses(search_term, df, num_of_rec=10):
    search_results = df[df['subject'].str.contains(search_term, case=False) | df['course_title'].str.contains(search_term, case=False)]
    if not search_results.empty:
        return search_results.head(num_of_rec)
    else:
        return pd.DataFrame()

# Function to get recommendations using cosine similarity
def get_recommendation(title, cosine_sim_mat, df, num_of_rec=10):
    # indices of the course
    course_indices = pd.Series(df.index, index=df['course_title']).drop_duplicates()
    # Index of course
    idx = course_indices[title]

    # Look into the cosine matrix for that index
    sim_scores = list(enumerate(cosine_sim_mat[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    selected_course_indices = [i[0] for i in sim_scores[1:num_of_rec + 1]]
    selected_course_scores = [i[1] for i in sim_scores[1:num_of_rec + 1]]

    # Get the dataframe & title
    result_df = df.iloc[selected_course_indices]
    result_df['similarity_score'] = selected_course_scores
    final_recommended_courses = result_df[['course_title', 'similarity_score', 'url']]
    return final_recommended_courses.head(num_of_rec)

@st.cache
def search_term_if_not_found(term,df):
	result_df = df[df['course_title'].str.contains(term)]
	return result_df

# Function to display course recommendations as cards

def display_course_cards(data):
    card_style = """
    <style>
        .card {
    border: 2px solid #dbc3db ;                                                                                                                                                                                                                               
    border-radius: 10px;
    padding: 20px;
    margin: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    background-color: #f2e1f2;
}

.card h3 {
    font-size: 18px;
    color: #880088;
    margin-bottom: 8px;
}

.card p {
    font-size: 16px;
    margin-bottom: 10px;
    color: #[theme]
primaryColor="#F63366"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#262730"
font="sans serif";
}

.card a {
    color: #b349b3;
    text-decoration: none;
    font-weight: bold;
}

.card a:hover {
    color: #cc8dcc;
}

/* Add additional styles for other elements as needed */

    </style>
    """

    st.markdown(card_style, unsafe_allow_html=True) 
    
    for _, row in data.iterrows():
        # Create a card for each course
        st.markdown(
            f'''
            <div class="card">
                <h3>Course Title: <p>{row['course_title']}</p></h3>
                <h3>Link:</h3><a href='{row['url']}' target='_blank'>{row['url']}</a>
                <h3>Is Paid?: <p>{row['is_paid']}</p></h3>
                <h3>Level: <p>{row['level']}</p></h3>
                <h3>Subject: <p>{row['subject']}</p></h3>
                <h3>Language: <p>{row['language']}</p></h3>
            </div>
            ''',unsafe_allow_html=True)
        
    # for _, row in data.iterrows():
    #     st.write(f"**Course Title:** {row['course_title']}")
    #     st.write(f"**Link:** [{row['url']}]({row['url']})")
    #     st.write(f"**Is paid?:** {row['is_paid']}")
    #     st.write(f"**Level:** {row['level']}")
    #     st.write(f"**Subject:** {row['subject']}")
    #     st.write(f"**Language:** {row['language']}")
    #     st.write("----")
    
        


def app():
    
    st.markdown("<h1 style='text-align: center; color: purple;'>Course Dekho</h1>",unsafe_allow_html=True)
    
    choice = option_menu(None, ["Home", "Recommend"], 
    icons=['house','hand-thumbs-up'], 
    menu_icon="cast", default_index=0)
    
    #choice = st.selectbox("Menu", menu)
    df = load_data("data/course_data.csv")
    
    if choice == "Home":
        st.subheader("Home")
        st.markdown("<h3 style='text-align: left; color: #880088;'>Recommended Courses:</h3>", unsafe_allow_html=True)
       
        
    if choice == "Recommend":
        st.markdown("<h3 style='text-align: left; color: #880088;'>Recommend Courses:</h3>", unsafe_allow_html=True)
        cosine_sim_mat = vectorize_text_to_cosine_mat(df['course_title'])
        search_term = st.text_input("Search")
        num_of_rec = st.number_input("Number")
        if st.button("Recommend"):
            if search_term is not None:
                try:
                    results = get_recommendation(search_term,cosine_sim_mat,df, num_of_rec)
                    
                    # Display recommended courses on the Recommended page
                    st.subheader("Recommended Courses:")
                    display_course_cards(results)
                    
                except:
                    st.info("Suggested Options include")
                    result_df = search_term_if_not_found(search_term, df)
                    display_course_cards(result_df) 

                    

if __name__ == '__main__':
    app()




