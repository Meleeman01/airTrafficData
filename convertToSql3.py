import json
import mysql.connector
import os
import sys 
# Connection parameters (update with your credentials)
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="admin",
    password="",
    database="flightsdb"
)
cursor = conn.cursor()

# # Drop and create the database
# cursor.execute("DROP DATABASE IF EXISTS flightsdb")
# cursor.execute("CREATE DATABASE flightsdb")
# cursor.execute("USE flightsdb")

# # Create the flights table
# create_flights_table = """
# CREATE TABLE flights (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     icao VARCHAR(50) NULL,
#     registration VARCHAR(50) NULL,
#     tailNo VARCHAR(50) NULL,
#     description VARCHAR(100) NULL,
#     time_stamp FLOAT NULL
# )
# """
# cursor.execute(create_flights_table)

# # Create the flight_trace table
# create_flight_trace_table = """
# CREATE TABLE flight_trace (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     flight_id INT NOT NULL,
#     time FLOAT NULL,
#     latitude FLOAT NULL,
#     longitude FLOAT NULL,
#     altitude INT NULL,
#     speed FLOAT NULL,
#     heading FLOAT NULL,
#     bit_flags_field INT NULL,
#     vertical_speed INT NULL,
#     adsb_type VARCHAR(50) NULL,
#     flight VARCHAR(50) NULL,
#     alt_baro VARCHAR(50) NULL,
#     alt_geom INT NULL,
#     gs FLOAT NULL,
#     ias FLOAT NULL,
#     tas FLOAT NULL,
#     mach FLOAT NULL,
#     wind_direction FLOAT NULL,
#     wind_speed FLOAT NULL,
#     oat FLOAT NULL,
#     tat FLOAT NULL,
#     track FLOAT NULL,
#     track_rate FLOAT NULL,
#     roll FLOAT NULL,
#     mag_heading FLOAT NULL,
#     true_heading FLOAT NULL,
#     baro_rate INT NULL,
#     geom_rate INT NULL,
#     squawk_code INT NULL,
#     emergency VARCHAR(50) NULL,
#     category VARCHAR(50) NULL,
#     nav_qnh FLOAT NULL,
#     nav_altitude_mcp INT NULL,
#     nav_modes JSON NULL,
#     seen_pos INT NULL,
#     nic INT NULL,
#     rc INT NULL,
#     version INT NULL,
#     nic_baro INT NULL,
#     nac_p INT NULL,
#     nac_v INT NULL,
#     sil INT NULL,
#     sil_type VARCHAR(50) NULL,
#     gva INT NULL,
#     sda INT NULL,
#     alert INT NULL,
#     spi INT NULL,
#     geom_altitude INT NULL,
#     baro_rate_2 INT NULL,
#     ias_2 FLOAT NULL,
#     climb_rate_2 FLOAT NULL,
#     FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE CASCADE
# )
# """
# cursor.execute(create_flight_trace_table)

