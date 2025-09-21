#!/usr/bin/env python3
"""
JSON From Field Validator

This script checks all JSON files in a specified folder to ensure that
the "from" fields in conversations contain only valid values: system, human, gpt
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Set

def validate_json_file(file_path: Path) -> Dict[str, Any]:
    """
    Validate a single JSON file for correct "from" values.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing validation results
    """
    valid_from_values = {"system", "human", "gpt"}
    result = {
        "file": file_path.name,
        "valid": True,
        "errors": [],
        "invalid_from_values": set()
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different ShareGPT formats
        conversations_list = []
        
        if isinstance(data, list):
            # Format: [{"conversations": [...]}, {"conversations": [...]}]
            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    result["valid"] = False
                    result["errors"].append(f"Item {i} in array is not a dictionary")
                    continue
                
                if "conversations" not in item:
                    result["valid"] = False
                    result["errors"].append(f"Item {i} missing 'conversations' key")
                    continue
                
                if not isinstance(item["conversations"], list):
                    result["valid"] = False
                    result["errors"].append(f"Item {i}: 'conversations' should be a list")
                    continue
                
                conversations_list.extend([(i, j, conv) for j, conv in enumerate(item["conversations"])])
        
        elif isinstance(data, dict) and "conversations" in data:
            # Format: {"conversations": [...]}
            if not isinstance(data["conversations"], list):
                result["valid"] = False
                result["errors"].append("'conversations' should be a list")
                return result
            
            conversations_list = [(0, i, conv) for i, conv in enumerate(data["conversations"])]
        
        else:
            result["valid"] = False
            result["errors"].append("Invalid JSON structure: expected array of objects with 'conversations' or single object with 'conversations'")
            return result
        
        # Check each conversation entry
        for item_idx, conv_idx, conversation in conversations_list:
            if not isinstance(conversation, dict):
                result["valid"] = False
                if len(data) > 1 if isinstance(data, list) else False:
                    result["errors"].append(f"Item {item_idx}, conversation {conv_idx} is not a dictionary")
                else:
                    result["errors"].append(f"Conversation item {conv_idx} is not a dictionary")
                continue
            
            if "from" not in conversation:
                result["valid"] = False
                if len(data) > 1 if isinstance(data, list) else False:
                    result["errors"].append(f"Item {item_idx}, conversation {conv_idx} missing 'from' field")
                else:
                    result["errors"].append(f"Conversation item {conv_idx} missing 'from' field")
                continue
            
            from_value = conversation["from"]
            if not isinstance(from_value, str):
                result["valid"] = False
                if len(data) > 1 if isinstance(data, list) else False:
                    result["errors"].append(f"Item {item_idx}, conversation {conv_idx}: 'from' field is not a string")
                else:
                    result["errors"].append(f"Conversation item {conv_idx}: 'from' field is not a string")
                continue
            
            if from_value not in valid_from_values:
                result["valid"] = False
                result["invalid_from_values"].add(from_value)
                if len(data) > 1 if isinstance(data, list) else False:
                    result["errors"].append(f"Item {item_idx}, conversation {conv_idx}: invalid 'from' value '{from_value}'")
                else:
                    result["errors"].append(f"Conversation item {conv_idx}: invalid 'from' value '{from_value}'")
    
    except json.JSONDecodeError as e:
        result["valid"] = False
        result["errors"].append(f"JSON decode error: {str(e)}")
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Error reading file: {str(e)}")
    
    return result

def check_folder(folder_path: str) -> None:
    """
    Check all JSON files in the specified folder.
    
    Args:
        folder_path: Path to the folder containing JSON files
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return
    
    if not folder.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        return
    
    # Get all JSON files
    json_files = list(folder.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in '{folder_path}'.")
        return
    
    print(f"Checking {len(json_files)} JSON files in '{folder_path}'...")
    print("=" * 60)
    
    valid_files = []
    invalid_files = []
    
    for json_file in sorted(json_files):
        result = validate_json_file(json_file)
        
        if result["valid"]:
            valid_files.append(result["file"])
        else:
            invalid_files.append(result)
    
    # Print results
    if valid_files:
        print(f"\n✅ VALID FILES ({len(valid_files)}):")
        for file in valid_files:
            print(f"  • {file}")
    
    if invalid_files:
        print(f"\n❌ INVALID FILES ({len(invalid_files)}):")
        for result in invalid_files:
            print(f"\n  📁 {result['file']}:")
            for error in result["errors"]:
                print(f"    - {error}")
            
            if result["invalid_from_values"]:
                print(f"    - Found invalid 'from' values: {', '.join(result['invalid_from_values'])}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"SUMMARY:")
    print(f"  Total files: {len(json_files)}")
    print(f"  Valid files: {len(valid_files)}")
    print(f"  Invalid files: {len(invalid_files)}")
    
    if invalid_files:
        print(f"\n⚠️  {len(invalid_files)} file(s) need attention!")
    else:
        print(f"\n🎉 All files are valid!")

def main():
    """Main function to run the validator."""
    if len(sys.argv) != 2:
        print("Usage: python json_validator.py <folder_path>")
        print("Example: python json_validator.py ./my_json_files/")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    check_folder(folder_path)

if __name__ == "__main__":
    main()