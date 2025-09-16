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
# 0) Ensure OpenID Connect (OIDC) dependencies (st.login relies on Authlib via streamlit[auth])
# - With OIDC, a trusted provider such as Google issues an ID token
# - The Streamlit app validates this token to confirm the user's identity 
# - The streamlit app can now read profile details such as name and email
# ──────────────────────────────────────────────────────────────────────────────
# -----------------------------------------------------------------------------
# ensure_auth_dependencies()
# Purpose: Make sure the libraries needed for in-app OIDC login are available.
# What it does:
#   1) Tries to import "authlib" (used under the hood by Streamlit's st.login()).
#   2) If missing, installs the "streamlit[auth]" extra (which brings in Authlib),
#      refreshes import caches, and imports "authlib" again.
#   3) On success returns True; on failure logs a helpful error in the app and
#      returns False (so the caller can disable login UI gracefully).
# Notes:
#   - Runtime installs can slow cold starts; prefer adding `streamlit[auth]`
#     to requirements.txt for production.
# -----------------------------------------------------------------------------
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
st.set_page_config(page_title="Google Login App - V-9-16-25.4", layout="centered")
#
# ---- Accessible theming: darker text on teal, focus outlines, reduced motion ----
st.markdown("""
<style>
:root{
  /* Teal backgrounds (darker than before for contrast) */
  --teal-main-1: #9ED9DC;
  --teal-main-2: #6EC7CB;
  --teal-side-1: #95D3D4;
  --teal-side-2: #5FBCC0;

  /* Text & link colors with strong contrast on teal */
  --text-on-teal: #102225;         /* deep near-black */
  --link-on-teal: #0b4f5a;         /* dark teal for links */
  --link-on-teal-hover: #083b44;   /* even darker on hover */

  /* High-contrast override (we'll toggle via a body class) */
  --hc-bg-main-1: #E8F4F6;
  --hc-bg-main-2: #BFE5EA;
  --hc-text: #0A0A0A;
}

/* Main content background */
[data-testid="stAppViewContainer"]{
  background: linear-gradient(180deg, var(--teal-main-1) 0%, var(--teal-main-2) 100%);
  color: var(--text-on-teal);
}

/* Sidebar background */
[data-testid="stSidebar"] > div:first-child{
  background: linear-gradient(180deg, var(--teal-side-1) 0%, var(--teal-side-2) 100%);
  color: var(--text-on-teal);
}

/* Make links readable on teal backgrounds */
a, .stMarkdown a {
  color: var(--link-on-teal);
  text-decoration-thickness: 2px;
}
a:hover, .stMarkdown a:hover { color: var(--link-on-teal-hover); }

/* Headings inherit readable color */
h1, h2, h3, h4, h5, h6 { color: var(--text-on-teal); }

/* Improve focus visibility for keyboard users */
*:focus {
  outline: 3px solid #ffbf47 !important;  /* WCAG-visible amber outline */
  outline-offset: 2px !important;
}

/* Respect prefers-reduced-motion for users who disable animations */
@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
    scroll-behavior: auto !important;
  }
}

/* Slightly widen sidebar for readability on dense content */
[data-testid="stSidebar"] { min-width: 290px; }

/* High-contrast mode (body.hc toggled below) */
body.hc [data-testid="stAppViewContainer"]{
  background: linear-gradient(180deg, var(--hc-bg-main-1) 0%, var(--hc-bg-main-2) 100%) !important;
  color: var(--hc-text) !important;
}
body.hc [data-testid="stSidebar"] > div:first-child{
  background: linear-gradient(180deg, #E3F2F4 0%, #C9E9ED 100%) !important;
  color: var(--hc-text) !important;
}
body.hc h1, body.hc h2, body.hc h3, body.hc a { color: var(--hc-text) !important; }
</style>
""", unsafe_allow_html=True)

### CSS end
### High Contrast Begin
# ---- Accessibility controls (sidebar) ----
with st.sidebar:
    st.markdown("### Accessibility")
    hc = st.toggle("High contrast mode")
    base_size = st.slider("Base text size", 14, 22, 16, help="Increase for readability")

# Apply user choices (toggle high-contrast class + adjust root font size)
st.markdown(f"""
<style>
html {{ font-size: {base_size}px; }}
</style>
""", unsafe_allow_html=True)

# Toggle high-contrast class on the body element
st.markdown(f"""
<script>
const b = window.parent.document.querySelector('body');
if (b) {{
  {'b.classList.add("hc");' if hc else 'b.classList.remove("hc");'}
}}
</script>
""", unsafe_allow_html=True)

### High Contrast End

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
# 2) UI (keeps your styling)  — FIXED INDENTATION
# ──────────────────────────────────────────────────────────────────────────────
if not is_logged_in:
    # -------- NOT LOGGED IN --------
    st.title("Google Login App - V-9-16-25 V5")
# Modified Alt Description Begin
    HERO_DESC = "Fantasy landscape with a butterfly; decorative background for the Butterfly Classification app."

    st.image(
        IMAGE_ADDRESS,
        caption="Butterfly classification app background image",
        use_container_width=True
            )

# Short, always-visible description (touch & desktop friendly)
    st.caption(f"Image description: {HERO_DESC}")

# Optional longer description for screen-reader/keyboard users
    with st.expander("Detailed image description"):
    st.write(
        "The image shows a stylized, pastel fantasy landscape with a large butterfly in the foreground. "
        "It is used as decorative context; no critical information is contained in the image."
            )
# Modified Alt Description End
    # Login button
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
    # Compute display name first
    display_name = uget("name", "full_name", "display_name", "email") or "Signed-in user"

    # Two-line greeting
    st.markdown(f"""
# Welcome, {display_name}!
## Click the app tab in the left-hand navigation column to classify butterflies.
""")

    # Logout button
    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        if login_api_available:
            st.logout()
        else:
            st.sidebar.info("Logout API not available in this runtime.")

