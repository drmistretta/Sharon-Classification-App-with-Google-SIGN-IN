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
IMAGE_ADDRESS = "https://images.unsplash.com/photo-1623615412998-c63b6d5fe9be?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8bW9uYXJjaCUyMGJ1dHRlcmZseXxlbnwwfHwwfHx8MA%3D%3D"
#
# The following if/else routine checks to see if the user is already logged into Google
# The "true" condition is invoked when Streamlit detects that the user is NOT logged in:
if not st.user.is_logged_in:
    st.title("Google Login App - V-9-16-25")
    st.image(IMAGE_ADDRESS)
    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        st.login()
        

else:
    st.subheader('Please visit the App')
    #st.html(f"Hello, <span style='color: orange; font-weight: bold;'>{st.experimental_user.name}</span>!")
    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()
