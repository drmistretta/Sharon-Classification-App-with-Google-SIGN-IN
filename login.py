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
st.set_page_config(page_title="Google Login App - V-9-16-25.3", layout="centered")
#
# IMAGE_ADDRESS is a module-level (login.py), global variable that is shared across this file
# IMAGE_ADDRESS is a variable linked to a string, which is the URL of an image on the freepik website
#
IMAGE_ADDRESS = "https://images.unsplash.com/photo-1623615412998-c63b6d5fe9be?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8bW9uYXJjaCUyMGJ1dHRlcmZseXxlbnwwfHwwfHx8MA%3D%3D"

# The following if/else routine checks to see if the user is already logged into Google
# The "true" condition is invoked when Streamlit detects that the user is NOT logged in:
# --- Viewer identity on Streamlit Community Cloud ---
# None => viewer not identified (or app visibility doesn't require sign-in)
# --- Helper: safely get user fields (works for attr or dict-like) ---
def current_user():
    """Return the Streamlit user object, preferring st.user; fallback to st.experimental_user."""
    try:
        return st.user  # New API (no deprecation)
    except Exception:
        try:
            return st.experimental_user  # Fallback on older hosts
        except Exception:
            return None

def get_user_value(u, *keys):
    """Safely fetch first available field from a user object (attr or mapping style)."""
    if u is None:
        return None
    for k in keys:
        try:
            v = getattr(u, k)
            if v:
                return v
        except Exception:
            pass
        try:
            v = u[k]  # dict-like
            if v:
                return v
        except Exception:
            pass
    return None

user = current_user()

if user is None:
    # ---- NOT LOGGED IN (no viewer identity present) ----
    st.title("Google Login App - V-9-16-25")
    st.image(IMAGE_ADDRESS)

    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        st.sidebar.info(
            "On Streamlit Community Cloud, sign-in is controlled via *App visibility* "
            "('Email required' or 'Restricted'). There is no programmatic st.login()."
        )

    with st.sidebar.expander("Why can’t I log in here?"):
        st.write(
            "- Set App visibility to 'Email required' or 'Restricted'.\n"
            "- Refresh and sign in from the app’s top-right user menu."
        )

else:
    # ---- LOGGED IN (viewer identity available) ----
    st.subheader("Please visit the App")

    display_name = (
        get_user_value(user, "name", "full_name", "display_name")
        or get_user_value(user, "email", "primaryEmail")
        or get_user_value(user, "username", "user", "user_id", "id")
        or "Signed-in user"
    )

    st.markdown(
        f"Hello, <span style='color: orange; font-weight: bold;'>{display_name}</span>!",
        unsafe_allow_html=True,
    )

    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.sidebar.warning(
            "On Streamlit Community Cloud, sign-out is handled by the platform. "
            "Use the user/profile menu in the app header."
        )
