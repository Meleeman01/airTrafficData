import json
import mysql.connector
import os
import sys

# Connect to your MariaDB database
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="admin",
    password="lol",
    database="flightsdb"
)



cursor = conn.cursor()
# [
#     {
#         "icao": "000001",
#         "noRegData": True,
#         "timestamp": 1704067200.000,
#         "trace": [
#             [29446.25, 31.211884, 33.809348, 2325, 99.9, 327.3, 1, 1024, None, "adsb_icao", None, None, None, 0.0],
#             [29451.97, 31.214160, 33.807623, 2425, 103.5, 327.2, 0, 1024, None, "adsb_icao", None, None, None, None],
#             [29456.89, 31.216095, 33.806170, 2500, 104.0, 326.8, 0, 1024, 
#                 {
#                     "type": "adsb_icao",
#                     "flight": "RHINO12 ",
#                     "tas": 102,
#                     "track": 326.77,
#                     "roll": 0.18,
#                     "baro_rate": 1024,
#                     "category": "A7",
#                     "nic": 8,
#                     "rc": 186,
#                     "version": 0,
#                     "nac_p": 8,
#                     "nac_v": 0,
#                     "sil": 2,
#                     "sil_type": "perhour",
#                     "alert": 0,
#                     "spi": 0
#                 }, 
#             "adsb_icao", None, None, None, 0.2
#             ]
#     }
#     {
#         "icao": "020101",
#         "r": "CN-COG",
#         "t": "AT76",
#         "dbFlags": 0,
#         "desc": "ATR-72-600",
#         "timestamp": 1704067200.000,
#         "trace": [
#             [30891.77, 33.383110, -7.596766, "ground", 7.8, 258.8, 1, None, None, "adsb_icao", None, None, None, None],
#             [30905.92, 33.382919, -7.597211, "ground", 4.8, 233.4, 0, None, None, "adsb_icao", None, None, None, None],
#             [30908.32, 33.382889, -7.597242, "ground", 3.8, 230.6, 0, None, {
#                 "type": "adsb_icao",
#                 "track": 230.62,
#                 "true_heading": 230.62,
#                 "emergency": "none",
#                 "nic": 8,
#                 "rc": 186,
#                 "version": 2,
#                 "nac_p": 9,
#                 "nac_v": 2,
#                 "sil": 3,
#                 "sil_type": "perhour",
#                 "sda": 2
#             }, "adsb_icao", None, None, None, None]
#     }
# ]
def convert_to_sql(release_name):
    current_dir = os.getcwd()
    traces_dir = f'{current_dir}/traces'
    os.chdir(traces_dir)

    print(os.getcwd(),traces_dir)

    #first go through traces directory
    for root, dirs, files in os.walk(traces_dir):

        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                insert_flight_data(data)
            else:
                print("not json!!!")

