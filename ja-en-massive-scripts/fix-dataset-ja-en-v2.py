import json
import requests
import time
from typing import Dict, List, Any
import os
from pathlib import Path

class ShareGPTCleaner:
    def __init__(self, openrouter_api_key: str, model: str = "mistralai/mistral-small-3.2-24b-instruct", provider_preferences: dict = None):
        """
        Initialize the ShareGPT dataset cleaner.
        
        Args:
            openrouter_api_key: Your OpenRouter API key
            model: The model to use for cleaning (default: Claude 3 Sonnet)
            provider_preferences: Provider routing preferences (see OpenRouter docs)
        """
        self.api_key = openrouter_api_key
        self.model = model
        self.provider_preferences = provider_preferences or {}
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Custom system prompt for cleaning GPT responses
        self.cleaning_prompt = """You're an expert dataset cleaner. Your task is to cleanup English translations to remove any messed up formatting or corruption it has including translator notes and so on but do not change the actual translations just fix any broken words and stuff due to the way it was scraped. (For instance if the original Japanese text had ton of dots like ...... or if it had a line keep that but turn double lines into a single line then the translation should keep them, just clean up stuff that shouldn't be there in the first place) Another note is if the Japanese text had chapter number/name then the translation should have it too. You will be given a single ShareGPT formatted conversation with Japanese and English pairs, in which you will modify the English translation to fix any issues you find.
Here is the list of things to look out for:
```
tln
T/N
TN:
Note
(TL Note:
(Translation Note:
**TL Note:
messed up words use format like:
.s. (for each alphabet)
[2]
fas.h.i.+on
This&h.e.l.lip;&h.e.l.lip; is terrible&h.e.l.lip;&h.e.l.lip;
Bu*rn*ed!
(EN:
EDN:
 (+)TLN:
TLN-
Sh*t
(T/N: >> kuwanpu <>
he=\"\" is=\"\" the=\"\" head=\"\" of=\"\" the=\"\" mounted=\"\">
who=\"\" is=\"\" a=\"\" former=\"\" eberian=\"\" mercenary.=\"\" bertrand=\"\" does=\"\" various=\"\" bad=\"\" things=\"\" and=\"\" the=\"\" gangsters=\"\" of=\"\" this=\"\" neighbourhood=\"\" obey=\"\" him.\"=\"\">
***T/N:
Melgon*
 . ]
(japanese romaji inside parenthesis)
\nc.r.a.p (capitalize words in front of \n)
some sentences don't end with . or they end with ,
there's also too many spaces often or a space before \n
```
Output only the translation and nothing else."""

    def load_dataset(self, file_path: str) -> List[Dict[str, Any]]:
        """Load the ShareGPT dataset from a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both single conversation and list of conversations
            if isinstance(data, dict) and "conversations" in data:
                return [data]  # Single conversation wrapped in list
            elif isinstance(data, list):
                return data  # Already a list of conversations
            else:
                raise ValueError("Invalid dataset format")
                
        except FileNotFoundError:
            raise FileNotFoundError(f"Dataset file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

    def save_dataset(self, data: List[Dict[str, Any]], output_path: str):
        """Save the cleaned dataset to a new JSON file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Cleaned dataset saved to: {output_path}")
        except Exception as e:
            raise Exception(f"Error saving dataset: {e}")

    def format_conversation_for_api(self, conversations: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format conversations for the OpenRouter API."""
        messages = [{"role": "system", "content": self.cleaning_prompt}]
        
        # Add the conversation context
        context_parts = []
        gpt_response = ""
        
        for msg in conversations:
            if msg["from"] == "system":
                context_parts.append(f"System: {msg['value']}")
            elif msg["from"] == "human":
                context_parts.append(f"Human: {msg['value']}")
            elif msg["from"] == "gpt":
                gpt_response = msg["value"]
                context_parts.append(f"GPT Response (to be cleaned): {msg['value']}")
        
        # Combine context into user message
        user_content = "Conversation context:\n" + "\n\n".join(context_parts)
        user_content += "\n\nPlease provide the cleaned GPT response:"
        
        messages.append({"role": "user", "content": user_content})
        return messages

    def call_openrouter_api(self, messages: List[Dict[str, str]], max_retries: int = 3) -> str:
        """Make API call to OpenRouter with retry logic."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 16384
        }
        
        # Add provider preferences if specified
        if self.provider_preferences:
            payload["provider"] = self.provider_preferences
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.base_url, 
                    headers=self.headers, 
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()
                elif response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt
                    print(f"Rate limit hit. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    response.raise_for_status()
                    
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise Exception(f"API call failed after {max_retries} attempts: {e}")
                print(f"API call attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(2 ** attempt)
        
        raise Exception("Max retries exceeded")

    def process_dataset(self, input_file: str, output_file: str = None, delay: float = 1.0):
        """
        Process the entire dataset, cleaning GPT responses.
        
        Args:
            input_file: Path to input ShareGPT dataset
            output_file: Path for output file (auto-generated if None)
            delay: Delay between API calls in seconds
        """
        # Load dataset
        print(f"Loading dataset from: {input_file}")
        dataset = self.load_dataset(input_file)
        
        # Generate output filename if not provided
        if output_file is None:
            input_path = Path(input_file)
            output_file = input_path.parent / f"{input_path.stem}_cleaned{input_path.suffix}"
        
        print(f"Processing {len(dataset)} conversations...")
        
        cleaned_dataset = []
        
        for i, conversation_data in enumerate(dataset):
            try:
                print(f"Processing conversation {i + 1}/{len(dataset)}")
                
                conversations = conversation_data.get("conversations", [])
                
                # Check if there's a GPT response to clean
                has_gpt_response = any(msg["from"] == "gpt" for msg in conversations)
                
                if not has_gpt_response:
                    print(f"  No GPT response found in conversation {i + 1}, skipping...")
                    cleaned_dataset.append(conversation_data)
                    continue
                
                # Format for API
                messages = self.format_conversation_for_api(conversations)
                
                # Call API
                cleaned_response = self.call_openrouter_api(messages)
                
                # Create new conversation data with cleaned response
                new_conversations = []
                for msg in conversations:
                    if msg["from"] == "gpt":
                        new_conversations.append({
                            "from": "gpt",
                            "value": cleaned_response
                        })
                    else:
                        new_conversations.append(msg.copy())
                
                # Add to cleaned dataset
                cleaned_conversation = conversation_data.copy()
                cleaned_conversation["conversations"] = new_conversations
                cleaned_dataset.append(cleaned_conversation)
                
                print(f"  Successfully cleaned conversation {i + 1}")
                
                # Add delay between requests
                if i < len(dataset) - 1:  # Don't delay after the last request
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"  Error processing conversation {i + 1}: {e}")
                # Add original conversation to maintain dataset integrity
                cleaned_dataset.append(conversation_data)
                continue
        
        # Save cleaned dataset
        self.save_dataset(cleaned_dataset, output_file)
        print(f"Dataset cleaning complete! Processed {len(cleaned_dataset)} conversations.")

def main():
    """Example usage of the ShareGPT cleaner."""
    
    # Configuration
    API_KEY = os.getenv("OPENROUTER_API_KEY")  # Set your API key as environment variable
    INPUT_FILE = "dataset-Ja_En-Massive-v2-1000-sharegpt-16k-part-10.json"  # Path to your input dataset
    OUTPUT_FILE = "dataset-Ja_En-Massive-v2-1000-sharegpt-16k-part-10-cleaned.json"  # Output file path
    MODEL = "mistralai/mistral-small-3.2-24b-instruct"  # Model to use for cleaning
    
    # Provider preferences (optional) - see OpenRouter documentation for all options
    PROVIDER_PREFERENCES = {
        # Examples of provider routing options:
        # "order": ["anthropic", "openai"],  # Try Anthropic first, then OpenAI
        # "allow_fallbacks": True,  # Allow fallback providers
        # "require_parameters": False,  # Only use providers that support all parameters
        # "data_collection": "deny",  # Only use providers that don't collect data
        # "only": ["mistral"],  # Only use Anthropic
        # "ignore": ["deepinfra"],  # Skip DeepInfra
        # "quantizations": ["fp16", "bf16"],  # Only use these quantization levels
        "sort": "throughput",  # Sort by price (or "throughput", "latency")
        # "max_price": {"prompt": 1, "completion": 2}  # Max pricing limits
    }
    
    if not API_KEY:
        print("Please set your OpenRouter API key as the OPENROUTER_API_KEY environment variable")
        print("Or modify the script to include your API key directly")
        return
    
    try:
        # Initialize cleaner
        cleaner = ShareGPTCleaner(
            openrouter_api_key=API_KEY,
            model=MODEL,
            provider_preferences=PROVIDER_PREFERENCES
        )
        
        # Process dataset
        cleaner.process_dataset(
            input_file=INPUT_FILE,
            output_file=OUTPUT_FILE,
            delay=1.0  # 1 second delay between API calls
        )
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()