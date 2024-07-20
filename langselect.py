# This script will detect your selected language form a dataset and then output a new file with just data from that language.
import json
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Ensure consistent results from langdetect
DetectorFactory.seed = 0

def is_finnish(text):
    try:
        return detect(text) == 'fi' # Here you can select your language.
    except LangDetectException:
        return False

def filter_finnish_entries(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    finnish_entries = [entry for entry in data if is_finnish(entry.get("Text", ""))]
    
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(finnish_entries, file, ensure_ascii=False, indent=4)

# Replace 'input.json' and 'output.json' with your actual file names
input_file = 'input.json'
output_file = 'output.json'
filter_finnish_entries(input_file, output_file)
