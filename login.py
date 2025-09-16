import sys
import subprocess
import importlib
#
# streamlit is an open-source Python library for building interactive data applications
#
import streamlit as st
#
# authlib is a Python library for implementing authentication and authorization protocols
# 
import authlib
#
# ──────────────────────────────────────────────────────────────────────────────
# 0) Ensure OIDC dependencies are available (Authlib via streamlit[auth])
#    st.login() relies on OIDC support. The "streamlit[auth]" extra pulls Authlib.
# ──────────────────────────────────────────────────────────────────────────────
def ensure_auth_dependencies():
    try:
        importlib.import_module("authlib")  # Authlib is required behind st.login()
        return True
    except ImportError:
        try:
            # Install the Streamlit auth extra (which brings in Authlib)
            subprocess.check_call([sys.executable, "-m", "pip", "install", 'streamlit[auth]'])
            importlib.invalidate_caches()
            importlib.import_module("authlib")
            return True
        except Exception as e:
            st.error(
                "Could not install OIDC dependencies (`streamlit[auth]`). "
                f"Please add `streamlit[auth]` to requirements.txt. Details: {e}"
            )
            return False

auth_ok = ensure_auth_dependencies()
# --- Page setup ---
# ──────────────────────────────────────────────────────────────────────────────
# App setup
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Google Login App - V-9-16-25", layout="centered")

IMAGE_ADDRESS = "https://img.freepik.com/free-photo/fantasy-landscape-with-butterfly_23-2151451739.jpg"

# Prefer st.user (new API); fallback to experimental_user if not present
try:
    user_obj = st.user  # read-only, dict-like identity proxy when OIDC is configured
except AttributeError:
    user_obj = getattr(st, "experimental_user", None)

def uget(*keys):
    """Return first truthy field from user_obj (attribute- or mapping-style)."""
    if not user_obj:
        return None
    for k in keys:
        v = getattr(user_obj, k, None)
        if v:
            return v
        try:
            v = user_obj[k]  # dict-like
            if v:
                return v
        except Exception:
            pass
    return None

# Determine login state robustly:
# - Prefer explicit .is_logged_in if present
# - Otherwise infer from presence of common identity claims
is_logged_in = bool(getattr(user_obj, "is_logged_in", False) or uget("email", "sub", "name", "user_id", "id"))

login_api_available = auth_ready and hasattr(st, "login") and hasattr(st, "logout")

# ──────────────────────────────────────────────────────────────────────────────
# UI
# ──────────────────────────────────────────────────────────────────────────────
if not is_logged_in:
    # -------- NOT LOGGED IN --------
    st.title("Google Login App - V-9-16-25")
    st.image(IMAGE_ADDRESS)

    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        if login_api_available:
            # Uses in-app OIDC with your current secrets:
            # [auth]
            # redirect_uri = "https://sharon-classification-app-with-app-sign-in-sl7zhe2hdfysksciabq.streamlit.app/oauth2callback"
            # client_id = "863781154987-38hbgcutu18f1ti7hvqc02p2cl4lpndl.apps.googleusercontent.com"
            # client_secret = "456"
            # server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
            st.login()
        else:
            st.sidebar.warning(
                "Login API not available. Ensure `streamlit[auth]` is installed "
                "and your OIDC secrets are configured."
            )

    with st.sidebar.expander("OIDC setup (current)"):
        # Show non-sensitive info to verify configuration
        redirect_uri = st.secrets.get("auth", {}).get("redirect_uri") if hasattr(st, "secrets") else None
        provider = st.secrets.get("auth", {}).get("server_metadata_url") if hasattr(st, "secrets") else None
        st.write(
            {
                "redirect_uri": redirect_uri or "(missing)",
                "server_metadata_url": provider or "(missing)",
                "client_id_present": bool(st.secrets.get("auth", {}).get("client_id")) if hasattr(st, "secrets") else False,
            }
        )
        st.markdown(
            "- Redirect URI must exactly match your Google OAuth **Authorized redirect URI**.\n"
            "- Add `streamlit[auth]` to **requirements.txt** to avoid runtime installs."
        )

else:
    # -------- LOGGED IN --------
    st.subheader("Please visit the App")

    display_name = uget("name", "full_name", "display_name", "email") or "Signed-in user"
    st.markdown(
        f"Hello, <span style='color: orange; font-weight: bold;'>{display_name}</span>!",
        unsafe_allow_html=True,
    )

    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        if login_api_available:
            st.logout()
        else:
            st.sidebar.info("Logout API not available in this runtime.")
