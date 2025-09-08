# This file contains code copied and modified from the following repository:
# Repository: https://github.com/huangd1999/AgentCoder/tree/main
# Original Author: Dong Huang, Jie M.Zhang, Michael Luck, Qingwen Bu, Yuhao Qing, Heming Cui
# License: MIT
import json
from tqdm import tqdm
import copy
import openai
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import google.generativeai as genai
import os
import time

prompt_path = "./prompts/test_designer_humaneval_prompt_update.txt"
with open(prompt_path, "r") as f:
    construct_few_shot_prompt = f.read()

def preprocess_data(test_case_string):
    if "```python" in test_case_string:
        test_case_string = test_case_string[test_case_string.find("```python") + len("```python"):]
        test_case_string = test_case_string[:test_case_string.find("```")]
    return test_case_string

# Function to fetch completion
def fetch_completion(data_entry, model, times=10):
    global construct_few_shot_prompt
    if "need_reproduce" in data_entry.keys() and not data_entry["need_reproduce"]:
        return data_entry
    
    prompt = data_entry["prompt"]
    entry_point = data_entry["entry_point"]
    text = f"""
{construct_few_shot_prompt}

**Input Code Snippet**:
```python
{prompt}
```
"""
    test_case_list = []

    # Use Gemini if GEMINI_API_KEY is available, otherwise fallback to OpenAI
    use_gemini = os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY") != ""

    if use_gemini:
        # Configure Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        gemini_model = genai.GenerativeModel(os.getenv('EVALUATOR_MODEL'))

        for _ in range(times):
            while True:
                try:
                    full_prompt = f"You are a code developer assistant.\n\n{text}"
                    response = gemini_model.generate_content(full_prompt)
                    test_case = response.text
                    test_case = preprocess_data(test_case)
                except Exception as e:
                    print(f"Gemini error: {e}")
                    time.sleep(20)
                    test_case = ""
                if test_case:
                    break
            test_case_list.append(test_case)
    else:
        # Fallback to OpenAI (original code)
        for _ in range(times):
            while True:
                try:
                    client = openai.OpenAI()
                    completions = client.chat.completions.create(
                        model=model,
                        stream=False,
                        messages=[
                            {"role": "system", "content": "You are a code developer assistant."},
                            {"role": "user", "content": text},
                        ],
                        request_timeout=100,
                    )
                    test_case = completions.choices[0].message.content
                    test_case = preprocess_data(test_case)
                except Exception as e:
                    time.sleep(20)
                    print(e)
                    test_case = ""
                if test_case:
                    break
            test_case_list.append(test_case)
    
    data_entry["test_case_list"] = test_case_list
    return data_entry

def designer_main(model, language, new_dataset, api_key, task_id):
    openai.api_key = api_key
    
    with ThreadPoolExecutor(max_workers=1) as executor:
        future_to_entry = {
            executor.submit(fetch_completion, copy.deepcopy(entry), "gpt-3.5-turbo-1106"): entry
            for entry in tqdm(new_dataset)
        }
        for future in tqdm(concurrent.futures.as_completed(future_to_entry)):
            entry = future_to_entry[future]
            try:
                updated_entry = future.result()
                idx = new_dataset.index(entry)
                new_dataset[idx] = updated_entry
            except Exception as e:
                print(repr(e))
    # Then open the file and write the JSON data
    with open(f"./dataset/{model}_{language}_{task_id}.json", "w") as f:
        json.dump(new_dataset, f, indent=4)
    
    return new_dataset

def call_fetch_test_completion_helper(dataset, model,lg):
    print("Fixing bug...")
    with ThreadPoolExecutor(max_workers=1) as executor:
        future_to_entry = {
            executor.submit(fetch_completion, copy.deepcopy(entry), "gpt-3.5-turbo-1106"): entry
            for entry in tqdm(dataset)
        }
        for future in tqdm(concurrent.futures.as_completed(future_to_entry)):
            entry = future_to_entry[future]
            try:
                updated_entry = future.result()
                idx = dataset.index(entry)
                dataset[idx] = updated_entry
            except Exception as e:
                print(repr(e))
    return dataset
