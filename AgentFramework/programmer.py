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
import time
import time
import os

print("Current Working Directory:", os.getcwd())

prompt_path = "./prompts/humaneval_prompt_update.txt"
with open(prompt_path, "r") as f:
    construct_few_shot_prompt = f.read()

def preprocess_data(completion_string):
    if "```python" in completion_string:
        completion_string = completion_string[completion_string.find("```python") + len("```python"):]
        completion_string = completion_string[:completion_string.find("```")]
    else:
        print("Error: No code block found")
    return completion_string

def fetch_completion(data_entry, model, times=5):
    global construct_few_shot_prompt
    if "need_reproduce" in data_entry.keys() and not data_entry["need_reproduce"]:
        return data_entry

    prompt = data_entry["prompt"]
    # clarity will only be added to the prompt if the question is modified
    clarity = "" if "clarity_prompt" not in data_entry else data_entry["clarity_prompt"]
    text = f"""
{construct_few_shot_prompt}
{clarity}
**Input Code Snippet**:
```python
{prompt}
```
## Completion 3:
"""
    completions_code = []

    # Use Gemini if GEMINI_API_KEY is available, otherwise fallback to OpenAI
    use_gemini = os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY") != ""

    if use_gemini:
        # Configure Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        gemini_model = genai.GenerativeModel(os.getenv('EVALUATOR_MODEL'))

        for _ in range(times):
            while True:
                try:
                    full_prompt = f"You are a software programmer.\n\n{text}"
                    response = gemini_model.generate_content(full_prompt)
                    completion = response.text
                    completion = preprocess_data(completion)
                except Exception as e:
                    print(f"Gemini error: {e}")
                    time.sleep(10)
                    completion = ""
                if completion:
                    break
            completions_code.append(completion)
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
                            {"role": "system", "content": "You are a software programmer."},
                            {"role": "user", "content": text},
                        ],
                        request_timeout=100,
                    )
                    completion = completions.choices[0].message.content
                    completion = preprocess_data(completion)
                except Exception as e:
                    print(e)
                    time.sleep(10)
                    completion = ""
                if completion:
                    break
            completions_code.append(completion)

    data_entry["completion_list"] = completions_code
    # print("Completion List is created?")
    # print(data_entry["completion_list"])
    return data_entry

def programmer_main(model, language, new_dataset, api_key, task_id):
    openai.api_key = api_key  # Set the API key here

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
    
    # create folder if it does't already exist
    os.makedirs(f"./dataset", exist_ok=True)
    
    # Then open the file and write the JSON data
    with open(f"./dataset/{model}_{language}_{task_id}.json", "w") as f:
        json.dump(new_dataset, f, indent=4)
    
    return new_dataset

def call_fetch_completion_helper(dataset, model,lg):
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