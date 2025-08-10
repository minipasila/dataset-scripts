import json
import argparse
import numpy as np
from transformers import AutoTokenizer
from tqdm import tqdm

def filter_by_token_count(input_file, output_file, max_tokens=16384, model_name="shisa-ai/shisa-v2-mistral-nemo-12b"):
    """
    Filters conversations from a ShareGPT dataset based on token count.
    
    Args:
        input_file (str): Path to the input ShareGPT-formatted JSON file
        output_file (str): Path to the filtered output JSON file
        max_tokens (int): Maximum allowed tokens per conversation
        model_name (str): Name of the model/tokenizer from HuggingFace
    """
    try:
        # Load the tokenizer
        print(f"Loading tokenizer for {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Load the dataset
        print(f"Loading dataset from {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        original_count = len(data)
        print(f"Original dataset contains {original_count} conversations")
        
        # Prepare filtered data and statistics
        filtered_data = []
        token_counts = []
        kept_counts = []
        removed_counts = []
        
        print(f"Filtering conversations with more than {max_tokens} tokens...")
        
        # Process each conversation
        for conversation_item in tqdm(data):
            conversations = conversation_item.get("conversations", [])
            
            # Count total tokens in this conversation
            total_tokens = 0
            for message in conversations:
                content = message.get("value", "")
                tokens = tokenizer.encode(content)
                total_tokens += len(tokens)
            
            token_counts.append(total_tokens)
            
            # Keep or filter based on token count
            if total_tokens <= max_tokens:
                filtered_data.append(conversation_item)
                kept_counts.append(total_tokens)
            else:
                removed_counts.append(total_tokens)
        
        # Write filtered data to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=4)
        
        # Calculate statistics
        kept_count = len(filtered_data)
        removed_count = original_count - kept_count
        
        # Print statistics
        print("\nFiltering Results:")
        print(f"Original conversations: {original_count}")
        print(f"Kept conversations: {kept_count} ({kept_count/original_count*100:.2f}%)")
        print(f"Removed conversations: {removed_count} ({removed_count/original_count*100:.2f}%)")
        
        if kept_counts:
            print(f"\nKept conversations token statistics:")
            print(f"  Average: {np.mean(kept_counts):.2f} tokens")
            print(f"  Median: {np.median(kept_counts):.2f} tokens")
            print(f"  Min: {np.min(kept_counts)} tokens")
            print(f"  Max: {np.max(kept_counts)} tokens")
        
        if removed_counts:
            print(f"\nRemoved conversations token statistics:")
            print(f"  Average: {np.mean(removed_counts):.2f} tokens")
            print(f"  Median: {np.median(removed_counts):.2f} tokens")
            print(f"  Min: {np.min(removed_counts)} tokens")
            print(f"  Max: {np.max(removed_counts)} tokens")
            
        # Token histogram for the original dataset
        ranges = [0, 512, 1024, 2048, 4096, 8192, 16384, float('inf')]
        range_names = ["0-512", "513-1024", "1025-2048", "2049-4096", "4097-8192", "8193-16384", "16385+"]
        histogram = [0] * (len(ranges) - 1)
        
        for count in token_counts:
            for i in range(len(ranges) - 1):
                if ranges[i] <= count < ranges[i+1]:
                    histogram[i] += 1
                    break
        
        print("\nOriginal Dataset Token Distribution:")
        for i, count in enumerate(histogram):
            print(f"{range_names[i]}: {count} conversations ({count/original_count*100:.2f}%)")
            
        print(f"\nFiltered dataset saved to {output_file}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter conversations by token count')
    parser.add_argument('input_file', help='Path to the input ShareGPT-formatted JSON file')
    parser.add_argument('output_file', help='Path to the filtered output JSON file')
    parser.add_argument('--max_tokens', type=int, default=16384, help='Maximum allowed tokens per conversation')
    parser.add_argument('--model', default="shisa-ai/shisa-v2-mistral-nemo-12b", 
                        help='Model/tokenizer name on HuggingFace')
    
    args = parser.parse_args()
    
    filter_by_token_count(args.input_file, args.output_file, args.max_tokens, args.model)
