import streamlit as st
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, storage
import requests
import pandas as pd

# Initialize Firebase
cred = credentials.Certificate("gitguardians-app-2e4d25999060.json")
# firebase_admin.initialize_app(cred, {'storageBucket': 'gitguardians-app.appspot.com'})

def app():
    st.subheader('Welcome to the storage page!')

    # Check if the user is logged in
    if 'username' not in st.session_state or not st.session_state.username:
        st.warning("You need to be logged in to view this content.")
        return
    
    stations_endpoint = "https://node-red-group2.smartville-poc.mycsn.be/app/stations"

    # User credentials for basic authentication
    nodered_username = "group2"
    nodered_password = "4KuN8i52qWGz8HULbBHuaZyT"

    def get_stations():
        node_red_api_endpoint = stations_endpoint

        # Modify the query to include the selected station
        
        # Make a GET request to Node-RED with basic authentication
        response = requests.get(
            node_red_api_endpoint,
            auth=(nodered_username, nodered_password)
        )
        if response.status_code == 200:
            data = response.json()
            df = pd.json_normalize(data)
            return [(row['stationname'].replace("/", "-"), row['id']) for _, row in df.iterrows()]
        else:
            st.error(f"Error from Node-RED: {response.status_code} - {response.text}")
            return []

    stations = get_stations()

    # Default station selection (first station)
    default_station = stations[0] if stations else None

    # Dropdown for selecting the station
    selected_station = st.selectbox("Select Station", stations, index=stations.index(default_station) if default_station else 0)

    # Use Firebase storage
    bucket = storage.bucket()

    # Get the current user's username
    username = st.session_state.username

    # Create a reference to the user's folder in storage
    user_folder = f"users/{username}/"

    # Switch for choosing between "sensor setup" and "survey plan"
    selected_option = st.radio("Choose Option", ["Sensor Setup", "Survey Plan"])

    # File upload section
    uploaded_file = st.file_uploader("Choose a file to upload")

    if uploaded_file is not None:
        # Textbox for the user to input a new filename
        new_filename = st.text_input("Enter new filename:", value=uploaded_file.name)
        # Button to trigger the upload with the new filename
        if st.button("Upload"):
            # Set destination path within the user's folder based on the selected option
            option_folder = "sensor_setup" if selected_option == "Sensor Setup" else "survey_plan"
            filename = f"{selected_station[0]}/{new_filename}"
            destination_blob_name = f"{user_folder}{option_folder}/{filename}"
            print(destination_blob_name)
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_file(uploaded_file)

            st.success(f"File {new_filename} uploaded successfully to {destination_blob_name}")
