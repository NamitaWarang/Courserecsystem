import streamlit as st
#import pyrebase
from datetime import datetime
from streamlit_option_menu import option_menu

st.set_page_config(initial_sidebar_state="collapsed")
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

#with open('style.css')as f:
 #   st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
css = """
<link rel="stylesheet" type="text/css" href="style.css">
"""
st.markdown(css, unsafe_allow_html=True)

# Check if the Firebase app is already initialized

#firebase = pyrebase.initialize_app(firebaseConfig)
#auth = firebase.auth()  

#db = firebase.database()
#storage = firebase.storage()

def is_user_logged_in():
    try:
        user = auth.current_user
        return user is not None
    except:
        return False

 
def app():
    st.markdown("<h1 style='text-align: center; color:#30C91E;'>Course Dekho</h1>", unsafe_allow_html=True)
    if not is_user_logged_in():
        # Select login or signup
        choice = option_menu(None,["Login", "Signup"],orientation='horizontal')

        if choice == "Signup":
            st.subheader("Signup")
            email = st.text_input("Email:")
            create_password = st.text_input("Create Password:", type="password")
            confirm_password = st.text_input("Confirm Password:", type="password")
            username = st.text_input('Username', value='Default')

            if create_password != confirm_password:
                st.error("Passwords do not match")
            if st.button("Signup"):
                try:
                    user = auth.create_user_with_email_and_password(email, confirm_password)
                    st.success('Your account is created sucessfully!')

                    # Sign in
                    user = auth.sign_in_with_email_and_password(email, confirm_password)

                    # # Store the user's local ID in session_state
                    st.session_state.user_local_id = user['localId']
                    st.session_state.user = user

                    db.child(user['localId']).child("Username").set(username)
                    db.child(user['localId']).child("ID").set(user['localId'])
                    st.title('Welcome' + username)
                    st.info('Login via login drop down selection')
                except Exception as e:
                    st.error(f"Signup Failed: {str(e)}")

# if 'user_local_id' in st.session_state:
#     # You can access the user's local ID here
#     # user_local_id = st.session_state.user_local_id
#     # Continue with your dashboard code using user_local_id
#     st.write(f"User's local ID: {user_local_id}")


        elif choice == "Login":
            st.subheader("Login")
            email = st.text_input("Email:")
            password = st.text_input("Password:", type="password")

            if st.button('Login'):
                try:
                    user = auth.sign_in_with_email_and_password(email, password)

                    # user = auth.get_user_by_email(email)
                    # auth.get_user(user.uid)
                    # console.log(user)
                    st.success("Login Successful")
                    st.markdown(f'<a href="Dashboard?user_id={user["localId"]}" target="_self">Get Started</a>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Login Failed: {str(e)}")



if __name__ == "__main__":
    app()
