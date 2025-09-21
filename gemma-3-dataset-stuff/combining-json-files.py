import json
import random
import os
import argparse

def combine_jsons(directory_path, output_file, shuffle=True):
    combined_data = []

    # Reading each file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            print(f"Processing file: {filename}")
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    combined_data.extend(data)
                    print(f"Added {len(data)} entries from {filename}")
                except json.JSONDecodeError as e:
                    print(f"Error reading {filename}: {e}")

    # Shuffling the combined data if requested
    if shuffle:
        print("Shuffling combined data...")
        random.shuffle(combined_data)
        message = "Data combined and shuffled."
    else:
        message = "Data combined without shuffling."

    # Writing the data to a new JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=4)

    print(f"{message} Total entries: {len(combined_data)}")
    print(f"Output saved in {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Combine and optionally shuffle JSON files.')
    
    # Add arguments
    parser.add_argument('--input_dir', '-i', type=str, 
                        default='D:/datasets/RP/json',
                        help='Directory containing JSON files to combine')
    
    parser.add_argument('--output_file', '-o', type=str,
                        default='D:/datasets/RP/Combined.json',
                        help='Output file path for the combined JSON')
    
    parser.add_argument('--no_shuffle', '-ns', action='store_true',
                        help='If set, will combine files without shuffling')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Call the function with parsed arguments
    combine_jsons(args.input_dir, args.output_file, not args.no_shuffle)

if __name__ == "__main__":
    main()
