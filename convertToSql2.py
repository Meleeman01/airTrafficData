import json
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Database connection using SQLAlchemy
DATABASE_URL = "mysql://admin:OBbm7esj1!@127.0.0.1/flightsdb"
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

# Define flight and trace models using SQLAlchemy ORM
class Flight(Base):
    __tablename__ = 'flights'

    id = Column(Integer, primary_key=True)
    icao = Column(String(10))
    registration = Column(String(10), nullable=True)
    tailNo = Column(String(10), nullable=True)
    description = Column(String(100), nullable=True)
    time_stamp = Column(Integer)
    #noRegData = Column(Boolean, default=False)

    traces = relationship("FlightTrace", back_populates="flight")

class FlightTrace(Base):
    __tablename__ = 'flight_trace'

    id = Column(Integer, primary_key=True)
    flight_id = Column(Integer, ForeignKey('flights.id'))
    time = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Integer)
    speed = Column(Float)
    heading = Column(Float)
    vertical_speed = Column(Integer)
    squawk = Column(Integer)
    adsb_type = Column(String(50))
    flight = Column(String(50), nullable=True)
    alt_geom = Column(Integer, nullable=True)
    ias = Column(Float, nullable=True)
    tas = Column(Float, nullable=True)
    mach = Column(Float, nullable=True)
    oat = Column(Float, nullable=True)
    tat = Column(Float, nullable=True)
    track = Column(Float, nullable=True)
    track_rate = Column(Float, nullable=True)
    roll = Column(Float, nullable=True)
    mag_heading = Column(Float, nullable=True)
    true_heading = Column(Float, nullable=True)
    baro_rate = Column(Float, nullable=True)
    geom_rate = Column(Float, nullable=True)
    squawk_2 = Column(Integer, nullable=True)
    emergency = Column(String(50), nullable=True)
    category = Column(String(50), nullable=True)
    nav_qnh = Column(Float, nullable=True)
    nav_altitude_mcp = Column(Integer, nullable=True)
    nav_modes = Column(String(100), nullable=True)
    nic = Column(Integer, nullable=True)
    rc = Column(Integer, nullable=True)
    version = Column(Integer, nullable=True)
    nic_baro = Column(Integer, nullable=True)
    nac_p = Column(Integer, nullable=True)
    nac_v = Column(Integer, nullable=True)
    sil = Column(Integer, nullable=True)
    sil_type = Column(String(50), nullable=True)
    gva = Column(Float, nullable=True)
    sda = Column(Integer, nullable=True)
    alert = Column(Integer, nullable=True)
    spi = Column(Integer, nullable=True)
    geom_altitude = Column(Integer, nullable=True)
    baro_rate_2 = Column(Float, nullable=True)
    ias_2 = Column(Float, nullable=True)
    climb_rate_2 = Column(Float, nullable=True)

    flight = relationship("Flight", back_populates="traces")


