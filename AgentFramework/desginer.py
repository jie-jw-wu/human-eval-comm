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

def preprocess_data(test_case_string):
    if f"```python" in test_case_string:
        test_case_string = test_case_string[test_case_string.find(f"```python")+len(f"```python"):]
        test_case_string = test_case_string[:test_case_string.find("```")]

    return test_case_string

# Function to fetch completion
def fetch_completion(data_entry, model, lg, times=10, api_key=None):
    global construct_few_shot_prompt

    openai.api_key = api_key  # Set the API key here

    if "need_reproduce" in data_entry.keys() and data_entry["need_reproduce"] == False:
        return data_entry

    prompt = data_entry["prompt"]
    entry_point = data_entry.get("entry_point", "")  # Add entry_point check if needed
    
    text = f"""
{construct_few_shot_prompt}

**Input Code Snippet**:
```python
```
{prompt}
"""
    test_case_list = []
    for i in range(times):
        while True:
            try:
                completions = openai.ChatCompletion.create(
                    model=model,
                    stream=False,
                    messages=[
                        {"role": "system", "content": "You are a code developer assistant."},
                        {"role": "user", "content": text},
                    ],
                    request_timeout=100,
                )
                test_case = completions.choices[0]["message"]["content"]
                test_case = preprocess_data(test_case)
            except Exception as e:
                time.sleep(20)
                print(e)
                test_case = ""
            if test_case != "":
                break
        test_case_list.append(test_case)
    data_entry["test_case_list"] = test_case_list
    return data_entry

def call_fetch_test_completion_helper(dataset, model,lg):
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
    parser = argparse.ArgumentParser(description="Run test case generation")
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