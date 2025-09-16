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
# 0) Ensure OIDC deps (st.login relies on Authlib via streamlit[auth])
# ──────────────────────────────────────────────────────────────────────────────
def ensure_auth_dependencies() -> bool:
    try:
        importlib.import_module("authlib")  # required behind st.login()
        return True
    except ImportError:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", 'streamlit[auth]']
            )
            importlib.invalidate_caches()
            importlib.import_module("authlib")
            return True
        except Exception as e:
            st.error(
                "Could not install OIDC dependencies (`streamlit[auth]`). "
                "Please add `streamlit[auth]` to requirements.txt. "
                f"Details: {e}"
            )
            return False

auth_ready = ensure_auth_dependencies()  # ← define BEFORE any use

# ──────────────────────────────────────────────────────────────────────────────
# 1) App setup
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Google Login App - V-9-16-25", layout="centered")

IMAGE_ADDRESS = "https://img.freepik.com/free-photo/fantasy-landscape-with-butterfly_23-2151451739.jpg"

# Prefer st.user; fallback to experimental_user for older runtimes
try:
    user_obj = st.user  # read-only, dict-like identity when OIDC configured
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
            v = user_obj[k]  # dict-like access
            if v:
                return v
        except Exception:
            pass
    return None

# Determine login state:
is_logged_in = bool(
    getattr(user_obj, "is_logged_in", False)
    or uget("email", "sub", "name", "user_id", "id")
)

# Check that login/logout APIs are available
login_api_available = auth_ready and hasattr(st, "login") and hasattr(st, "logout")

# ──────────────────────────────────────────────────────────────────────────────
# 2) UI (keeps your styling)
# ──────────────────────────────────────────────────────────────────────────────
if not is_logged_in:
    # -------- NOT LOGGED IN --------
    st.title("Google Login App - V-9-16-25")
    st.image(IMAGE_ADDRESS)

    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        if login_api_available:
            # Uses your current Secrets:
            # [auth]
            # redirect_uri = "https://sharon-classification-app-with-app-sign-in-sl7zhe2hdfysksciabq.streamlit.app/oauth2callback"
            # client_id = "863781154987-38hbgcutu18f1ti7hvqc02p2cl4lpndl.apps.googleusercontent.com"
            # client_secret = "456"
            # server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
            st.login()
        else:
            st.sidebar.warning(
                "Login API not available. Ensure `streamlit[auth]` is installed "
                "and OIDC secrets are configured."
            )

    # Non-sensitive config peek (helps verify deployment settings)
    with st.sidebar.expander("OIDC setup (current)"):
        auth_secrets = {}
        try:
            auth_secrets = dict(st.secrets.get("auth", {}))
        except Exception:
            pass
        st.write(
            {
                "redirect_uri": auth_secrets.get("redirect_uri", "(missing)"),
                "server_metadata_url": auth_secrets.get("server_metadata_url", "(missing)"),
                "client_id_present": bool(auth_secrets.get("client_id")),
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