# Example JSON data (this could be loaded from a file or other source)
json_data = '''{
    "icao":"3c66b0",
    "r":"D-AIUP",
    "t":"A320",
    "dbFlags":0,
    "desc":"AIRBUS A-320",
    "timestamp": 1663259853.016,
    "trace":[
        [7016.59,49.263300,10.614239,25125,446.5,309.0,0,-2176,
            {"type":"adsb_icao","flight":"DLH7YA  ","alt_geom":25875,"ias":335,"tas":484,"mach":0.796,"wd":297,"ws":40,"oat":-30,"tat":1,"track":309.00,"track_rate":-0.53,"roll":-10.72,"mag_heading":304.28,"true_heading":308.02,"baro_rate":-2176,"geom_rate":-2208,"squawk":"1000","category":"A3","nav_qnh":1012.8,"nav_altitude_mcp":14016,"nic":8,"rc":186,"version":2,"nic_baro":1,"nac_p":8,"nac_v":0,"sil":3,"sil_type":"perhour","gva":2,"sda":2,"alert":0,"spi":0},
            "adsb_icao",25875,-2208,335,-10.7],
        [7024.85,49.273589,10.593278,24825,446.0,306.6,0,-2176,null,"adsb_icao",25550,-2144,337,-1.6],
        [7035.67,49.286865,10.565890,24425,446.8,306.5,0,-2176,null,"adsb_icao",25150,-2144,339,0.3],
        [7046.71,49.300403,10.537985,24025,446.8,306.5,0,-2176,null,"adsb_icao",24775,-2176,341,0.3],
        [7057.80,49.314042,10.509941,23625,445.2,306.7,0,-2176,
            {"type":"adsb_icao","flight":"DLH7YA  ","alt_geom":24325,"ias":339,"tas":482,"mach":0.784,"wd":296,"ws":37,"oat":-24,"tat":6,"track":306.69,"track_rate":0.00,"roll":0.18,"mag_heading":302.17,"true_heading":305.89,"baro_rate":-2176,"geom_rate":-2176,"squawk":"1000","category":"A3","nav_qnh":1012.8,"nav_altitude_mcp":14016,"nic":8,"rc":186,"version":2,"nic_baro":1,"nac_p":8,"nac_v":0,"sil":3,"sil_type":"perhour","gva":2,"sda":2,"alert":0,"spi":0},
            "adsb_icao",24325,-2176,339,0.2],
        [7068.82,49.327469,10.482225,23250,443.2,306.6,0,-2112,null,"adsb_icao",23925,-2144,340,0.2],
        [7080.53,49.341694,10.452841,22875,441.2,306.4,0,-1728,null,"adsb_icao",23550,-1728,341,-0.2]
    ]
}'''
#data = json.loads(json_data)

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

