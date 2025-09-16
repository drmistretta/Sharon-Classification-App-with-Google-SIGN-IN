#
# streamlit is an open-source Python library for building interactive data applications
#
import streamlit as st
#
# authlib is a Python library for implementing authentication and authorization protocols
# 
import authlib
#
# IMAGE_ADDRESS is a module-level (login.py), global variable that is shared across this file
# IMAGE_ADDRESS is a variable linked to a string which is the URL of an image on the freepik website
#
IMAGE_ADDRESS = "https://img.freepik.com/free-photo/fantasy-landscape-with-butterfly_23-2151451739.jpg"
#
# The following if/else routine checks to see if the user is already logged into Google
# The "true" condition is invoked when Streamlit detects that the user is NOT logged in:
if not st.user.is_logged_in:
    st.title("Google Login App")
    st.image(IMAGE_ADDRESS)
    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        st.login()
        

else:
    st.subheader('Please visit the App')
    #st.html(f"Hello, <span style='color: orange; font-weight: bold;'>{st.experimental_user.name}</span>!")
    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()
