import sys
import subprocess
import importlib
import base64
import requests
import streamlit as st
from PIL import Image

# ──────────────────────────────────────────────────────────────────────────────
# 0) Auth deps (optional if already in your main app)
# ──────────────────────────────────────────────────────────────────────────────
def ensure_auth_dependencies() -> bool:
    try:
        importlib.import_module("authlib")
        return True
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit[auth]"])
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

auth_ready = ensure_auth_dependencies()

# ──────────────────────────────────────────────────────────────────────────────
# 1) App setup + styling (same pattern as login app)
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Butterfly Classifier", layout="centered")

# ---- Accessible theming (teal, high contrast, reduced motion) ----
st.markdown("""
<style>
:root{
  --teal-main-1:#9ED9DC; --teal-main-2:#6EC7CB;
  --teal-side-1:#95D3D4; --teal-side-2:#5FBCC0;
  --text-on-teal:#102225; --link-on-teal:#0b4f5a; --link-on-teal-hover:#083b44;
  --hc-bg-main-1:#E8F4F6; --hc-bg-main-2:#BFE5EA; --hc-text:#0A0A0A;
}
[data-testid="stAppViewContainer"]{
  background: linear-gradient(180deg,var(--teal-main-1) 0%,var(--teal-main-2) 100%);
  color: var(--text-on-teal);
}
[data-testid="stSidebar"] > div:first-child{
  background: linear-gradient(180deg,var(--teal-side-1) 0%,var(--teal-side-2) 100%);
  color: var(--text-on-teal);
}
a,.stMarkdown a{color:var(--link-on-teal);text-decoration-thickness:2px;}
a:hover,.stMarkdown a:hover{color:var(--link-on-teal-hover);}
h1,h2,h3,h4,h5,h6{color:var(--text-on-teal);}
*:focus{outline:3px solid #ffbf47 !important; outline-offset:2px !important;}
@media (prefers-reduced-motion: reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important;}}
[data-testid="stSidebar"]{min-width:290px;}
body.hc [data-testid="stAppViewContainer"]{
  background: linear-gradient(180deg,var(--hc-bg-main-1) 0%,var(--hc-bg-main-2) 100%) !important; color: var(--hc-text)!important;
}
body.hc [data-testid="stSidebar"] > div:first-child{
  background: linear-gradient(180deg,#E3F2F4 0%,#C9E9ED 100%) !important; color: var(--hc-text)!important;
}
body.hc h1, body.hc h2, body.hc h3, body.hc a { color: var(--hc-text)!important; }
/* Make st.caption text black if you use it for accessibility notes */
[data-testid="stCaptionContainer"] p,.stCaption,[data-testid="stCaption"]{color:#000!important;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Accessibility")
    hc = st.toggle("High contrast mode")
    base_size = st.slider("Base text size", 14, 22, 16, help="Increase for readability")

st.markdown(f"<style>html{{font-size:{base_size}px;}}</style>", unsafe_allow_html=True)
st.markdown(f"""
<script>
const b = window.parent.document.querySelector('body');
if (b) {{
  {'b.classList.add("hc");' if hc else 'b.classList.remove("hc");'}
}}
</script>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# 2) Auth gate (same pattern as login app)
# ──────────────────────────────────────────────────────────────────────────────
try:
    user_obj = st.user
except AttributeError:
    user_obj = getattr(st, "experimental_user", None)

def uget(u, *keys):
    if not u: return None
    for k in keys:
        v = getattr(u, k, None)
        if v: return v
        try:
            v = u[k]
            if v: return v
        except Exception:
            pass
    return None

is_logged_in = bool(getattr(user_obj, "is_logged_in", False) or uget(user_obj, "email", "sub", "name"))

if not is_logged_in:
    st.error("Please log in to access the App")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# 3) App content
# ──────────────────────────────────────────────────────────────────────────────
ENDPOINT_URL = "https://askai.aiclub.world/83845c7c-6fc6-42c0-a3d4-b1918a688783"

def get_prediction(image_bytes_b64: bytes, url: str) -> str:
    """POST base64 image bytes to the model endpoint and return predicted label."""
    try:
        r = requests.post(url, data=image_bytes_b64, timeout=30)
        r.raise_for_status()
        js = r.json()
        return js.get("predicted_label", "Unknown")
    except Exception as e:
        st.error(f"Prediction request failed: {e}")
        return "Error"

st.markdown("# Butterfly Classifier")
HERO_URL = "https://images.unsplash.com/photo-1623615412998-c63b6d5fe9be?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8bW9uYXJjaCUyMGJ1dHRlcmZseXxlbnwwfHwwfHx8MA%3D%3D"
HERO_DESC = "Monarch butterfly on a flower (decorative background for the classifier)."

st.image(HERO_URL, caption="Butterfly classification app background image", use_container_width=True)
st.caption(f"Image description: {HERO_DESC}")

st.markdown("## About the Web App")
with st.expander("Web App 🌐"):
    st.subheader("Butterfly Image Predictions")
    st.write("Upload or capture a butterfly image to get a predicted class label from the model.")

tab1, tab2 = st.tabs(["Image Upload 👁️", "Camera Upload 📷"])

ALLOWED_EXT = {"jpg", "jpeg", "png", "jfif"}

with tab1:
    image = st.file_uploader(
        label="Upload a butterfly image",
        accept_multiple_files=False,
        type=list(ALLOWED_EXT),
        help="Supported types: jpg, jpeg, png, jfif"
    )

    if image:
        ext = (image.type.split("/")[-1] or "").lower()
        if ext not in ALLOWED_EXT:
            st.error(f"Invalid file type: {image.type}", icon="🚨")
        else:
            # Show image preview
            st.image(image, caption="Uploaded image", use_container_width=True)

            # Read bytes and predict
            raw_bytes = image.getvalue()              # bytes
            payload_b64 = base64.b64encode(raw_bytes) # base64-encoded bytes
            label = get_prediction(payload_b64, ENDPOINT_URL)

            if label not in {"Error", "Unknown"}:
                st.success(f"Class Label: {label}")
            else:
                st.error("Could not retrieve a valid prediction.")

with tab2:
    cam_image = st.camera_input("Please take a photo")
    if cam_image:
        st.image(cam_image, caption="Captured image", use_container_width=True)

        # Read bytes from camera image and predict
        raw_bytes = cam_image.getvalue()              # correct source (cam_image)
        payload_b64 = base64.b64encode(raw_bytes)
        label = get_prediction(payload_b64, ENDPOINT_URL)

        if label not in {"Error", "Unknown"}:
            st.success(f"Class Label: {label}")
        else:
            st.error("Could not retrieve a valid prediction.")