def insert_flight_data(flight_data):


    if flight_data.get("dbFlags") == 0:
        # Skip this entry since dbFlags is 0
        return

    # Handle "noRegData" = true case by skipping data that doesn't have registration info
    if flight_data.get("noRegData"):
        icao = flight_data["icao"]
        time_stamp = int(flight_data["timestamp"])
        print(time_stamp)
        flight_id = None  # No flight registration, we'll handle it later
        # Insert into flights table
        cursor.execute("""
            INSERT INTO flights (icao, time_stamp)
            VALUES (%s, %s)
        """, (icao, time_stamp))
        conn.commit()
        # Get the generated flight_id
        flight_id = cursor.lastrowid
        # Iterate through each trace
        for trace in flight_data["trace"]:
            # Extract the trace values
            trace_values = trace[:-1]  # Remove the last value which is extra

            # Prepare the data for insertion, assuming we don't have much other info from noRegData
            cursor.execute("""
                INSERT INTO flight_trace (
                    flight_id, time, latitude, longitude, altitude, speed, heading, vertical_speed, squawk,
                    adsb_type, flight, alt_geom, ias, tas, mach, oat, tat, track, track_rate, roll,
                    mag_heading, true_heading, baro_rate, geom_rate, squawk_2, emergency, category, 
                    nav_qnh, nav_altitude_mcp, nav_modes, nic, rc, version, nic_baro, nac_p, nac_v, sil, 
                    sil_type, gva, sda, alert, spi, geom_altitude, baro_rate_2, ias_2, climb_rate_2
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 
                    NULL, NULL, NULL, NULL, NULL, NULL
                )
            """, trace_values + [None] * 18)  # Add None for the missing columns

        conn.commit()
        return

    
    # Handle regular data with dbFlags != 0
    icao = flight_data["icao"]
    time_stamp = int(flight_data["timestamp"])

    registration = flight_data.get("r")
    tailNo = flight_data.get("t")
    description = flight_data.get("desc")

    # Insert into flights table
    cursor.execute("""
        INSERT INTO flights (icao, registration, tailNo, description, time_stamp)
        VALUES (%s, %s, %s, %s, %s)
    """, (icao, registration, tailNo, description, time_stamp))
    conn.commit()

    # Get the generated flight_id
    flight_id = cursor.lastrowid

    for trace in flight_data["trace"]:
        # Process trace data
        trace_values = trace[:-1]
        adsb_data = trace[8] if trace[8] else {}

        # Extract the ADS-B data as columns
        adsb_type = adsb_data.get("type", None)
        flight = adsb_data.get("flight", None)
        alt_geom = adsb_data.get("alt_geom", None)
        ias = adsb_data.get("ias", None)
        tas = adsb_data.get("tas", None)
        mach = adsb_data.get("mach", None)
        oat = adsb_data.get("oat", None)
        tat = adsb_data.get("tat", None)
        track = adsb_data.get("track", None)
        track_rate = adsb_data.get("track_rate", None)
        roll = adsb_data.get("roll", None)
        mag_heading = adsb_data.get("mag_heading", None)
        true_heading = adsb_data.get("true_heading", None)
        baro_rate = adsb_data.get("baro_rate", None)
        geom_rate = adsb_data.get("geom_rate", None)
        squawk_2 = adsb_data.get("squawk", None)
        emergency = adsb_data.get("emergency", None)
        category = adsb_data.get("category", None)
        nav_qnh = adsb_data.get("nav_qnh", None)
        nav_altitude_mcp = adsb_data.get("nav_altitude_mcp", None)
        nav_modes = adsb_data.get("nav_modes", None)
        nic = adsb_data.get("nic", None)
        rc = adsb_data.get("rc", None)
        version = adsb_data.get("version", None)
        nic_baro = adsb_data.get("nic_baro", None)
        nac_p = adsb_data.get("nac_p", None)
        nac_v = adsb_data.get("nac_v", None)
        sil = adsb_data.get("sil", None)
        sil_type = adsb_data.get("sil_type", None)
        gva = adsb_data.get("gva", None)
        sda = adsb_data.get("sda", None)
        alert = adsb_data.get("alert", None)
        spi = adsb_data.get("spi", None)

        # Insert into flight_trace table
        cursor.execute("""
            INSERT INTO flight_trace (
                flight_id, time, latitude, longitude, altitude, speed, heading, vertical_speed, squawk,
                adsb_type, flight, alt_geom, ias, tas, mach, oat, tat, track, track_rate, roll,
                mag_heading, true_heading, baro_rate, geom_rate, squawk_2, emergency, category, 
                nav_qnh, nav_altitude_mcp, nav_modes, nic, rc, version, nic_baro, nac_p, nac_v, sil, 
                sil_type, gva, sda, alert, spi, geom_altitude, baro_rate_2, ias_2, climb_rate_2
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, trace_values + [
            adsb_type, flight, alt_geom, ias, tas, mach, oat, tat, track, track_rate, roll,
            mag_heading, true_heading, baro_rate, geom_rate, squawk_2, emergency, category, 
            nav_qnh, nav_altitude_mcp, nav_modes, nic, rc, version, nic_baro, nac_p, nac_v, sil, 
            sil_type, gva, sda, alert, spi, None, None, None, None
        ])

    conn.commit()

# # Process the data
# for flight_data in data:
#     insert_flight_data(flight_data)




def choose_directory():
    # Path to your project directory
    project_dir = os.getcwd()

    # List all directories in the given folder
    directories = [d for d in os.listdir(project_dir) if os.path.isdir(os.path.join(project_dir, d))]

    # Check if there are any directories in the project directory
    if not directories:
        print("No directories found in the project folder.")
    else:
        # Display available directories for the user
        print("Available directories:")
        for i, directory in enumerate(directories, start=1):
            print(f"{i}. {directory}")
        
        # Ask the user to choose a directory
        try:
            choice = int(input("Enter the number of the directory you'd like to convert to sql: "))
            
            # Check if the choice is valid
            if 1 <= choice <= len(directories):
                selected_directory = directories[choice - 1]
                print(f"You've selected: {selected_directory}")
                # Optionally: Change into the selected directory
                selected_path = os.path.join(project_dir, selected_directory)
                print(selected_path)
                os.chdir(selected_path)
                print(f"Now in directory: {selected_path}")
                print(f"Converting contents of {selected_path}/traces JSON files to sql:")
                
                convert_to_sql(selected_path)
                print("done!")
            else:
                print("Invalid choice. Please select a valid directory.")
        except ValueError:
            print("Please enter a valid number.")

def main():
   

    # Sample data (replace with actual data)
    data = []
    choose_directory()
    # Close the connection
    cursor.close()
    conn.close()
# Only run the script if it is executed directly (not imported)
if __name__ == "__main__":
    main()
