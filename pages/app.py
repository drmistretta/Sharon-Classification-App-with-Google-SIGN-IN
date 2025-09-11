import streamlit as st
import numpy as np
import requests
import base64
import os
from PIL import Image


if not st.user.is_logged_in:
    st.error("Please log in to access the App")
    st.stop()

ENDPOINT_URL = 'https://askai.aiclub.world/83845c7c-6fc6-42c0-a3d4-b1918a688783'

#####functions#########
def get_prediction(image_data, url):
  r = requests.post(url, data=image_data)
  response = r.json()['predicted_label']
  print(response)
  return response

  

#Building the website

#title of the web page
st.title("Butterfly Classifier")

#setting the main picture
st.image(
    "https://images.unsplash.com/photo-1623615412998-c63b6d5fe9be?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8bW9uYXJjaCUyMGJ1dHRlcmZseXxlbnwwfHwwfHx8MA%3D%3D", 
    caption = "Butterfly")

#about the web app
st.header("About the Web App")

#details about the project
with st.expander("Web App 🌐"):
    st.subheader("Butterfly Image Predictions")
    st.write("This web app is about.....................")

#setting the tabs
tab1, tab2 = st.tabs(['Image Upload 👁️', 'Camera Upload 📷'])

#tab1
with tab1:
    #setting file uploader
    #you can change the label name as your preference
    image = st.file_uploader(label="Upload an image",accept_multiple_files=False, help="Upload an image to classify them")

    if image:
        #validating the image type
        image_type = image.type.split("/")[-1]
        if image_type not in ['jpg','jpeg','png','jfif']:
            st.error("Invalid file type : {}".format(image.type), icon="🚨")
        else:
            #displaying the image
            st.image(image, caption = "Uploaded Image")

            #getting the predictions
            with image:
                payload = base64.b64encode(image.read())
                response = get_prediction(payload, ENDPOINT_URL)
                st.success(f"Class Label: {response}")


with tab2:
    #camera input
    cam_image = st.camera_input("Please take a photo")

    if cam_image:
        #displaying the image
        st.image(cam_image)

        #getting the predictions
        with cam_image:
            payload = base64.b64encode(image.read())
            response = get_prediction(payload, ENDPOINT_URL)
            
            #displaying the predicted label
            st.success("Your Condition is **{}**".format(label))
            
