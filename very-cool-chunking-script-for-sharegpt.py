from transformers import PreTrainedTokenizerFast
import json

# Load the JSON file
with open("jsonfile-name.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Initialize tokenizer
tokenizer = PreTrainedTokenizerFast.from_pretrained("organization/modelname")

# Function to calculate token length
def token_len(text):
    return len(tokenizer.encode(text))

# Function to split conversations based on a maximum token count
def split_conversation(raw_conversations, max_length):
    system_message = next((msg for msg in raw_conversations if msg["from"] == "system"), None)
    system_tokens = token_len(system_message["value"]) if system_message else 0

    chunks = []
    current_chunk = []
    current_length = system_tokens if system_message else 0

    for msg in raw_conversations:
        msg_token_length = token_len(msg["value"])
        
        if msg["from"] != "system" and current_length + msg_token_length > max_length:
            if system_message:
                chunks.append([system_message] + current_chunk)
            else:
                chunks.append(current_chunk)
            current_chunk = []
            current_length = system_tokens if system_message else 0
        
        if msg["from"] != "system":
            current_chunk.append(msg)
            current_length += msg_token_length

    if current_chunk:
        if system_message:
            chunks.append([system_message] + current_chunk)
        else:
            chunks.append(current_chunk)

    return chunks

# Process each conversation and collect updated data
updated_data = []
for item in data:
    conversation_id = item["id"]
    conversations = item["conversations"]
    split_conversations = split_conversation(conversations, 8192) # You can put any number of tokens you want here.
    
    for idx, convo in enumerate(split_conversations):
        updated_data.append({"id": f"{conversation_id}_{idx}", "conversations": convo})

# Save the modified conversations to a new JSON file
with open("chunked-output.json", "w", encoding="utf-8") as file:
    json.dump(updated_data, file, indent=2)
