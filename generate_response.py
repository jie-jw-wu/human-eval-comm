import math
import time

import nltk
import openai
import re
import os
import json
import subprocess
import argparse
import random
import string
from nltk.corpus import stopwords

openai.api_key = os.environ['OPENAI_KEY']
MAX_NUM_PROBLEMS = 1 # limit the number of problems to be run and call ChatGPT. -1 means no such limit
PROMPT_START_0 = 'Generate Python3 code (Markdown):\n'
PROMPT_START_1 = 'Generate either Python3 code only (Markdown) or no code:\n'
PROMPT_START_2 = 'Generate either Python3 code only (Markdown) or ask questions:\n'
PROMPT_START_3 = 'You are an expert software developer. Generate Python3 code (code must has Markdown in response) in below information. Alternatively, you can ask clarifying questions: \n'
PROMPT_START_3_v2 = 'You are an expert software developer who writes high quality code. With below information, please either generate Python3 code (Respond directly with code only with markdown), or ask clarifying questions: \n'

def create_prompt(description, option='original', percentage=0):
    if option == 'original':
        prompt = PROMPT_START_3
        return prompt + description
    elif option.startswith('randRemove'):
        return PROMPT_START_3 + split_and_remove_chunk(description, percentage)
    elif option.startswith('manualRemove'): # TODO(jwu): WIP
        return PROMPT_START_3_v2 + description
    else:
        return PROMPT_START_3 + split_and_replace_with_random_words(description, percentage)


# A larger vocabulary of common English words
common_words = [
    "apple", "banana", "chocolate", "dog", "elephant", "flower", "guitar",
    "happiness", "internet", "jazz", "kangaroo", "laughter", "mountain", "ocean",
    "penguin", "question", "rainbow", "sunshine", "umbrella", "victory", "wonderful",
    "xylophone", "zebra", "car", "house", "book", "computer", "chair", "table",
    "phone", "shoes", "music", "friend", "beach", "movie", "cake", "coffee",
    "game", "travel", "nature", "art", "garden", "party", "smile", "love", "star",
    "moon", "bird", "child", "family", "money", "dream", "time", "water", "fire",
    "food", "work", "school", "world", "health", "peace", "joy", "knowledge", "color",
    "forest", "planet", "song", "heart", "adventure", "freedom", "success", "history"
]

# Function to generate a random word from the larger vocabulary
def generate_random_common_word():
    return random.choice(common_words)

def split_and_replace_with_random_words(text, percentage):
    # Split the input string into words
    words = text.split()

    # Calculate the length of the input text
    num_words = len(words)

    # Calculate the number of words to replace (approximately one-third)
    num_words_to_replace = calculate_percentage_integer(num_words, percentage)

    if num_words_to_replace == 0:
        return text  # If there are too few words to replace, return the original text

    # Choose a random starting index for the chunk to replace
    start_index = random.randint(0, num_words - num_words_to_replace)

    # Determine the end index of the chunk
    end_index = start_index + num_words_to_replace

    # Generate random common words to replace the chunk
    random_common_words = [generate_random_common_word() for _ in range(num_words_to_replace)]

    # Create a list to store the modified words
    modified_words = words[:start_index] + random_common_words + words[end_index:]

    # Join the modified words to create the modified text
    modified_text = ' '.join(modified_words)

    return modified_text

def split_and_remove_chunk(text, percentage):
    # Split the input string into words
    words = text.split()

    # Calculate the length of the input text
    num_words = len(words)

    # Calculate the number of words to remove (approximately one-third)
    num_words_to_remove = calculate_percentage_integer(num_words, percentage)

    if num_words_to_remove == 0:
        return text  # If there are too few words to remove, return the original text

    # Choose a random starting index for the chunk to remove
    start_index = random.randint(0, num_words - num_words_to_remove)

    # Determine the end index of the chunk
    end_index = start_index + num_words_to_remove

    # Create a list to store the words to keep
    words_to_keep = []

    # Iterate through the words and add them to the list if they are outside the chunk
    for index, word in enumerate(words):
        if index < start_index or index >= end_index:
            words_to_keep.append(word)

    # Join the words to create the modified text
    modified_text = ' '.join(words_to_keep)

    return modified_text

def calculate_percentage_integer(value, percentage):
    # Calculate the result as a floating-point number
    result = value * (percentage / 100.0)
    
    # Round the result to the nearest integer
    rounded_result = round(result)
    
    return rounded_result

