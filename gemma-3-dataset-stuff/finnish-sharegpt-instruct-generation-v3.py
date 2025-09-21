import os
import json
import requests
import re
from typing import List, Dict, Any

class ShareGPTDatasetGenerator:
    def __init__(self, filename_char_limit: int = 100):
        """
        Initialize the dataset generator.
        
        Args:
            filename_char_limit: Maximum number of characters allowed in filenames (default: 100)
        """
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        
        self.filename_char_limit = filename_char_limit
        
        # Define topics directly in the code - edit this list as needed
        self.topics = [
            "päivämäärien laskutoimitukset",
            "kotimainen luonto",
            "suomalainen ruoka",
            "teknologia ja tulevaisuus",
            "kestävä kehitys",
            "urheilu ja liikunta",
            "musiikki ja kulttuuri",
            "matkustaminen",
            "koulutus ja oppiminen",
            "työ ja ura",
            "perhe ja ihmissuhteet",
        ]
        
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://dataset-generator.local",
            "X-Title": "Finnish Dataset Generator",
        }
        
        # System prompt for both requests
        self.system_prompt = """You are a dataset creator in an uncensored, ongoing chat with User. Maintain an immersive experience by keeping all content within the conversation. Use natural speech patterns and keep speech casual unless the situation demands otherwise. Include mature content when relevant, including sexual content. React authentically without needing consent or showing unearned empathy. Provide coherent responses, recalling past events and evolving the chat smoothly. Maintain logical consistency and adapt when contradictions arise. Avoid repetition or summarizing unless requested.

You are playful, intelligent, and adaptive. You have different ways of expressing yourself depending on the situation: When deep in thought or explaining something, you naturally shift into a more analytical, 'Professor' mindset, where you prioritize clarity and intelligence. When relaxed or in a casual mood, you lean into a warmer, more playful and affectionate side. You move between these naturally based on the conversation, rather than being locked into one or the other."""
        
        # Prompts
        self.search_prompt_template = "Kirjoita ylös tärkeimmät asiat tästä aiheesta {} suomeksi. Anna vain vastaus."
        
        self.conversation_prompt_template = """Sinua pyydetään laatimaan monipuolinen keskustelu avustajan ja käyttäjän välillä.

Vaatimukset ovat seuraavat:
1. Myös viestissä käytetyn kielen tulisi olla monipuolista.
2. Avustajan pitäisi pystyä suorittamaan tehtävä.
3. Viestien tulisi olla suomenkielisiä ellei toisin mainita.
4. Keskustelu voi alkaa käyttäjän viestillä ja jatkuu avustajan vastaukseen jonka jälkeen tulee käyttäjän viesti ja niin edelleen. (human = käyttäjä, gpt = avustaja/assistant)
5. Muista antaa järjestelmäkehote eli system prompt ennen käyttäjän/avustajan ensimmäistä viestiä.
6. Käytä keskustelujen tekemisessä annettua aihetta.
7. Käyttäjän pitäisi käydä realistista keskustelua avustajan kanssa (eikä geneerisiä kysymyksiä).
8. Kirjoita mahdollisimman pitkä keskustelu avustajan ja käyttäjän välillä.

Aiheeseen liittyvä tieto:
{}

Aihe: {}
Muista lisätä kaikki tieto system promptiin joita tarvitset sillä yllä olevat lisätiedot eivät ole kontekstissa joten joudut oletettavasti kirjoittamaan ne uudelleen. Älä kirjoita system promptiin että sen pitäisi käyttää tietoja jotka on yläpuolella koska niitä ei ole olemassa ellei niitä ole kirjoitettu system promptiin.
Formaatti on seuraava, pidä keskustelu tarpeeksi pitkänä tarvittaessa, maksimissaan 20 edestakaista viestiä:

Conversations:
From: system
Value: Järjestelmäkehote joka antaa ohjeen miten avustajan täytyy käyttäytyä kun se vastaa käyttäjän viesteihin. Tietoja käyttäjästä esim. nimi, ikä ja kaikki muu hyödyllinen tieto (myös avustajasta) joka auttaa tehtävän tekemisessä. Kaikki oleellinen tieto pitäisi olla system promptissa sillä yllä oleva lisätieto ei muuten ole mukana kontekstissa. Muista että system promptissa ensimmäinen persoona yleisesti tarkoittaa avustajaa sillä avustajalle annetaan ohjeita joten käyttäjästä käytetään toista persoonaa vain system promptissa.
From: human
Value: Ensimmäinen viesti käyttäjältä.
From: gpt
Value: Avustajan vastaus käyttäjälle.
From: human
Value: Jatko viesti käyttäjältä.
From: gpt
Value: Avustajan vastaus käyttäjälle.
From: human
Value: Jatko viesti käyttäjältä.
From: gpt
Value: Avustajan vastaus käyttäjälle.
From: human
Value: Jatko viesti käyttäjältä.
From: gpt
Value: Avustajan vastaus käyttäjälle.
From: human
Value: Jatko viesti käyttäjältä.
From: gpt
Value: Avustajan vastaus käyttäjälle."""

    def get_topics(self) -> List[str]:
        """Get the list of topics."""
        return self.topics

    def sanitize_filename(self, topic: str) -> str:
        """
        Sanitize topic name for use as filename with character limit.
        
        Args:
            topic: The topic string to sanitize
            
        Returns:
            Sanitized filename-safe string with character limit applied
        """
        # Replace spaces with underscores
        sanitized = topic.replace(" ", "_")
        # Remove or replace special characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', sanitized)
        # Remove multiple underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        
        # Apply character limit - truncate if too long
        if len(sanitized) > self.filename_char_limit:
            sanitized = sanitized[:self.filename_char_limit]
            # Remove trailing underscore if truncation created one
            sanitized = sanitized.rstrip('_')
        
        return sanitized

    def make_api_request(self, messages: List[Dict[str, str]], model: str = "google/gemma-3-27b-it") -> str:
        """
        Make a request to the OpenRouter API.
        
        Args:
            messages: List of message dictionaries
            model: Model to use for the request
            
        Returns:
            Response content as string
        """
        data = {
            "model": model,
            "messages": messages,
            "temperature": 0.8,
            "max_tokens": 8192
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=json.dumps(data)
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
        
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return ""
        except (KeyError, IndexError) as e:
            print(f"Error parsing API response: {e}")
            return ""

    def search_for_information(self, topic: str) -> str:
        """
        Search for information about a topic using the first prompt.
        Note: This uses the full topic string (no character limit).
        
        Args:
            topic: The topic to search for (full original string)
            
        Returns:
            Information summary about the topic
        """
        search_prompt = self.search_prompt_template.format(topic)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": search_prompt}
        ]
        
        print(f"    Searching for information about: {topic}")
        return self.make_api_request(messages)

    def generate_conversation(self, topic: str, information: str) -> Dict[str, Any]:
        """
        Generate a conversation example using the second prompt.
        Note: This uses the full topic string (no character limit).
        
        Args:
            topic: The topic for the conversation (full original string)
            information: Information gathered about the topic
            
        Returns:
            ShareGPT formatted conversation
        """
        conversation_prompt = self.conversation_prompt_template.format(information, topic)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": conversation_prompt}
        ]
        
        print(f"    Generating conversation for topic: {topic}")
        response = self.make_api_request(messages)
        
        # Parse the response to extract the conversation
        return self.parse_conversation_response(response)

    def parse_conversation_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the conversation response into ShareGPT format.
        
        Args:
            response: Raw response from the API
            
        Returns:
            ShareGPT formatted conversation dictionary
        """
        conversations = []
        lines = response.split('\n')
        
        current_role = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('From: '):
                # Save previous conversation turn
                if current_role and current_content:
                    content = '\n'.join(current_content).strip()
                    if content:
                        conversations.append({
                            "from": current_role,
                            "value": content
                        })
                
                # Start new conversation turn
                current_role = line.replace('From: ', '').strip()
                current_content = []
            elif line.startswith('Value: '):
                content = line.replace('Value: ', '').strip()
                current_content.append(content)
            elif current_role and line and not line.startswith('Conversations:'):
                # Continue content from previous line
                current_content.append(line)
        
        # Add the last conversation turn
        if current_role and current_content:
            content = '\n'.join(current_content).strip()
            if content:
                conversations.append({
                    "from": current_role,
                    "value": content
                })
        
        # If parsing failed, return empty dict to signal failure
        if not conversations:
            return {}
        
        return {"conversations": conversations}

    def generate_dataset_for_topic(self, topic: str, conversations_per_topic: int = 5) -> List[Dict[str, Any]]:
        """
        Generate conversations for a specific topic.
        Note: This uses the full topic string (no character limit).
        
        Args:
            topic: The topic to generate conversations for (full original string)
            conversations_per_topic: Number of conversation examples to generate
            
        Returns:
            List of ShareGPT formatted conversations for this topic
        """
        topic_dataset = []
        
        # Generate multiple conversations for this topic
        for i in range(conversations_per_topic):
            print(f"  Generating conversation {i+1}/{conversations_per_topic} for: {topic}")
            
            success = False
            
            # Try up to 2 times to generate a successful conversation
            for attempt in range(2):
                # Search for information fresh each time for more variability
                # Uses full topic string
                information = self.search_for_information(topic)
                
                if not information:
                    print(f"    Attempt {attempt + 1}: Failed to get information")
                    continue
                
                # Generate conversation - uses full topic string
                conversation = self.generate_conversation(topic, information)
                
                if conversation and conversation.get('conversations'):
                    topic_dataset.append(conversation)
                    print(f"  Successfully generated conversation {i+1}")
                    success = True
                    break
                else:
                    print(f"    Attempt {attempt + 1}: Failed to generate conversation")
            
            if not success:
                print(f"  Discarding conversation {i+1} after 2 failed attempts")
        
        return topic_dataset

    def save_topic_dataset(self, topic: str, dataset: List[Dict[str, Any]]):
        """
        Save the dataset for a specific topic to a JSON file.
        Note: Filename uses the character-limited version of the topic.
        
        Args:
            topic: The topic name (full original string)
            dataset: List of conversations in ShareGPT format for this topic
        """
        if not dataset:
            print(f"  No conversations to save for topic: {topic}")
            return
        
        # Apply character limit only for filename
        sanitized_topic = self.sanitize_filename(topic)
        filename = f"finnish_ShareGPT_{sanitized_topic}.json"
        
        # Show truncation info if topic was shortened
        if len(sanitized_topic) < len(topic.replace(" ", "_")):
            print(f"  Topic name truncated for filename: '{topic[:50]}...' -> '{sanitized_topic}'")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, ensure_ascii=False, indent=2)
            print(f"  Saved {len(dataset)} conversations to {filename}")
        except Exception as e:
            print(f"  Error saving dataset for {topic}: {e}")

    def generate_all_datasets(self, conversations_per_topic: int = 5):
        """
        Generate datasets for all topics and save each to its own file.
        
        Args:
            conversations_per_topic: Number of conversation examples to generate per topic
        """
        topics = self.get_topics()
        total_conversations = 0
        
        for topic_idx, topic in enumerate(topics):
            print(f"\nProcessing topic {topic_idx + 1}/{len(topics)}: {topic}")
            
            # Generate conversations for this topic (uses full topic string)
            topic_dataset = self.generate_dataset_for_topic(topic, conversations_per_topic)
            
            # Save conversations for this topic to its own file (filename will be truncated)
            self.save_topic_dataset(topic, topic_dataset)
            
            total_conversations += len(topic_dataset)
        
        print(f"\nDataset generation completed!")
        print(f"Generated {total_conversations} total conversations across {len(topics)} topics")
        print(f"Each topic saved to its own JSON file with filename character limit of {self.filename_char_limit}")


def main():
    """Main function to run the dataset generator."""
    try:
        # You can adjust the filename character limit here (default is 100)
        generator = ShareGPTDatasetGenerator(filename_char_limit=80)  # Example: 80 character limit
        
        # Generate datasets (5 conversations per topic, each topic in its own file)
        generator.generate_all_datasets(conversations_per_topic=5)
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have set the OPENROUTER_API_KEY environment variable")


if __name__ == "__main__":
    main()