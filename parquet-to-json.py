import pyarrow.parquet as pq
import json
from json import JSONEncoder
import numpy as np

# Define a custom JSON encoder to handle non-ASCII characters and ndarray
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8')  # Decode bytes to string
        elif isinstance(obj, np.ndarray):
            return obj.tolist()  # Convert ndarray to list
        return JSONEncoder.default(self, obj)

# Load the Parquet dataset
parquet_file = 'dataset-name.parquet'
table = pq.read_table(parquet_file)

# Convert the Parquet table to a Pandas DataFrame
df = table.to_pandas()

# Convert the DataFrame to JSON using custom encoder
json_data = json.dumps(df.to_dict(orient='records'), ensure_ascii=False, cls=CustomJSONEncoder)

# Save JSON data to a file
json_file = 'dataset-output.json'
with open(json_file, 'w', encoding='utf-8') as f:
    f.write(json_data)

print("Conversion completed. JSON file saved as:", json_file)
