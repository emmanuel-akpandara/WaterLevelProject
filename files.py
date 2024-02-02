from imports import *

stations_endpoint = st.secrets["STATIONS_ENDPOINT"]

# User credentials for basic authentication
nodered_username = st.secrets["NODE_RED_USERNAME"]
nodered_password = st.secrets["NODE_RED_PASSWORD"]

def get_stations():
    node_red_api_endpoint = stations_endpoint


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



def delete_file(selected_option, selected_station, file_id):
    option_folder = "sensor_setup" if selected_option == "Sensor Setup" else "survey_plan"
    file_path = f"users/{st.session_state.username}/{option_folder}/{selected_station[0]}/{file_id}"
    print("preparing to delete file: ", file_path)
    try:
        # Use Firebase storage to delete the file
        bucket = storage.bucket()
        blob = bucket.blob(file_path)
        blob.delete()

        st.success(f"File '{file_id}' deleted successfully!")
        # Refresh the page after deleting the file
        time.sleep(2)
        st.experimental_rerun()

    except Exception as e:
        st.error(f"Error deleting file: {e}")


def list_files(option, station):
    # Use Firebase storage
    bucket = storage.bucket()

    # Get the current user's username
    username = st.session_state.username

    # Create a reference to the user's folder in storage
    user_folder = f"users/{username}/"

    # Set the destination path based on the selected option and station
    option_folder = "sensor_setup" if option == "Sensor Setup" else "survey_plan"
    destination_folder = f"{user_folder}{option_folder}/{station[0]}/"

    # List all files in the destination folder
    blobs = bucket.list_blobs(prefix=destination_folder)
    files_list = [blob.name[len(destination_folder):] for blob in blobs]

    return files_list

def app():
    st.subheader('List Files in Sensor Setup and Survey Plan')

    # Checks if the user is logged in
    if 'username' not in st.session_state or not st.session_state.username:
        st.warning("You need to be logged in to view this content.")
        return

    # Switching for choosing between "sensor setup" and "survey plan"
    selected_option = st.radio("Choose Option", ["Sensor Setup", "Survey Plan"])

   
    stations = get_stations()

    # Default station selection (first station)
    default_station = stations[0] if stations else None

    
    selected_station = st.selectbox("Select Station", stations, index=stations.index(default_station) if default_station else 0)

    # Listing all files in the "sensor_setup" and "survey_plan" folders
    files_list = list_files(selected_option, selected_station)

    
    selected_file = None
    for index, file_name in enumerate(files_list, start=1):
        
        file_checkbox = st.checkbox(file_name)
        if file_checkbox:
            selected_file = file_name

    
    if st.button("Delete Selected File"):
        delete_file(selected_option, selected_station, selected_file)
        st.success(f"File '{selected_file}' deleted successfully.")

    