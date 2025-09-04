import json
import sys
from typing import List, Dict, Any, Optional


def convert_to_sharegpt_format(input_data: List[Dict[str, Any]]) -> List[Dict[str, List[Dict[str, str]]]]:
    """
    Convert the input dataset to ShareGPT format.
    
    Args:
        input_data: List of conversation dictionaries
        
    Returns:
        List of conversations in ShareGPT format
    """
    converted_conversations = []
    
    for item in input_data:
        # Skip if everything is null (including Prompt)
        if (item.get("Prompt") is None and 
            all(item.get(f"Replies [{i}]") is None for i in range(1, 5))):
            print("Skipping conversation with all null values")
            continue
            
        # Skip if Prompt is null (can't start a conversation without it)
        if item.get("Prompt") is None:
            print("Skipping conversation with null Prompt")
            continue
            
        conversation = {
            "conversations": []
        }
        
        # Add system message if present
        system_message = item.get("System")
        if system_message:
            conversation["conversations"].append({
                "from": "system",
                "value": system_message
            })
        
        # Add the initial prompt from bot/assistant
        conversation["conversations"].append({
            "from": "gpt",  # Bot starts the conversation
            "value": item["Prompt"]
        })
        
        # Process replies alternating between human and gpt
        # Start with human (since bot already spoke)
        current_speaker = "human"
        
        for i in range(1, 5):  # Replies [1] through Replies [4]
            reply_key = f"Replies [{i}]"
            reply_value = item.get(reply_key)
            
            # Stop processing if we hit a null reply
            if reply_value is None:
                break
                
            conversation["conversations"].append({
                "from": current_speaker,
                "value": reply_value
            })
            
            # Alternate between human and gpt
            current_speaker = "gpt" if current_speaker == "human" else "human"
        
        # Only add conversations that have at least the initial prompt and one reply
        if len(conversation["conversations"]) > 1:  # More than just system message
            converted_conversations.append(conversation)
        else:
            print("Skipping conversation with no valid replies")
    
    return converted_conversations


def main():
    """
    Main function to handle file input/output and conversion.
    """
    # You can modify these file paths as needed
    input_file = "input_dataset.json"
    output_file = "output_sharegpt.json"
    
    # Allow command line arguments for file paths
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    
    try:
        # Read input file
        print(f"Reading from {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        
        # Convert to ShareGPT format
        print("Converting to ShareGPT format...")
        converted_data = convert_to_sharegpt_format(input_data)
        
        # Write output file
        print(f"Writing to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(converted_data, f, indent=2, ensure_ascii=False)
        
        print(f"Conversion completed! Processed {len(converted_data)} conversations.")
        
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_file}'")
        print("Usage: python script.py [input_file] [output_file]")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file - {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()