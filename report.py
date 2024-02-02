from imports import *


# Replace 'YOUR_NODE_RED_USERNAME' and 'YOUR_NODE_RED_PASSWORD' with your Node-RED credentials
NODE_RED_USERNAME = st.secrets["NODE_RED_USERNAME"]
NODE_RED_PASSWORD = st.secrets["NODE_RED_PASSWORD"]


def app():
    st.subheader('Welcome to the alert page')

     # Check if the user is logged in
    if 'username' not in st.session_state or not st.session_state.username:
        st.warning("You need to be logged in to view this content.")
        return
    

    def address_to_latlng(address: str, api_key: str) -> Optional[Tuple[float, float]]:
        geocoder = OpenCageGeocode(api_key)
        results = geocoder.geocode(address)

        if results and results[0]['geometry']:
            lat, lng = results[0]['geometry']['lat'], results[0]['geometry']['lng']
            return lat, lng
        else:
            return None
    

    def post_reading(lock: int, longitude: float, latitude: float, timestamp: str, value: int, unit: str):
        url = st.secrets["POST_READING_URL"]
        data = [{
            "lock": lock,
            "longitude": longitude,
            "latitude": latitude,
            "timestamp": timestamp,
            "value": value,
            "unit": unit
        }]

        auth = (NODE_RED_USERNAME, NODE_RED_PASSWORD)
        response = requests.post(url, json=data, auth=auth)
        
        if response.status_code == 200:
            st.success("Data successfully sent!")
        else:
            st.error(f"Failed to send data. Status code: {response.status_code}")

    latitude = 0.0
    longitude = 0.0
    
    
    lock_value = st.slider("Lock (%)", min_value=0, max_value=100, step=10, value=50)

    
    address = st.text_input("Enter an address:")

    api_key = st.secrets["OPENCAGE_API_KEY"]

    if st.button("Convert"):
        # Convert address to latitude and longitude
        coordinates = address_to_latlng(address, api_key)

        if coordinates:
            latitude, longitude = coordinates  # Update latitude and longitude
            st.session_state.latitude = latitude  # Store in session_state
            st.session_state.longitude = longitude

            st.success(f"Coordinates for {address}: {coordinates}")

            # Create a map centered around the converted location
            m = folium.Map(location=coordinates, zoom_start=12)
            folium.Marker(coordinates, popup=f"Location: {address}").add_to(m)

            # Display the map in Streamlit using folium_static
            folium_static(m)

    # Date and time picker for timestamp
    date_value = st.date_input("Date", value=datetime.now().date(), min_value=datetime(1970, 1, 1).date())
    time_value = st.time_input("Time", value=datetime.now().time())
    timestamp = datetime.combine(date_value, time_value)
    timestamp = timestamp.isoformat() + "Z"

    
    # Integer text box for value
    value = st.number_input("Height of water", value=2, format="%d", step=1)

    # Unit default in meters
    unit = st.text_input("Unit", value="m")

    # Display the values for verification
    st.subheader("Selected Values:")
    st.markdown(f"- Lock: {lock_value}%")
    st.markdown(f"- Timestamp: {timestamp}")
    st.markdown(f"- Value: {value}")
    st.markdown(f"- Unit: {unit}")



    if st.button("Send Reading"):
        post_reading(lock_value, st.session_state.longitude, st.session_state.latitude, timestamp, value, unit)
        


