import json
from tqdm import tqdm
import copy
import openai
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import time

prompt_path = "../prompts/humaneval_prompt_update.txt"
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
    text = f"""
{construct_few_shot_prompt}

**Input Code Snippet**:
```python
{prompt}
```
## Completion 3:
"""
    completions_code = []
    for _ in range(times):
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
            if completion:
                break
        completions_code.append(completion)

    data_entry["completion_list"] = completions_code
    return data_entry

def programmer_main(model, language, dataset, api_key):
    openai.api_key = api_key  # Set the API key here

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_entry = {
            executor.submit(fetch_completion, copy.deepcopy(entry), model): entry
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
    
    with open(f"./dataset/{model}_{language}.json", "w") as f:
        json.dump(dataset, f, indent=4)
    
    return dataset

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--api_key", type=str, required=True, help="OpenAI API key")
#     parser.add_argument("--model", type=str, required=True, help="Model to use for completion")
#     parser.add_argument("--language", type=str, default="python", help="Programming language")
    
#     args = parser.parse_args()

#     model_list = [args.model]
#     language = [args.language]
    
#     for model in model_list:
#         for lg in language:
#             updated_dataset = programmer_main(model, lg, dataset, args.api_key)


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