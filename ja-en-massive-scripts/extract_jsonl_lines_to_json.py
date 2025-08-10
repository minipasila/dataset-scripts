import json
import argparse
from collections import defaultdict

def extract_diverse_lines(input_file, output_file, total_lines, max_per_title=10):
    """
    Extract lines from a .jsonl file, limiting the number of entries per title.
    
    Args:
        input_file (str): Path to the input .jsonl file
        output_file (str): Path to the output .json file
        total_lines (int): Total number of lines to extract across all titles
        max_per_title (int): Maximum number of lines to extract per title
    """
    extracted_data = []
    title_counter = defaultdict(int)
    unique_titles_found = set()
    
    try:
        # First pass: count all available titles to know what we're working with
        with open(input_file, 'r', encoding='utf-8') as f:
            print("First pass: scanning available titles...")
            all_titles = set()
            for i, line in enumerate(f):
                if (i+1) % 100000 == 0:
                    print(f"Scanned {i+1} lines...")
                try:
                    json_obj = json.loads(line.strip())
                    title = json_obj.get('meta', {}).get('general', {}).get('series_title_eng', '')
                    if not title:
                        title = json_obj.get('meta', {}).get('general', {}).get('series_title_jap', 'unknown')
                    all_titles.add(title)
                except:
                    continue
            
        print(f"Found {len(all_titles)} unique titles in the dataset")
        
        # Second pass: extract data with diversity in mind
        with open(input_file, 'r', encoding='utf-8') as f:
            print(f"Second pass: extracting up to {max_per_title} lines per title, max {total_lines} total...")
            count = 0
            
            for line in f:
                if count >= total_lines:
                    break
                    
                try:
                    json_obj = json.loads(line.strip())
                    
                    # Get title from metadata
                    title = json_obj.get('meta', {}).get('general', {}).get('series_title_eng', '')
                    if not title:
                        title = json_obj.get('meta', {}).get('general', {}).get('series_title_jap', 'unknown')
                    
                    # If we haven't reached the max for this title, add it
                    if title_counter[title] < max_per_title:
                        extracted_data.append(json_obj)
                        title_counter[title] += 1
                        unique_titles_found.add(title)
                        count += 1
                        
                        if count % 100 == 0:
                            print(f"Extracted {count} lines from {len(unique_titles_found)} unique titles...")
                    
                except json.JSONDecodeError as e:
                    # Skip invalid lines
                    continue
        
        # Write the extracted data to the output file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully extracted {count} lines from {len(unique_titles_found)} unique titles to {output_file}")
        
        # Print distribution statistics
        print("\nDistribution of extracted lines by title:")
        for title, count in sorted(title_counter.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"- {title}: {count}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract diverse lines from a .jsonl file to a .json file')
    parser.add_argument('input_file', help='Path to the input .jsonl file')
    parser.add_argument('output_file', help='Path to the output .json file')
    parser.add_argument('total_lines', type=int, help='Total number of lines to extract')
    parser.add_argument('--max_per_title', type=int, default=10, 
                        help='Maximum number of lines to extract per title (default: 10)')
    
    args = parser.parse_args()
    
    extract_diverse_lines(args.input_file, args.output_file, args.total_lines, args.max_per_title)
