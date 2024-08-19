import argparse
import os
import json
from tqdm import tqdm
import copy
import openai
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import time

# Remove dataset loading since we'll be using external data passed as a parameter.

def preprocess_data(completion_string):
    if f"```python" in completion_string:
        completion_string = completion_string[completion_string.find(f"```python")+len(f"```python"):]
        completion_string = completion_string[:completion_string.find("```")]
    else:
        print("Error: No code block found")
    return completion_string

# Function to fetch completion
def fetch_completion(data_entry, model, lg, times=5, api_key=None):
    global construct_few_shot_prompt
    if "need_reproduce" in data_entry.keys() and data_entry["need_reproduce"] == False:
        return data_entry
    
    openai.api_key = api_key  # Set the API key here

    prompt = data_entry["prompt"]
    text = f"""
{construct_few_shot_prompt}

**Input Code Snippet**:
```python
{prompt}
```
## Completion 3:
"""
    completions_code = []
    for i in range(times):
        while True:
            try:
                completions = openai.ChatCompletion.create(
                    model=model,
                    stream=False,
                    messages=[
                        {"role": "system", "content": "You are a software programmer."},
                        {"role": "user", "content": text},
                    ],
                    request_timeout=100,
                )
                completion = completions.choices[0]["message"]["content"]
                completion = preprocess_data(completion)

            except Exception as e:
                print(e)
                time.sleep(10)
                completion = ""
            if completion != "":
                break
        completions_code.append(completion)
    data_entry["completion_list"] = completions_code
    return data_entry

def call_fetch_completion_helper(dataset, model,lg):
    print("Fixing bug...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_entry = {executor.submit(fetch_completion, copy.deepcopy(entry), model, lg): entry for entry in tqdm(dataset)}
        for future in tqdm(concurrent.futures.as_completed(future_to_entry)):
            entry = future_to_entry[future]
            try:
                updated_entry = future.result()
                idx = dataset.index(entry)
                dataset[idx] = updated_entry
            except Exception as e:
                print(repr(e))
    return dataset

def main(model, lg, msgs, api_key):
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_entry = {
            executor.submit(fetch_completion, copy.deepcopy(entry), model, lg, api_key=api_key): entry for entry in tqdm(msgs)
        }
        results = []
        for future in tqdm(concurrent.futures.as_completed(future_to_entry)):
            entry = future_to_entry[future]
            try:
                updated_entry = future.result()
                results.append(updated_entry)
            except Exception as e:
                print(repr(e))
    return results

# This block only runs when the script is executed directly.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run completions")
    parser.add_argument("--model", type=str, required=True, help="Model name")
    parser.add_argument("--lg", type=str, required=True, help="Programming language")
    parser.add_argument("--api_key", type=str, required=True, help="OpenAI API Key")
    parser.add_argument("--msgs", type=str, required=True, help="Path to JSON file with messages")
    args = parser.parse_args()

    with open(args.msgs, 'r') as f:
        msgs = json.load(f)

    results = main(args.model, args.lg, msgs, args.api_key)
    
    output_path = f"./dataset/{args.model}_{args.lg}.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)