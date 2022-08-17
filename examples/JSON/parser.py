import json
import sys

# Open the file passed as argument 1 or default to UNKNOWN_DUT.json file.
# Open the file as read only specified by the 'r' flag.
with open(sys.argv[1] if len(sys.argv) > 1 else "UNKNOWN_DUT.json", 'r') as json_file:
    # Parse the data from the JSON file.
    json_data: dict = json.load(json_file)

# Process the results.
print(f"General:")
print(f"\tDUT ID: {json_data.get('dut_id')}")
print(f"\tOutcome: {json_data.get('outcome')}")

print(f"Phases:")
for phase in json_data.get('phases'):
    print(f"\t- {phase.get('name')}:")

    measurements = phase.get('measurements')
    for measurement_key in phase.get('measurements'):
        measurement_value = measurements.get(measurement_key)
        print(f"\t\t- {measurement_key} [{measurement_value.get('outcome')}]: {measurement_value.get('measured_value')}{measurement_value.get('units').get('suffix')}")
