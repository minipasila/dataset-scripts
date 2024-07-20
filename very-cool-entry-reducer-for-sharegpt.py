import json

# Function to load JSON data from a file
def load_json_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

# Function to save JSON data to a file
def save_json_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

# Main function to trim the JSON data
def trim_json_data(input_file, output_file, max_entries):
    # Load data from the original JSON file
    data = load_json_file(input_file)
    
    if isinstance(data, list):  # assuming the root of the JSON is a list
        # Trim data to maintain only the first 'max_entries' elements
        trimmed_data = data[:max_entries]
    else:
        print("The JSON root is not a list. Check your JSON structure.")
        return

    # Save the trimmed data to a new JSON file
    save_json_file(trimmed_data, output_file)
    print(f"Data has been trimmed and saved to {output_file}")

# Replace 'your_input.json' and 'your_output.json' with your actual file paths
input_json_file = 'original-file.json'
output_json_file = 'output-file.json'
max_id_count = 1000 # Arbitrary number of examples you want the new json file to contain.

# Execute the trimming function
trim_json_data(input_json_file, output_json_file, max_id_count)
