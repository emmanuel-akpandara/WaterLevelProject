import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests
import plotly.express as px

from firebase_admin import firestore

  
def app():
    # # Node-RED API endpoint
    readings_endpoint = "https://node-red-group2.smartville-poc.mycsn.be/readingstable"
    stations_endpoint = "https://node-red-group2.smartville-poc.mycsn.be/stationstable"

    # User credentials for basic authentication
    username = "group2"
    password = "4KuN8i52qWGz8HULbBHuaZyT"



    def get_stations():
        node_red_api_endpoint = stations_endpoint

        # Modify the query to include the selected station
        station_query = f"SELECT id,stationname FROM station;"
        # Make a GET request to Node-RED with basic authentication
        response = requests.post(
            node_red_api_endpoint,
            json={"query": station_query},
            auth=(username, password)
        )
        if response.status_code == 200:
            data = response.json()
            df = pd.json_normalize(data)
            return [(row['stationname'], row['id']) for _, row in df.iterrows()]

        else:
            st.error(f"Error from Node-RED: {response.status_code} - {response.text}")
            return []
        
    
    def fetch_data_and_plot(time_range, selected_station):
        node_red_api_endpoint = readings_endpoint

        # Generate the query based on the selected time range and station
        current_time = datetime.now()

        if time_range == "48 hours":
            start_time = current_time - timedelta(hours=48)
        elif time_range == "week":
            start_time = current_time - timedelta(weeks=1)
        elif time_range == "month":
            start_time = current_time - timedelta(days=30)
        elif time_range == "3 months":
            start_time = current_time - timedelta(days=90)
        else:
            st.error("Invalid time range selected.")
            return

        # Extract the ID from the selected station tuple
        selected_station_id = selected_station[1]

        # Modify the query to include the selected station
        dynamic_query = f"SELECT * FROM reading WHERE timestamp >= '{start_time}' AND timestamp <= '{current_time}' AND stationid = '{selected_station_id}';"

        # Make a POST request to Node-RED with basic authentication
        response = requests.post(
            node_red_api_endpoint,
            json={"query": dynamic_query},
            auth=(username, password)
        )

        if response.status_code == 200:
            data = response.json()
            df = pd.json_normalize(data)

            # Plot a line chart using Plotly Express with adjusted x-axis range
            fig = px.line(df, x='timestamp', y='value', title=f"Water levels in the last {time_range}")
            
            # Set x-axis range based on the time range
            fig.update_xaxes(range=[start_time, current_time])

            st.plotly_chart(fig)

        else:
            st.error(f"Error from Node-RED: {response.status_code} - {response.text}")



    def set_threshold(station_id, threshold):
        threshold_endpoint = "https://node-red-group2.smartville-poc.mycsn.be/threshold"
        threshold_data = {"stationid": station_id, "threshold": threshold}

        response = requests.post(
            threshold_endpoint,
            json=threshold_data,
            auth=(username, password)
        )

        if response.status_code == 200:
            st.success("Threshold set successfully!")
        else:
            st.error(f"Error setting threshold: {response.status_code} - {response.text}")


    st.title("Welcome to the graph Page")

    if 'username' not in st.session_state or not st.session_state.username:
        st.warning("You need to be logged in to view this content.")
        return
    st.write("This is the graph page.")

    # Dropdown for selecting the time range
    time_range = st.selectbox("Select Time Range", ["48 hours", "week", "month", "3 months"])

    # Get the list of stations
    stations = get_stations()

    # Default station selection (first station)
    default_station = stations[0] if stations else None

    # Dropdown for selecting the station
    selected_station = st.selectbox("Select Station", stations, index=stations.index(default_station) if default_station else 0)

    # Input box for threshold
    threshold = st.number_input("Set Threshold", value=5.55, format="%.2f")

    # Button to set threshold
    if st.button("Set Threshold"):
        set_threshold(selected_station[1], threshold)


    # Call the function with the selected time range and station
    fetch_data_and_plot(time_range, selected_station)