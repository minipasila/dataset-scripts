import json
import argparse
import numpy as np
from transformers import AutoTokenizer
from tqdm import tqdm

def count_tokens(input_file, model_name="shisa-ai/shisa-v2-mistral-nemo-12b", verbose=False):
    """
    Counts tokens for each conversation in a ShareGPT-formatted dataset.
    
    Args:
        input_file (str): Path to the ShareGPT-formatted JSON file
        model_name (str): Name of the model/tokenizer from HuggingFace
        verbose (bool): Whether to print detailed info for each conversation
    """
    try:
        # Load the tokenizer
        print(f"Loading tokenizer for {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Load the dataset
        print(f"Loading dataset from {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Prepare to count tokens
        token_counts = []
        system_token_counts = []
        human_token_counts = []
        assistant_token_counts = []
        
        print(f"Counting tokens for {len(data)} conversations...")
        
        # Process each conversation
        for i, conversation_item in enumerate(tqdm(data)):
            conversations = conversation_item.get("conversations", [])
            
            total_count = 0
            system_count = 0
            human_count = 0
            assistant_count = 0
            
            # Count tokens for each message in the conversation
            for message in conversations:
                role = message.get("from", "")
                content = message.get("value", "")
                
                # Count tokens for this message
                tokens = tokenizer.encode(content)
                token_count = len(tokens)
                total_count += token_count
                
                # Track by role
                if role == "system":
                    system_count += token_count
                elif role == "human":
                    human_count += token_count
                elif role == "gpt" or role == "assistant":
                    assistant_count += token_count
            
            # Store the counts
            token_counts.append(total_count)
            system_token_counts.append(system_count)
            human_token_counts.append(human_count)
            assistant_token_counts.append(assistant_count)
            
            # Print detailed info if verbose
            if verbose:
                print(f"Conversation {i+1}:")
                print(f"  System tokens: {system_count}")
                print(f"  Human tokens: {human_count}")
                print(f"  Assistant tokens: {assistant_count}")
                print(f"  Total tokens: {total_count}")
                print()
        
        # Calculate statistics
        total_tokens = sum(token_counts)
        avg_tokens = np.mean(token_counts)
        median_tokens = np.median(token_counts)
        max_tokens = np.max(token_counts)
        min_tokens = np.min(token_counts)
        
        # Print overall statistics
        print("\nToken Count Statistics:")
        print(f"Total conversations: {len(data)}")
        print(f"Total tokens: {total_tokens}")
        print(f"Average tokens per conversation: {avg_tokens:.2f}")
        print(f"Median tokens per conversation: {median_tokens}")
        print(f"Maximum tokens in a conversation: {max_tokens}")
        print(f"Minimum tokens in a conversation: {min_tokens}")
        
        # Role-based statistics
        print("\nToken Distribution by Role:")
        print(f"System messages: {sum(system_token_counts)} tokens ({sum(system_token_counts)/total_tokens*100:.2f}%)")
        print(f"Human messages: {sum(human_token_counts)} tokens ({sum(human_token_counts)/total_tokens*100:.2f}%)")
        print(f"Assistant messages: {sum(assistant_token_counts)} tokens ({sum(assistant_token_counts)/total_tokens*100:.2f}%)")
        
        # Token histogram
        ranges = [0, 512, 1024, 2048, 4096, 8192, 16384, float('inf')]
        range_names = ["0-512", "513-1024", "1025-2048", "2049-4096", "4097-8192", "8193-16384", "16385+"]
        histogram = [0] * (len(ranges) - 1)
        
        for count in token_counts:
            for i in range(len(ranges) - 1):
                if ranges[i] <= count < ranges[i+1]:
                    histogram[i] += 1
                    break
        
        print("\nToken Count Distribution:")
        for i, count in enumerate(histogram):
            print(f"{range_names[i]}: {count} conversations ({count/len(data)*100:.2f}%)")
        
        return token_counts
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Count tokens in a ShareGPT dataset')
    parser.add_argument('input_file', help='Path to the ShareGPT-formatted JSON file')
    parser.add_argument('--model', default="shisa-ai/shisa-v2-mistral-nemo-12b", 
                        help='Model/tokenizer name on HuggingFace')
    parser.add_argument('--verbose', action='store_true', help='Print detailed info for each conversation')
    
    args = parser.parse_args()
    
    count_tokens(args.input_file, args.model, args.verbose)
