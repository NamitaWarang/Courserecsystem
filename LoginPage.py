import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import db



# cred = credentials.Certificate("courserecsystem-9a84c-17724027f67f.json")
# firebase_admin.initialize_app(cred)

# Check if the Firebase app is already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("courserecsystem-9a84c-17724027f67f.json")
    firebase_admin.initialize_app(cred)

def is_user_logged_in():
    try:
        user = auth.current_user
        return user is not None
    except:
        return False

# def f(email): 
#     try:
#         user = auth.get_user_by_email(email)
#         print(user.uid)
#         st.session_state.username = user.uid
#         st.session_state.useremail = user.email
        
#         global Usernm
#         Usernm=(user.uid)
        
#         st.session_state.signedout = True
#         st.session_state.signout = True    

        
#     except: 
#         st.warning('Login Failed')
st.set_page_config(initial_sidebar_state="collapsed") 
def app():
    st.markdown("<h1 style='text-align: center; color: purple;'>Course Dekho</h1>", unsafe_allow_html=True)
    if not is_user_logged_in():
        # Select login or signup
        menu = ["Login", "Signup"]
        choice = st.selectbox("Choose an option", menu)

        if choice == "Signup":
            st.subheader("Signup")
            email = st.text_input("Email:")
            create_password = st.text_input("Create Password:", type="password")
            confirm_password = st.text_input("Confirm Password:", type="password")

            if create_password != confirm_password:
                st.error("Passwords do not match")
            elif st.button("Signup"):
                try:
                    # Store user information (you can implement this logic)
                    user = auth.create_user(email=email, password=create_password)
                    ref= db.reference('/')
                    ref.child(user['uid']).child('email').set(email)
                    st.success("Signup Successful")
                    st.title('Welcome '+ email)
                    st.info("Login via Login drop-down select")
                except Exception as e:
                    st.error(f"Signup Failed: {str(e)}")

        elif choice == "Login":
            st.subheader("Login")
            email = st.text_input("Email:")
            password = st.text_input("Password:", type="password")

            if st.button('Login'):
                try:
                    # user = auth.get_user_by_email(email)
                    # user = auth.sign_in_with_email_and_password(email, password)

                    user = auth.get_user_by_email(email)
                    auth.get_user(user.uid)
                    # console.log(user)
                    st.success("Login Successful")
                    st.markdown('<a href="Dashboard" target="_self">Get Started</a>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Login Failed: {str(e)}")



if __name__ == "__main__":
    app()


