from imports import *

  
def app():
    # # Node-RED API endpoint
    readings_endpoint = st.secrets["READINGS_ENDPOINT"]  
    stations_endpoint = st.secrets["STATIONS_ENDPOINT"]
    # User credentials for basic authentication
    username = st.secrets["NODE_RED_USERNAME"]
    password = st.secrets["NODE_RED_PASSWORD"]



    def get_stations():
        node_red_api_endpoint = stations_endpoint

        # Make a GET request to Node-RED with basic authentication
        response = requests.get(
            node_red_api_endpoint,
            auth=(username, password)
            )
        if response.status_code == 200:
            data = response.json()
            df = pd.json_normalize(data)
            return [(row['stationname'], row['id']) for _, row in df.iterrows()]

        else:
            st.error(f"Error from Node-RED: {response.status_code} - {response.text}")
            return []
        
    def get_threshold(user_email):
        threshold_endpoint = st.secrets["GET_THRESHOLD_ENDPOINT"]+user_email
        response = requests.get(threshold_endpoint, auth=(username, password))
        print("function called")
        if response.status_code == 200:
            data = response.json()
            print("successfully fetched threshold")
            if data:
                return data[0]
        return None
    
    def fetch_data_and_plot(time_range, selected_station, user_email):
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

        params = {
            'stationid': selected_station_id,
            'start_time': start_time,
            'end_time': current_time
        }
        
        response = requests.get(
            node_red_api_endpoint, 
            params=params,
            auth=(username, password)
            )
        
        if response.status_code == 200:
            data = response.json()
            df = pd.json_normalize(data)

            # Plot a line chart using Plotly Express with adjusted x-axis range
            fig = px.line(df, x='timestamp', y='value', title=f"Water levels in the last {time_range}")
            threshold_value = get_threshold(user_email)['threshold']
            station_id_value = get_threshold(user_email)['stationid']
            

            if threshold_value is not None and station_id_value == selected_station[1]:
                # Add a horizontal line for the threshold
                fig.add_shape(
                    dict(
                        type='line',
                        x0=start_time,
                        x1=current_time,
                        y0=threshold_value,
                        y1=threshold_value,
                        line=dict(color='red', width=2)
                    )
                )
            
            # Set x-axis range based on the time range
            fig.update_xaxes(range=[start_time, current_time])

            st.plotly_chart(fig)

        else:
            st.error(f"Error from Node-RED: {response.status_code} - {response.text}")



    def set_threshold(user_email, station_id, threshold):
        threshold_endpoint = st.secrets["THRESHOLD_ENDPOINT"]
        threshold_data = {"email":user_email,"stationid": station_id, "threshold": threshold}

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
        set_threshold(st.session_state.useremail, selected_station[1], threshold)


    # Call the function with the selected time range and station
    fetch_data_and_plot(time_range, selected_station, st.session_state.useremail)

    #button to call the get_threshold function
    if st.button("Get Threshold"):
        threshold_value = get_threshold(st.session_state.useremail)
        if threshold_value is not None:
            st.write(f"Threshold is set to {threshold_value}")
        else:
            st.write("Threshold is not set")
