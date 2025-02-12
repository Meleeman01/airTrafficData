-- DROP DATABASE IF EXISTS flightsdb;
-- CREATE DATABASE flightsdb;
--Create Flights table
CREATE TABLE flights (
    id INT AUTO_INCREMENT PRIMARY KEY,          -- Unique ID for each trace entry
    icao VARCHAR(50) NULL,
    registration VARCHAR(50) NULL,
    tailNo VARCHAR(50) NULL,
    description VARCHAR(100) NULL,
    time_stamp FLOAT NULL
);
--"icao":"06a101",
--"r":"A7-ALM",
--"t":"A359",
--"dbFlags":0,
--"desc":"AIRBUS A-350-900",
--"timestamp": 1704067200.000,

-- Create the flight_trace table to store the parsed data
CREATE TABLE flight_trace (
    id INT AUTO_INCREMENT PRIMARY KEY,          -- Unique ID for each trace entry
    flight_id INT NOT NULL,                     -- Foreign key to the flights table
    time FLOAT NULL,                            -- [0] Time value (e.g., 38101.64)
    latitude FLOAT NULL,                        -- [1] Latitude (e.g., 6.775445)
    longitude FLOAT NULL,                       -- [2] Longitude (e.g., 3.767363)
    altitude INT NULL,                          -- [3] Altitude (e.g., 39200)
    speed FLOAT NULL,                           -- [4] Speed (e.g., 482.8)
    heading FLOAT NULL,                         -- [5] Heading (e.g., 254.4)
    bit_flags_field INT NULL,                    -- [6] Vertical speed (e.g., 0)
    vertical_speed INT NULL,                            -- [7] Squawk code (e.g., -832)
    
    -- ADS-B data columns, each key from the JSON object as a separate column
    adsb_type VARCHAR(50) NULL,                 -- [9] ADS-B type (e.g., 'adsb_icao')
    flight VARCHAR(50) NULL,                    -- Flight identifier (e.g., 'ETH516')
    alt_baro VARCHAR(50) NULL,
    alt_geom INT NULL,                          -- Geometric altitude (e.g., 41850)
    gs FLOAT NULL,
    ias FLOAT NULL,                             -- Indicated Airspeed (IAS) (e.g., 254)
    tas FLOAT NULL,                             -- True Airspeed (e.g., 478)
    mach FLOAT NULL,
    wind_direction FLOAT NULL,
    wind_speed FLOAT NULL,                            -- Mach number (e.g., 0.832)
    oat FLOAT NULL,                             -- Outside Air Temperature (e.g., -56)
    tat FLOAT NULL,                             -- Total Air Temperature (e.g., -26)
    track FLOAT NULL,                           -- Track (e.g., 254.38)
    track_rate FLOAT NULL,                      -- Track rate (e.g., 0.00)
    roll FLOAT NULL,                            -- Roll (e.g., 0.35)
    mag_heading FLOAT NULL,                     -- Magnetic Heading (e.g., 256.29)
    true_heading FLOAT NULL,                    -- True Heading (e.g., 255.06)
    baro_rate INT NULL,                         -- Barometric rate (e.g., -832)
    geom_rate INT NULL,                         -- Geometric rate (e.g., -2240)
    squawk_code INT NULL,                          -- Squawk code (e.g., 5572)
    emergency VARCHAR(50) NULL,                 -- Emergency status (e.g., 'none')
    category VARCHAR(50) NULL,                  -- Category (e.g., 'A5')
    nav_qnh FLOAT NULL,                         -- QNH (e.g., 1012.8)
    nav_altitude_mcp INT NULL,                  -- MCP Altitude (e.g., 26016)
    nav_modes JSON NULL,
    seen_pos INT NULL,                        -- Navigation modes (e.g., ["autopilot", "vnav", "lnav", "tcas"])
    nic INT NULL,                               -- Navigation Integrity Category (e.g., 8)
    rc INT NULL,                                -- Resolution Capability (e.g., 186)
    version INT NULL,                           -- Version (e.g., 2)
    nic_baro INT NULL,                          -- Barometric Navigation Integrity Category (e.g., 1)
    nac_p INT NULL,                             -- Navigation Accuracy Category for Position (e.g., 9)
    nac_v INT NULL,                             -- Navigation Accuracy Category for Velocity (e.g., 1)
    sil INT NULL,                               -- SIL (e.g., 3)
    sil_type VARCHAR(50) NULL,                  -- SIL Type (e.g., 'perhour')
    gva INT NULL,                               -- GVA (e.g., 2)
    sda INT NULL,                               -- SDA (e.g., 2)
    alert INT NULL,                             -- Alert flag (e.g., 0)
    spi INT NULL,                               -- SPI flag (e.g., 0)
    -- Additional columns based on new data provided:
    geom_altitude INT NULL,                     -- [10] Geometric altitude (e.g., 28075)
    baro_rate_2 INT NULL,                       -- [11] Barometric rate (e.g., -1728)
    ias_2 FLOAT NULL,                           -- [12] Indicated Airspeed (IAS) (e.g., 282)
    climb_rate_2 FLOAT NULL,                    -- [13] Climb rate (e.g., 4.0)

    -- Foreign key constraint to the flights table`
    FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE CASCADE
);