# Create tables
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def convert_to_sql(release_name):
    current_dir = os.getcwd()
    traces_dir = f'{current_dir}/traces'
    os.chdir(traces_dir)

    print(os.getcwd(), traces_dir)

    # first go through traces directory
    for root, dirs, files in os.walk(traces_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                insert_flight_data(data)
            else:
                print("Not JSON!")

def insert_flight_data(flight_data):
    # Handle "noRegData" = true case by skipping data that doesn't have registration info
    if flight_data.get("dbFlags") == 0:
        # Skip this entry since dbFlags is 0
        return

    if flight_data.get("noRegData"):
        icao = flight_data["icao"]
        time_stamp = int(flight_data["timestamp"])
        print(time_stamp)

        flight = Flight(icao=icao, time_stamp=time_stamp)
        session.add(flight)
        session.commit()

        for trace in flight_data["trace"]:
            trace_values = trace[:-1]  # Remove the last value which is extra

            flight_trace = FlightTrace(
                flight_id=flight.id,
                time=trace_values[0],
                latitude=trace_values[1],
                longitude=trace_values[2],
                altitude=trace_values[3],
                speed=trace_values[4],
                heading=trace_values[5],
                vertical_speed=trace_values[6],
                squawk=trace_values[7],
                adsb_type=None,
                flight=None,
                alt_geom=None,
                ias=None,
                tas=None,
                mach=None,
                oat=None,
                tat=None,
                track=None,
                track_rate=None,
                roll=None,
                mag_heading=None,
                true_heading=None,
                baro_rate=None,
                geom_rate=None,
                squawk_2=None,
                emergency=None,
                category=None,
                nav_qnh=None,
                nav_altitude_mcp=None,
                nav_modes=None,
                nic=None,
                rc=None,
                version=None,
                nic_baro=None,
                nac_p=None,
                nac_v=None,
                sil=None,
                sil_type=None,
                gva=None,
                sda=None,
                alert=None,
                spi=None,
                geom_altitude=None,
                baro_rate_2=None,
                ias_2=None,
                climb_rate_2=None,
            )

            session.add(flight_trace)

        session.commit()
        return

    # Handle regular data with dbFlags != 0
    icao = flight_data["icao"]
    time_stamp = int(flight_data["timestamp"])

    registration = flight_data.get("r")
    tailNo = flight_data.get("t")
    description = flight_data.get("desc")

    flight = Flight(icao=icao, registration=registration, tailNo=tailNo, description=description, time_stamp=time_stamp)
    session.add(flight)
    session.commit()

    for trace in flight_data["trace"]:
        trace_values = trace[:-1]
        adsb_data = trace[8] if trace[8] else {}
        print("TRACEDATA: ",)
        flight_trace = FlightTrace(
            flight_id=flight.id,
            time=trace_values[0],
            latitude=trace_values[1],
            longitude=trace_values[2],
            altitude=trace_values[3],
            speed=trace_values[4],
            heading=trace_values[5],
            vertical_speed=trace_values[6],
            squawk=trace_values[7],
            adsb_type=adsb_data.get("type"),
            flight=adsb_data.get("flight"),
            alt_geom=adsb_data.get("alt_geom"),
            ias=adsb_data.get("ias"),
            tas=adsb_data.get("tas"),
            mach=adsb_data.get("mach"),
            oat=adsb_data.get("oat"),
            tat=adsb_data.get("tat"),
            track=adsb_data.get("track"),
            track_rate=adsb_data.get("track_rate"),
            roll=adsb_data.get("roll"),
            mag_heading=adsb_data.get("mag_heading"),
            true_heading=adsb_data.get("true_heading"),
            baro_rate=adsb_data.get("baro_rate"),
            geom_rate=adsb_data.get("geom_rate"),
            squawk_2=adsb_data.get("squawk"),
            emergency=adsb_data.get("emergency"),
            category=adsb_data.get("category"),
            nav_qnh=adsb_data.get("nav_qnh"),
            nav_altitude_mcp=adsb_data.get("nav_altitude_mcp"),
            nav_modes=None,
            nic=adsb_data.get("nic"),
            rc=adsb_data.get("rc"),
            version=adsb_data.get("version"),
            nic_baro=adsb_data.get("nic_baro"),
            nac_p=adsb_data.get("nac_p"),
            nac_v=adsb_data.get("nac_v"),
            sil=adsb_data.get("sil"),
            sil_type=adsb_data.get("sil_type"),
            gva=adsb_data.get("gva"),
            sda=adsb_data.get("sda"),
            alert=adsb_data.get("alert"),
            spi=adsb_data.get("spi"),
            geom_altitude=None,
            baro_rate_2=None,
            ias_2=None,
            climb_rate_2=None,
        )

        session.add(flight_trace)

    session.commit()

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
    choose_directory()
    session.close()

if __name__ == "__main__":
    main()
