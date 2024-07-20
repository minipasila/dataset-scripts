import json
import random
import os

def combine_and_shuffle_jsons(directory_path, output_file):
    combined_data = []

    # Reading each file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:  # Specify the encoding here
                data = json.load(f)
                combined_data.extend(data)

    # Shuffling the combined data
    random.shuffle(combined_data)

    # Writing the mixed data to a new JSON file
    with open(output_file, 'w', encoding='utf-8') as f:  # Also specify the encoding on writing
        json.dump(combined_data, f, ensure_ascii=False, indent=4)

    print(f"Data combined and shuffled. Output is saved in {output_file}")

# Customize the following variables
directory_path = 'path/to/your/jsonfiles'
output_file = 'path/to/your/output-file.json'

combine_and_shuffle_jsons(directory_path, output_file)
