#This is where we will create our fake facory data and send it to influxdb
import pandas as pd
import random
import time
import uuid
from influxdb_client_3 import InfluxDBClient3, Point
import secret

# Load the dataset
dataset_path = 'files/milktea.csv'
df = pd.read_csv(dataset_path)

# Initialize the InfluxDB client
client = InfluxDBClient3(token=secret.INFLUXDB_TOKEN, host=secret.INFLUXDB_HOST, org=secret.INFLUXDB_ORG, database=secret.INFLUXDB_DB)

# Function to generate random values for each tag type
def generate_fake_value(tag_type):
    if tag_type == 'temperature':
        return round(random.uniform(20, 100), 2)  # General range for temperature sensors
    elif tag_type == 'pressure':
        return round(random.uniform(0, 10), 2)  # Range for pressure (bars)
    elif tag_type == 'flow':
        return round(random.uniform(100, 1000), 2)  # Flow rate in liters per hour
    elif tag_type == 'level':
        return round(random.uniform(0, 100), 2)  # Level in percentage (0% to 100%)
    elif tag_type == 'time':
        return round(random.uniform(0, 60), 2)  # Time in minutes or seconds
    elif tag_type == 'density':
        return round(random.uniform(1, 100), 2)  # Grams per liter (tea concentration)
    elif tag_type == 'pH':
        return round(random.uniform(4, 6), 2)  # pH for tea (slightly acidic range)
    elif tag_type == 'speed':
        return round(random.uniform(50, 500), 2)  # RPM or bottles per minute
    elif tag_type == 'efficiency':
        return round(random.uniform(80, 100), 2)  # Efficiency in percent
    elif tag_type == 'vibration':
        return round(random.uniform(0, 7), 2)  # Vibration in mm/s (normal operating range)
    elif tag_type == 'power':
        return round(random.uniform(1, 100), 2)  # Kilowatts for power consumption
    elif tag_type == 'torque':
        return round(random.uniform(50, 500), 2)  # Torque in Newton-meters
    elif tag_type == 'position':
        return round(random.uniform(0, 2), 2)  # Positioning accuracy in mm
    elif tag_type == 'humidity':
        return round(random.uniform(30, 70), 2)  # Humidity in percentage
    else:
        return round(random.uniform(0, 100), 2)  # Generic random value

# Function to simulate the generation of fake data for each row in the dataset
def simulate_machine_data(df):
    for index, row in df.iterrows():
        # Generate a fake value based on the tag_type
        fake_value = generate_fake_value(row['tag_type'])
        
        # Create an InfluxDB Point for each row, including all fields
        point = Point("machine_data") \
            .tag("area_factory", row['area_factory']) \
            .tag("equipment_manufacturer", row['equipment_manufacturer']) \
            .tag("equipment_name", row['equipment_name']) \
            .tag("equipment_type", row['equipment_type']) \
            .tag("line_name", row['line_name']) \
            .tag("site_name", row['site_name']) \
            .tag("tag_name", row['tag_name']) \
            .tag("equipment_uuid", row['equipment_uuid']) \
            .tag("line_uuid", row['line_uuid']) \
            .tag("site_uuid", row['site_uuid']) \
            .tag("tag_uuid", row['tag_uuid']) \
            .field("value", fake_value) \
            .field("tag_unit", row['tag_unit']) \
            .field("tag_description", row['tag_description']) \
            .field("tag_type", row['tag_type']) \
            .field("work_center_type", row['work_center_type']) \
            .time(int(time.time() * 1e9))  # Timestamp in nanoseconds for InfluxDB
        
        # Write the point to InfluxDB
        client.write(point)

# Main loop to generate and send data continuously
while True:
    # Simulate and send data to InfluxDB
    simulate_machine_data(df)
    print("Data sent to InfluxDB")
    # Sleep for a while before generating the next batch (simulate data coming every 5 seconds)
    time.sleep(5)