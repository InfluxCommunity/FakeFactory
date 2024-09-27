#This is where we will create our fake facory data and send it to influxdb
import pandas as pd
import random
import time
import threading
from flask import Flask, request, jsonify, render_template
from influxdb_client_3 import InfluxDBClient3, Point
import secret

# Load the dataset
dataset_path = 'files/milktea.csv'
df = pd.read_csv(dataset_path)

# Initialize the InfluxDB client
client = InfluxDBClient3(token=secret.INFLUXDB_TOKEN, host=secret.INFLUXDB_HOST, org=secret.INFLUXDB_ORG, database=secret.INFLUXDB_DB)

# Extract unique machine information from the dataset
machines = df[['equipment_name', 'equipment_type', 'equipment_uuid']].drop_duplicates().to_dict('records')

# Adding more machines
for i in range(8):  # Adjust this number to add more machines if needed
    new_machine = random.choice(machines).copy()
    new_machine["equipment_uuid"] = f"uuid{25+i}{new_machine['equipment_name'][:2]}{i}"
    machines.append(new_machine)

# Flask app setup
app = Flask(__name__)
factory_running = False
factory_thread = None


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
def simulate_machine_data(machines, df):
    for machine in machines:
        # Filter relevant tags for the current machine
        machine_tags = df[df['equipment_uuid'] == machine['equipment_uuid']]
        
        for _, row in machine_tags.iterrows():
            # Generate a fake value based on the tag_type
            fake_value = generate_fake_value(row['tag_type'])
            
            # Create an InfluxDB Point for each tag
            point = Point("machine_data") \
                .tag("area_factory", row['area_factory']) \
                .tag("equipment_manufacturer", row['equipment_manufacturer']) \
                .tag("equipment_name", machine['equipment_name']) \
                .tag("equipment_type", machine['equipment_type']) \
                .tag("line_name", row['line_name']) \
                .tag("site_name", row['site_name']) \
                .tag("tag_name", row['tag_name']) \
                .tag("equipment_uuid", machine['equipment_uuid']) \
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

# Function to run the factory simulation
def simulate_factory_operation():
    global factory_running
    while factory_running:
        simulate_machine_data(machines, df)
        print("Factory is running... Data sent to InfluxDB.")
        time.sleep(5)  # Adjust the timing as needed

# Function to simulate bad data generation
def send_bad_data(machine, duration):
    end_time = time.time() + (int(duration) * 60)
    
    while time.time() < end_time:
        # Fetch the relevant tags for the machine
        machine_tags = df[df['equipment_uuid'] == machine]

        
        for _, row in machine_tags.iterrows():
            # Generate a bad value based on the tag_type
            if row['tag_type'] == 'temperature':
                fake_value = random.uniform(150, 200)  # Out of range temperature (e.g., too hot)
            elif row['tag_type'] == 'pressure':
                fake_value = random.uniform(-5, -1)  # Negative pressure, which is unrealistic
            elif row['tag_type'] == 'flow':
                fake_value = random.uniform(0, 10)  # Extremely low flow rate, indicating a blockage
            elif row['tag_type'] == 'pH':
                fake_value = random.uniform(0, 2)  # pH too acidic
            elif row['tag_type'] == 'vibration':
                fake_value = random.uniform(10, 20)  # Excessive vibration
            else:
                fake_value = random.uniform(1000, 2000)  # Some generic high value for other tags
            
            # Create an InfluxDB Point for the bad data
            point = Point("machine_data") \
                .tag("area_factory", row['area_factory']) \
                .tag("equipment_manufacturer", row['equipment_manufacturer']) \
                .tag("equipment_name", machine) \
                .tag("equipment_type", row['equipment_type']) \
                .tag("line_name", row['line_name']) \
                .tag("site_name", row['site_name']) \
                .tag("tag_name", row['tag_name']) \
                .tag("equipment_uuid", machine) \
                .tag("line_uuid", row['line_uuid']) \
                .tag("site_uuid", row['site_uuid']) \
                .tag("tag_uuid", row['tag_uuid']) \
                .field("value", fake_value) \
                .field("tag_unit", row['tag_unit']) \
                .field("tag_description", row['tag_description']) \
                .field("tag_type", row['tag_type']) \
                .field("work_center_type", row['work_center_type']) \
                .time(int(time.time() * 1e9))  # Timestamp in nanoseconds for InfluxDB
            
            # Send the bad data to InfluxDB
            client.write(point)
        
        print(f"Sent bad data for {machine}...{end_time}")
        time.sleep(5)  # Delay between sending bad data points
    
    print(f"Stopped sending bad data for {machine}.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate_break', methods=['POST'])
def simulate_break():
    data = request.get_json()
    machine = data['machine']
    duration = data['duration']
    
    # Start a new thread to simulate bad data generation
    threading.Thread(target=send_bad_data, args=(machine, duration)).start()

    return jsonify({"message": f"Simulating break for {machine} for {duration} minutes."})


@app.route('/start_factory', methods=['POST'])
def start_factory():
    global factory_running, factory_thread
    if not factory_running:
        factory_running = True
        factory_thread = threading.Thread(target=simulate_factory_operation)
        factory_thread.start()
        return jsonify({"message": "Factory started."})
    else:
        return jsonify({"message": "Factory is already running."})

@app.route('/stop_factory', methods=['POST'])
def stop_factory():
    global factory_running
    if factory_running:
        factory_running = False
        if factory_thread:
            factory_thread.join()
        return jsonify({"message": "Factory stopped."})
    else:
        return jsonify({"message": "Factory is not running."})

if __name__ == '__main__':
    app.run(debug=True)