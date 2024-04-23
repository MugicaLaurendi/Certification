import streamlit as st
from PIL import Image
from io import BytesIO
import base64
import requests
import os
import json
import time

from requests_toolbelt.multipart.encoder import MultipartEncoder

import requests
import streamlit as st

st.set_page_config(layout="wide", page_title="Plane Detector")

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'create_account' not in st.session_state:
    st.session_state['create_account'] = False
if 'history' not in st.session_state:
    st.session_state['history'] = False

def login() :

    st.title('Plane Detector Login Page')

    username = st.sidebar.text_input("Username", key= "user_login")
    password = st.sidebar.text_input("Password", type="password", key= "user_password")

    if st.sidebar.button('Login', use_container_width= True):
        response = requests.post("http://127.0.0.1:8000/getuser", params={"username": username, "password": password})
        print(response.text)
        if response.status_code == 200:
            st.success("You are successfully logged in")
            time.sleep(2)
            st.session_state['username'] = username
            st.session_state['authenticated'] = True
            st.rerun()
        else :
            st.error("The username or password you have entered is invalid")

    if st.sidebar.button('Create account', use_container_width= True):
        st.session_state['create_account'] = True
        st.rerun()



def create_account():

        st.title('Plane Detector Login Page')

        st.write('Enter your username and password')
        username0 = st.text_input("Username", key= 1)
        password1 = st.text_input("Password", type="password", key= 2)
        password2 = st.text_input("Password", type="password", key= 3)

        if st.button('Validate'):
            if password1 != password2 :
                st.error("Password do not match")
            else :
                response = requests.post("http://127.0.0.1:8000/adduser", params={"username": username0, "password": password1})
                if response.status_code == 200:
                    st.success("Account created")
                    st.session_state['create_account'] = False
                    st.rerun()
                else :
                    st.error("The username or password you have entered is invalid")



def main_page() :

        url = "http://127.0.0.1:8000/planedetector"




        st.write("## Plane Detector")
        st.write(":airplane: Try uploading a satellite image to detect planes. Full quality images can be downloaded from the sidebar.")
        st.sidebar.write("## Upload and download :gear:")

        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

        # Download the image
        def convert_image(img):
            buf = BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            return byte_im

        # Transforme the image
        def fix_image(upload):

            image = upload
            col1.write("Original Image :camera:")
            col1.image(image)

            print(st.session_state['username'])

            def process(image, server_url: str):

                m = MultipartEncoder(fields={"file": ("filename", image, "image/png"),})

                r = requests.post(
                    server_url,params={"username": st.session_state['username']} ,data=m, headers={"Content-Type": m.content_type}
                )

                return r


            response = process(image, url)

            image_req = BytesIO(response.content)
            image_predicted = Image.open(image_req).convert("RGB")

            col2.write("Analyzed image :wrench:")
            col2.image(image_predicted)

            st.sidebar.markdown("\n")
            st.sidebar.download_button("Download analyzed image", convert_image(image_predicted), "image_predicted.png", "image/png")


        col1, col2 = st.columns(2)
        my_upload = st.sidebar.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

        if st.sidebar.button(label= 'History', use_container_width= True):
            st.session_state['history'] = True
            st.rerun()

        if my_upload is not None:
            if my_upload.size > MAX_FILE_SIZE:
                st.error("The uploaded file is too large. Please upload an image smaller than 5MB.")
            else:
                fix_image(upload=my_upload)

def history():

    st.write("## History")

    if st.sidebar.button(label= 'Menu', use_container_width= True):
        st.session_state['history'] = False
        st.rerun()

    username = st.session_state['username']
    response = requests.post("http://127.0.0.1:8000/gethistory", params={"username": username})

    if response.status_code == 200:
        image_links = response.json()
        for link in image_links:
            st.image(f"{link}")
    else :
        st.write("No history found")



# Affichage conditionnel basé sur l'état d'authentification
if st.session_state['create_account']:
    create_account()
else :
    if not st.session_state['authenticated']:
        login()

    else:
        if not st.session_state['history']:
            main_page()
        else:
            history()
