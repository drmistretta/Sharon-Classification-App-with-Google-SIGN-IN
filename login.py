import streamlit as st
import authlib


IMAGE_ADDRESS = "https://www.theglobeandmail.com/resizer/v2/ZEC33ARWYNF7JKHKH6NN2PLRCQ.jpg?auth=b96fceb4acb641eb7765f3f1dff182dfa52eba742065b9da99b560e1ea32da21&width=1200&height=800&quality=80&smart=true"


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
