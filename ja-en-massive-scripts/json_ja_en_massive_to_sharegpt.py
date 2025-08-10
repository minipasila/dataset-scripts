import json
import argparse

def convert_to_sharegpt(input_file, output_file, system_message="You are a helpful assistant that translates Japanese to English."):
    """
    Converts JSON data with 'src' and 'trg' fields to ShareGPT format.
    
    Args:
        input_file (str): Path to the input JSON file (from previous extraction)
        output_file (str): Path to the output ShareGPT formatted JSON file
        system_message (str): Default system message to include in each conversation
    """
    try:
        # Load the extracted data
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to ShareGPT format
        sharegpt_data = []
        
        for item in data:
            # Skip entries that don't have both src and trg
            if 'src' not in item or 'trg' not in item:
                continue
                
            # Create a conversation entry
            conversation = {
                "conversations": [
                    {
                        "from": "system",
                        "value": system_message
                    },
                    {
                        "from": "human",
                        "value": item['src'].strip()
                    },
                    {
                        "from": "gpt",
                        "value": item['trg'].strip()
                    }
                ]
            }
            
            # Add to our ShareGPT dataset
            sharegpt_data.append(conversation)
        
        # Write the ShareGPT formatted data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sharegpt_data, f, ensure_ascii=False, indent=4)
            
        print(f"Successfully converted {len(sharegpt_data)} conversations to ShareGPT format in {output_file}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert JSON data to ShareGPT format')
    parser.add_argument('input_file', help='Path to the input JSON file')
    parser.add_argument('output_file', help='Path to the output ShareGPT formatted JSON file')
    parser.add_argument('--system_message', default="You are a helpful assistant that translates Japanese to English.", 
                        help='System message to include in each conversation')
    
    args = parser.parse_args()
    
    convert_to_sharegpt(args.input_file, args.output_file, args.system_message)