def insert_flight_data(data):
    # --- Insert into flights table ---
    insert_flights = """
    INSERT INTO flights (icao, registration, tailNo, description, time_stamp)
    VALUES (%s, %s, %s, %s, %s)
    """
    flight_values = (
        data.get("icao"),
        data.get("r"),
        data.get("t"),
        data.get("desc"),
        data.get("timestamp")
    )
    cursor.execute(insert_flights, flight_values)
    flight_id = cursor.lastrowid  # We'll use this as the foreign key in flight_trace

    # --- Insert each trace record into flight_trace ---
    # Note: This sample insert covers only some of the available columns.
    # You can extend the mapping as needed.
    insert_trace = """
    INSERT INTO flight_trace (
        flight_id, time, latitude, longitude, altitude, speed, heading, bit_flags_field, vertical_speed,
        adsb_type, flight, alt_baro, alt_geom, gs, ias, tas, mach, wind_direction,
        wind_speed, oat, tat, track, track_rate, roll, mag_heading, true_heading,
        baro_rate, geom_rate, squawk_code, emergency, category, nav_qnh, nav_altitude_mcp, seen_pos,
        nic, rc, version, nic_baro, nac_p, nac_v,
        sil, sil_type, gva, sda, alert, spi
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, 
        %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s
    )
    """
   
    for trace in data.get("trace", []):
        # Base fields from the trace array (indices 0-7)
        trace_time      = trace[0] if len(trace) > 0 else None
        latitude        = trace[1] if len(trace) > 1 else None
        longitude       = trace[2] if len(trace) > 2 else None
        altitude        = trace[3] if len(trace) > 3 else None
        speed           = trace[4] if len(trace) > 4 else None
        heading         = trace[5] if len(trace) > 5 else None
        bit_flags_field = trace[6] if len(trace) > 6 else None
        vertical_speed  = trace[7] if len(trace) > 7 else None

        if altitude == 'ground':
            altitude = 0
        # Initialize ADS-B (extended) fields to None

        adsb_type = None
        flight = None 
        alt_baro = None
        alt_geom = None
        gs = None
        ias = None 
        tas = None 
        mach = None 
        wind_direction = None
        wind_speed = None 
        oat = None 
        tat = None
        track = None
        track_rate = None
        roll = None 
        mag_heading = None 
        true_heading = None
        baro_rate = None 
        geom_rate = None 
        squawk_code = None 
        emergency = None 
        category = None 
        nav_qnh = None 
        nav_altitude_mcp = None 
        seen_pos = None
        nic = None 
        rc = None 
        version = None
        nic_baro = None 
        nac_p = None 
        nac_v = None      
        sil = None 
        sil_type = None 
        gva = None 
        sda = None 
        alert = None 
        spi = None

        print(type(trace[8]))
        print(trace[8])
        # Check if an ADS-B JSON object is present at index 8.
        if len(trace) > 8 and isinstance(trace[8], dict):
            print('made it here')
            adsb_data = trace[8]
            adsb_type = adsb_data.get("type")
            flight = adsb_data.get("flight")
            alt_baro = adsb_data.get("alt_baro")
            alt_geom = adsb_data.get("alt_geom")
            gs = adsb_data.get("gs")
            ias = adsb_data.get("ias")
            tas = adsb_data.get("tas")
            mach = adsb_data.get("mach")
            wind_direction = adsb_data.get("wd")
            wind_speed = adsb_data.get("ws")
            oat = adsb_data.get("oat")
            tat = adsb_data.get("tat")
            track = adsb_data.get("track")
            track_rate = adsb_data.get("track_rate")
            roll = adsb_data.get("roll")
            mag_heading = adsb_data.get("mag_heading")
            true_heading = adsb_data.get("true_heading")
            baro_rate = adsb_data.get("baro_rate")
            geom_rate = adsb_data.get("geom_rate")
            # Convert squawk (which may be a string) to int if possible
            squawk = adsb_data.get("squawk")
            try:
                squawk_code = int(squawk) if squawk is not None else None
            except ValueError:
                squawk_code = None
            emergency = adsb_data.get("emergency")
            category = adsb_data.get("category")
            nav_qnh = adsb_data.get("nav_qnh")
            nav_altitude_mcp = adsb_data.get("nav_altitude_mcp")
            seen_pos = adsb_data.get("seen_pos")
            nic = adsb_data.get("nic")
            rc = adsb_data.get("rc")
            version = adsb_data.get("version")
            nic_baro = adsb_data.get("nic_baro")
            nac_p = adsb_data.get("nac_p")
            nac_v = adsb_data.get("nac_v")
            sil = adsb_data.get("sil")
            sil_type = adsb_data.get("sil_type")
            gva = adsb_data.get("gva")
            sda = adsb_data.get("sda")
            alert = adsb_data.get("alert")
            spi = adsb_data.get("spi")
            # Also check if index 9 is present; sometimes it redundantly provides the ADS-B type.
            if len(trace) > 9:
                adsb_type = trace[9] if not adsb_type else adsb_type
            
        else:
            # If no ADS-B object, use the available indices (if any)
            if len(trace) > 9:
                adsb_type = trace[9]
            if len(trace) > 10:
                alt_geom = trace[10]
            if len(trace) > 11:
                geom_rate = trace[11]
            if len(trace) > 12:
                ias_2 = trace[12]
            if len(trace) > 13:
                climb_rate_2 = trace[13]
        print(adsb_type,
                flight, 
                alt_baro, 
                alt_geom, 
                gs, 
                ias,  
                tas,  
                mach,  
                wind_direction, 
                wind_speed,  
                oat, 
                tat, 
                track, 
                track_rate, 
                roll,  
                mag_heading,  
                true_heading, 
                baro_rate,  
                geom_rate,  
                squawk_code,  
                emergency,  
                category,  
                nav_qnh,  
                nav_altitude_mcp,  
                seen_pos, 
                nic,  
                rc,  
                version, 
                nic_baro,  
                nac_p,  
                nac_v,       
                sil,  
                sil_type,  
                gva,  
                sda,  
                alert,  
                spi 
            )
        print(insert_trace)


        # Execute the INSERT for the trace record
        cursor.execute(insert_trace, (
            flight_id, trace_time, latitude, longitude, altitude, speed, heading,
            bit_flags_field, vertical_speed,
            adsb_type, flight, alt_baro, alt_geom, gs, ias, tas,
            mach, wind_direction, wind_speed, oat, tat,
            track, track_rate, roll, mag_heading, true_heading,
            baro_rate, geom_rate, squawk_code, emergency, category, nav_qnh, nav_altitude_mcp,
            seen_pos, nic, rc, version, nic_baro, nac_p, nac_v,
            sil, sil_type, gva, sda, alert, spi
        ))
        conn.commit()

    
    print("Data inserted successfully!")

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
    cursor.close()
    conn.close()
    # Close the connection
# Only run the script if it is executed directly (not imported)
if __name__ == "__main__":
    main()