def description_2_code(prompt, model, topn, temperature):
    if model=='comm':
        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            n=1,
            temperature=temperature,
            messages=[{"role": "user",
                       "content": prompt},
                      ]
        )
        first_response_list = []
        for i in completion['choices']:
            first_response_list.append(i['message']['content'])

        new_prompt = "You are an expert in software engineering. You will be given the problem description and current code of a coding task. You will decide whether to ask clarifying questions or return the code with markup. \n ### Problem Description: \n"+ prompt + "\n ### Generated Code From Previous Iteration:\n" + first_response_list[0]
        
        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            n=topn,
            temperature=temperature,
            messages=[{"role": "user",
                       "content": new_prompt},
                      ]
        )
        response_list = []
        # code_list = []
        for i in completion['choices']:
            response_list.append(i['message']['content'])

        return response_list
    else:
        completion = openai.ChatCompletion.create(
            model=model,
            n=topn,
            temperature=temperature,
            messages=[{"role": "user",
                       "content": prompt},
                      ]
        )
        response_list = []
        # code_list = []
        for i in completion['choices']:
            response_list.append(i['message']['content'])
        # code_template = re.compile('```.*\n([\s\S]+?)\n```', re.M)
        # for response in response_list:
        #     code = code_template.findall(response)
        #     if len(code) > 0:
        #         code_list.append(code[-1])
        #     else:
        #         code_list.append('')
        # return code_list, response_list
        return response_list

def get_ith_element(input_string, i):
    # Split the input string by '_' to create a list of elements
    elements = input_string.split('_')

    # Check if i is a valid index within the range of elements
    if 0 <= i < len(elements):
        return elements[i]
    else:
        return ""  # Return "" if i is out of range

def string_to_int(input_string):
    try:
        result = int(input_string)
        return result
    except ValueError:
        return None  # Return None if the string cannot be converted to an integer

def HumanEval_experiment(dataset, dataset_loc, option, model, sequence, topn=1, temperature=1.0):
    remove_percentage = 0
    if option == 'original':
        log_file = './log/dataset_%s_model_%s_topn_%s_temperature_%s.log_%s' % \
                   (dataset, model, topn, temperature, sequence)
    else:
        log_file = './log/%s_dataset_%s_model_%s_topn_%s_temperature_%s.log_%s' % \
                   (option, dataset, model, topn, temperature, sequence)
        remove_percentage = string_to_int(get_ith_element(option, 1))
    problem_list = []
    line_cnt = 0
    with open(dataset_loc, 'r') as f:
        for line in f.readlines():
            problem_list.append(json.loads(line))
            # added by JW
            line_cnt += 1
            if MAX_NUM_PROBLEMS >= 0 and line_cnt==MAX_NUM_PROBLEMS:
                break
    names = set()
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            for line in f:
                content = json.loads(line)
                names.add(content['name'])

    response_list = []
    for problem in problem_list:
        if problem['task_id'] in names:
            continue
        print('----------------------problem name: %s--------------------------------' % (problem['task_id']), flush=True)
        print('using %s to generate response' % (model), flush=True)
        
        if dataset == "HumanEvalComm":
            input_prompt_fields = ['prompt1a','prompt1c','prompt1p','prompt2ac','prompt2ap','prompt2cp','prompt3acp']
        else:  
            input_prompt_fields = ['prompt']
        
        for input_prompt in input_prompt_fields:
            description = problem[input_prompt]
            try:
                prompt = create_prompt(description, option, remove_percentage)
                #print('!!!original prompt!!!')
                #print(description)
                #print('!!!new prompt!!!')
                #print(prompt)
                response_list = description_2_code(prompt, model, topn, temperature)
            except Exception as e:
                print('%s---------%s' % (problem['task_id'], e), flush=True)
                continue
            for i in range(len(response_list)):
                res = {
                    'name': problem['task_id'],
                    'index': i,
                    'response': response_list[i],
                    'original_prompt': description,
                    'modified_prompt': prompt,
                    'prompt_type': input_prompt,
                }
                print('response %s is writting into file' % (i), flush=True)
                json_str = json.dumps(res)
                with open(log_file, 'a') as f:
                    f.write(json_str + '\n')
            print('%s finish!' % (problem['task_id']), flush=True)
    print('Done!', flush=True)

# call LLM to generate results from problems
# input: HumanEval.jsonl
# output: file in folder log/
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--dataset",
        type=str,
        choices=['APPS', 'code_contest', 'HumanEval', 'HumanEvalComm'],
        help="Choose dataset",
        required=True,
    )
    parser.add_argument(
        "-m",
        "--model",
        help="Openai Model",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-n",
        "--topn",
        type=int,
        help="Top N candidates",
        required=True,
    )
    parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        help="Set the temperature",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--option",
        type=str,
        #choices=['original', 'rephrase', 'extractive_summarize', 'abstractive_summarize'],
        help="Choose the mode of the experiment",
        required=True,
        default='original'
    )
    parser.add_argument(
        "-s",
        "--sequence",
        type=str,
        help="Choose the order of the experiment",
        default='0'
    )
    args = parser.parse_args()
    if args.dataset.startswith('HumanEval'):
        HumanEval_experiment(args.dataset, './HumanEval/'+args.dataset+'.jsonl', args.option, args.model, args.sequence, args.topn, args.temperature)
