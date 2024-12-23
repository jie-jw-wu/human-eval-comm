import json
import csv

def convert_jsonl_to_json(jsonl_file_path, json_file_path):
    """
    Converts a JSONL file to a JSON file.
    """
    data = []
    with open(jsonl_file_path, 'r', encoding='utf-8') as jsonl_file:
        for line in jsonl_file:
            data.append(json.loads(line))
    
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Converted {jsonl_file_path} to {json_file_path} in JSON format.")

def convert_jsonl_to_csv(jsonl_file_path, csv_file_path):
    """
    Converts a JSONL file to a CSV file.
    """
    with open(jsonl_file_path, 'r', encoding='utf-8') as jsonl_file:
        data = [json.loads(line) for line in jsonl_file]

    # Extract the keys for the CSV header
    keys = set()
    for entry in data:
        keys.update(entry.keys())
    keys = sorted(keys)

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Converted {jsonl_file_path} to {csv_file_path} in CSV format.")

# Example usage:
jsonl_path = "Benchmark/HumanEvalComm_v2.jsonl"  # Replace with your JSONL file path
csv_output_path = "Benchmark/HumanEvalComm_v2.csv"  # Desired output path for JSON file

# Convert to JSON
#convert_jsonl_to_json(jsonl_path, json_output_path)

# Convert to CSV
convert_jsonl_to_csv(jsonl_path, csv_output_path)
