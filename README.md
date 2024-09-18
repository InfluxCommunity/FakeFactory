# FakeFactory
This is a work in progress as of September 18th.

Include your own influxdb credentials add them to your own secret.py file. 
To run, install the requirements.txt file then run the python FakeData.py file. 


Ideal Values:
Temperature: 20-100°C (general range for various temperature sensors).
Pressure: 0-10 bars for machines like the water heater, filtration, etc.
Flow: 100-1000 liters per hour.
Level: 0-100% for water or tea tank levels.
pH: 4-6 pH (slightly acidic for tea steeping).
Efficiency: 80-100% efficiency for separation processes.
Vibration: 0-7 mm/s for normal operation of mechanical parts.
Torque: 50-500 Nm for mixing or agitation torque.
Position: 0-2 mm deviation for label alignment.
Humidity: 30-70% for the cooling tunnel.


Work Todo: 
Add Grafana JSON files once created
Add a simple UI where you can cause an outage for anomoly detection. Add those bad values into the DB