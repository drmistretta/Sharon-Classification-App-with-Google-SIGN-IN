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

# The following if/else routine checks to see if the user is already logged into Google
# The "true" condition is invoked when Streamlit detects that the user is NOT logged in:
# --- Viewer identity on Streamlit Community Cloud ---
# None => viewer not identified (or app visibility doesn't require sign-in)
# --- Helper: safely get user fields (works for attr or dict-like) ---
def user_field(u, *keys, default=None):
    """Try multiple keys as attributes, then as dict-keys; return first non-None."""
    if u is None:
        return default
    for k in keys:
        # attribute style
        try:
            v = getattr(u, k)
            if v is not None:
                return v
        except Exception:
            pass
        # dict style
        try:
            v = u.get(k)
            if v is not None:
                return v
        except Exception:
            pass
    return default
#
# experimental_user is a part of the Streamlit API, which is a read-only attribute that returns information
# The information it returns is None if the user is not logged in or fields such as .email and .name
#
user = st.experimental_user  # None if viewer identity isn’t available

if user is None:
    # NOT LOGGED IN
    st.title("Google Login App - V-9-16-25")
    st.image(IMAGE_ADDRESS)

    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        st.sidebar.info(
            "On Streamlit Community Cloud, sign-in is controlled by App Visibility "
            "('Email required' or 'Restricted'). Use the app’s header menu to sign in."
        )

    with st.sidebar.expander("Why can’t I log in here?"):
        st.write(
            "- Set App visibility to 'Email required' or 'Restricted'.\n"
            "- There is no `st.login()` API on Streamlit.\n"
            "- After changing visibility, refresh and sign in from the top-right menu."
        )

else:
    # LOGGED IN (viewer identity available)
    st.subheader("Please visit the App")

    # Try common fields: name/email; also attempt username/user_id as fallbacks.
    display_name = (
        user_field(user, "name", "full_name", "display_name") or
        user_field(user, "email") or
        user_field(user, "username", "user", "user_id", "id") or
        "Signed-in user"
    )

    st.markdown(
        f"Hello, <span style='color: orange; font-weight: bold;'>{display_name}</span>!",
        unsafe_allow_html=True,
    )

    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.sidebar.warning(
            "On Streamlit Community Cloud, sign-out is handled by the platform. "
            "Use the user/profile menu in the app header to sign out."
        )

    # Show raw user info to verify available fields
    with st.sidebar.expander("Account details (debug)"):
        st.write("Raw object:", type(user))
        # Try to show attribute-style and dict-style views defensively
        try:
            st.write("dir(user):", dir(user))
        except Exception:
            pass
        try:
            st.write("as dict (if supported):", dict(user))
        except Exception:
            try:
                st.write("user.__dict__ (if present):", getattr(user, "__dict__", None))
            except Exception:
                pass
