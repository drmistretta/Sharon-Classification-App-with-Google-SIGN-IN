#
# streamlit is an open-source Python library for building interactive data applications
#
import streamlit as st
#
# authlib is a Python library for implementing authentication and authorization protocols
# 
import authlib
#
# --- Page setup ---
st.set_page_config(page_title="Google Login App - V-9-16-25.2", layout="centered")
#
# IMAGE_ADDRESS is a module-level (login.py), global variable that is shared across this file
# IMAGE_ADDRESS is a variable linked to a string, which is the URL of an image on the freepik website
#
IMAGE_ADDRESS = "https://images.unsplash.com/photo-1623615412998-c63b6d5fe9be?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8bW9uYXJjaCUyMGJ1dHRlcmZseXxlbnwwfHwwfHx8MA%3D%3D"
#
# experimental_user is a part of the Streamlit API, which is a read-only attribute that returns information
# The information it returns is None if the user is not logged in or fields such as .email and .name
user = st.experimental_user  # None if not signed in (or if app visibility doesn't require sign-in)
#
# The following if/else routine checks to see if the user is already logged into Google
# The "true" condition is invoked when Streamlit detects that the user is NOT logged in:
# --- Viewer identity on Streamlit Community Cloud ---
# None => viewer not identified (or app visibility doesn't require sign-in)
user = st.experimental_user

if user is None:
    # ========== NOT LOGGED IN (no viewer identity) ==========
    st.title("Google Login App - V-9-16-25")
    st.image(IMAGE_ADDRESS)

    # Keep your styled sidebar button; explain how sign-in works on Cloud
    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        st.sidebar.info(
            "On Streamlit Community Cloud, sign-in is controlled by the app's "
            "visibility settings (e.g., ‘Email required’). There’s no programmatic "
            "`st.login()`—use the app’s hosted URL with sign-in required, or open "
            "the user menu to sign in."
        )

    with st.sidebar.expander("Why can’t I log in here?"):
        st.write(
            "- Streamlit Cloud manages authentication.\n"
            "- `st.user` / `st.login()` are not Streamlit APIs.\n"
            "- Use app visibility (Email required/Restricted) to prompt Google sign-in."
        )

else:
    # ========== LOGGED IN (viewer identity available) ==========
    st.subheader("Please visit the App")

    # Show a styled greeting (Streamlit doesn't have st.html; use markdown with HTML)
    st.markdown(
        f"Hello, <span style='color: orange; font-weight: bold;'>{user.name or user.email}</span>!",
        unsafe_allow_html=True,
    )

    # Keep your styled sidebar button; explain how to sign out on Cloud
    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.sidebar.warning(
            "On Streamlit Community Cloud, sign-out is handled by the platform. "
            "Use the user/profile menu in the app header (or your Google account) to sign out."
        )

    with st.sidebar.expander("Account details"):
        st.write(
            {
                "name": user.name,
                "email": user.email,
            }
        )
