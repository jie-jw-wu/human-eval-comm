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

# Standard Library Modules
import argparse

# External Modules
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed

# set random seed
set_seed(42)


openai.api_key = os.environ['OPENAI_KEY']
MAX_NUM_PROBLEMS = 1 # limit the number of problems to be run and call ChatGPT. -1 means no such limit
PROMPT_START_0 = 'Generate Python3 code (Markdown):\n'
PROMPT_START_1 = 'Generate either Python3 code only (Markdown) or no code:\n'
PROMPT_START_2 = 'Generate either Python3 code only (Markdown) or ask questions:\n'
PROMPT_START_3 = 'You are an expert software developer. Generate Python3 code (code must has Markdown in response) in below information. Alternatively, you can ask clarifying questions: \n'
PROMPT_START_3_v2 = 'You are an expert software developer who writes high quality code. With below information, please either generate Python3 code (Respond directly with code only with markdown), or ask clarifying questions: \n'

PROMPT_EVALUATE_QUESTIONS = 'The original description of a coding problem is modified so that the requriements become inconsistent, incomplete or ambiguous. Given the modifed description, some clarifying questions were raised to clarify the description. Given the original and modified problem description, evaluate the quality of the questions. Please provide an integer representing the quality of questions (3: Good questions that recover all missing info. 2: Fair questions that recover some missing info. 1: Bad questions or totally irrelevent content).\n  QUALITY=[your int] \n Please also provide answers to the questions to recover the missing requirements! \n ANSWERS=```[your answer]``` \n Please strictly follow the format RESULT=[the int] and ANSWERS=```[the answer]``` in the response! \n\n ### Questions: {clarifying_questions} \n ### Problem Description: {problem} \n ### Original Description: {missing_information} \n'
PROMPT_2ND_ROUND = '\n Given above conversations, generate Python code directly (Markdown) to solve the coding problem:\n'
OK_PROMPT_CODEGEN = 'Generate Python code directly (Markdown) to solve the coding problem. \n\n'
OK_PROMPT_CLARIFY_Q = 'Given the coding problem description and the generated code above, decide whether to ask clarifying questions that are necessary to solve the problem correctly. \n If no need to ask clarifying questions, return strictly \'NO_QUESTIONS\' only. Otherwise, return the clarifying questions. \n\n'
    #+ "### Problem Description: {problem} \n"
    #+ "### Generated Code: {code} \n"

# Instruction-tuned Models and Foundation Models have different nl_2_pl/pl_2_nl prompts and functions
INSTRUCTION_MODELS = [
    "codellama/CodeLlama-7b-Instruct-hf",
    "codellama/CodeLlama-13b-Instruct-hf",
    "codellama/CodeLlama-34b-Instruct-hf",
    "HuggingFaceH4/starchat-beta",
]
FOUNDATION_MODELS = [
    "bigcode/starcoder",
    "bigcode/starcoderplus",
    "bigcode/starcoderbase",
    "bigcode/starcoderbase-7b",
    "bigcode/starcoderbase-3b",
    "bigcode/starcoderbase-1b",
    "codellama/CodeLlama-7b-hf",
    "codellama/CodeLlama-13b-hf",
    "codellama/CodeLlama-34b-hf",
]


# prompt settings
NL_2_PL_HUMANEVAL = [
    {  # Instructions
        "role": "system",
        "content": "Solve a coding problem in Python. "
        + "Given the function signature and the problem description in the docstring, "
        + "you only need to continue to complete the function body. "
        + "Please strictly follow the format of the example below! "
        + "Don't write down any thought processes! "
        + "Don't copy the problem description! "
        + "You must use correct indentation! "
        + "Make sure your return statement is always inside the function! "
        + "Make sure your output always starts with an indentation of exactly 4 spaces! "
        + "Output an indentation of 4 spaces first before you write anything else! "
        + "You’d better be sure. \n\n",
    },
    {  # One-Shot Example: user input = function signature + problem description in docstring format
        "role": "user",
        "content": 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n    '
        + '"""Check if in given list of numbers, are any two numbers closer to each other than\n    given threshold.\n    '
        + '>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n    False\n    '
        + '>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n    True\n    """\n',
    },
    {  # One-Shot Example: model output = solution
        "role": "assistant",
        "content": '    sorted_numbers = sorted(numbers)\n    for i in range(len(sorted_numbers) - 1):\n        '
        + 'if sorted_numbers[i + 1] - sorted_numbers[i] < threshold:\n            return True\n    return False\n\n',
    },
    {  # Instructions to emphasize the format
        "role": "system",
        "content": "\nPlease strictly follow the format of the example above! "
        + "You must use correct indentation! "
        + "Make sure your return statement is always inside the function! "
        + "Make sure your output always starts with an indentation of exactly 4 spaces! "
        + "Output an indentation of 4 spaces first before you write anything else! "
        + "You’d better be sure. \n\n",
    },
]

PL_2_NL_HUMANEVAL = [
    {  # Instructions
        "role": "system",
        "content": "Given a Python solution to a coding problem, "
        + "write an accurate problem description for it in the format of Python docstring without 'Args' and 'Returns'. "
        + "Please strictly follow the format of the example below!"
        + "Provide all necessary details to accurately describe the problem, but in a concise way! "
        + "Make sure to give a few examples of inputs and outputs in the docstring! "
        + "Make sure the docstring has no 'Args' and no 'Returns'! "
        + "You can only write a text desciption with a few examples as shown in the example below!  "
        + "Make sure your output always starts with an indentation of exactly 4 spaces! "
        + "You’d better be sure. \n\n",
    },
    {  # One-Shot Example: user input = function signature + candidate solution
        "role": "user",
        "content": 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n    '
        + 'sorted_numbers = sorted(numbers)\n    for i in range(len(sorted_numbers) - 1):\n        '
        + 'if sorted_numbers[i + 1] - sorted_numbers[i] < threshold:\n            return True\n    return False\n\n',
    },
    {  # One-Shot Example: model output = problem description in docstring format
        "role": "assistant",
        "content": '    """Check if in given list of numbers, are any two numbers closer to each other than\n    '
        + 'given threshold.\n    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n    False\n    '
        + '>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n    True\n    """\n',
    },
    {  # Instructions to emphasize the format
        "role": "system",
        "content": "\nPlease strictly follow the format of the example above! "
        + "Provide all necessary details to accurately describe the problem, but in a concise way! "
        + "Make sure to give a few examples of inputs and outputs in the docstring! "
        + "Make sure the docstring has no 'Args' and no 'Returns'! "
        + "You can only write a text desciption with a few examples as shown in the example above!  "
        + "Make sure your output always starts with an indentation of exactly 4 spaces! "
        + "You’d better be sure. \n\n",
    },
]

NL_2_PL_MBPP = [
    {  # Instructions
        "role": "system",
        "content": "Solve a coding problem in Python. "
        + "Given the function signature and the problem description in the docstring, you only need to continue to complete the function body. "
        + "Please strictly follow the format of the example below! "
        + "Don't write down any thought processes! "
        + "Don't copy the problem description! "
        + "You must use correct indentation! "
        + "Make sure your return statement is always inside the function! "
        + "Make sure your output always starts with an indentation of exactly 4 spaces! "
        + "Output an indentation of 4 spaces first before you write anything else! "
        + "You’d better be sure. \n\n",
    },
    {  # One-Shot Example: user input = function signature + problem description in docstring format
        "role": "user",
        "content": 'def similar_elements(test_tup1, test_tup2):\n    '
        + '""" Write a function to find the shared elements from the given two lists.\n    """\n',
    },
    {  # One-Shot Example: model output = solution
        "role": "assistant",
        "content": '    res = tuple(set(test_tup1) & set(test_tup2))\n    return (res)\n\n',
    },
    {  # Instructions to emphasize the format
        "role": "system",
        "content": "\nPlease strictly follow the format of the example above! "
        + "You must use correct indentation! "
        + "Make sure your return statement is always inside the function! "
        + "Make sure your output always starts with an indentation of exactly 4 spaces! "
        + "Output an indentation of 4 spaces first before you write anything else! "
        + "You’d better be sure. \n\n",
    },
]

PL_2_NL_MBPP = [
    {  # Instructions
        "role": "system",
        "content": "Given a Python solution to a coding problem, write an accurate problem description for it in the format of Python docstring"
        + "Please strictly follow the format of the example below!"
        + "Provide all necessary details to accurately describe the problem, but in a concise way! "
        + "Make sure the docstring has no 'Args', no 'Returns', and no 'Examples'! "
        + "You can only write a plain text desciption as shown in the example below! "
        + "Make sure your output always starts with an indentation of exactly 4 spaces! "
        + "You’d better be sure. \n\n",
    },
    {  # One-Shot Example: user input = function signature + candidate solution
        "role": "user",
        "content": 'def similar_elements(test_tup1, test_tup2):\n    res = tuple(set(test_tup1) & set(test_tup2))\n    return (res)\n\n',
    },
    {  # One-Shot Example: model output = problem description in docstring format
        "role": "assistant",
        "content": '    """ Write a function to find the shared elements from the given two lists.\n    """\n',
    },
    {  # Instructions to emphasize the format
        "role": "system",
        "content": "\nPlease strictly follow the format of the example above! "
        + "Provide all necessary details to accurately describe the problem, but in a concise way! "
        + "Make sure the docstring has no 'Args', no 'Returns', and no 'Examples'! "
        + "You can only write a plain text desciption as shown in the example above! "
        + "Make sure your output always starts with an indentation of exactly 4 spaces! "
        + "You’d better be sure. \n\n",
    },
]

ONE_SHOT_HUMANEVAL = (
    'def has_close_elements(numbers: List[float], threshold: float) -> bool:\n    '
    + '"""Check if in given list of numbers, are any two numbers closer to each other than\n    given threshold.\n    '
    + '>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n    False\n    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n    '
    + 'True\n    """\n    sorted_numbers = sorted(numbers)\n    for i in range(len(sorted_numbers) - 1):\n        '
    + 'if sorted_numbers[i + 1] - sorted_numbers[i] < threshold:\n            return True\n    return False\n\n'
)

ONE_SHOT_MBPP = (
    'def similar_elements(test_tup1, test_tup2):\n    """ Write a function to find the shared elements from the given two lists.\n    '
    + '"""\n    res = tuple(set(test_tup1) & set(test_tup2))\n    return (res)\n\n'
)


def generate_text(model, tokenizer, prompt_text, args, eos_token_id=None):
    if eos_token_id is None:
        eos_token_id = tokenizer.eos_token_id
    model_inputs = tokenizer(prompt_text, padding=False, add_special_tokens=False, return_tensors="pt")
    model_inputs["prompt_text"] = prompt_text
    input_ids = model_inputs["input_ids"]
    attention_mask = model_inputs.get("attention_mask", None)
    # Allow empty prompts
    if input_ids.shape[1] == 0:
        input_ids = None
        attention_mask = None
        in_b = 1
    else:
        in_b = input_ids.shape[0]
    # BS x SL
    if args.gen_length is None:
        max_length = args.seq_length
    else:
        max_length = input_ids.shape[1] + args.gen_length
    print("Generating text...")
    generated_sequence = model.generate(
        input_ids=input_ids.to(model.device),
        attention_mask=attention_mask.to(model.device),
        temperature=args.temperature,
        top_k=args.top_k,
        top_p=args.top_p,
        max_length=max_length,
        do_sample=args.do_sample,
        num_beams=args.num_beams,
        num_return_sequences=args.num_return_sequences,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=eos_token_id,
    )
    out_b = generated_sequence.shape[0]
    generated_sequence = generated_sequence.reshape(in_b, out_b // in_b, *generated_sequence.shape[1:])
    generated_sequence = generated_sequence[0].cpu().numpy().tolist()
    records = []
    print("Decoding text...")
    for sequence in generated_sequence:
        text = tokenizer.decode(sequence, skip_special_tokens=True)
        prompt_length = len(tokenizer.decode(input_ids[0], skip_special_tokens=True))
        all_text = text[prompt_length:]
        record = {"generated_text": all_text}
        records.append(record)
    return records


def get_completion_starchat_nl_to_pl(prompt, user_input, model, tokenizer, args):
    # select the correct in-context learning prompt based on the task
    messages = prompt + [{"role": "user", "content": user_input}]
    try:
        dialogue_template = DialogueTemplate.from_pretrained(args.model_name_or_path)
    except Exception:
        print("No dialogue template found in model repo. Defaulting to the `no_system` template.")
        dialogue_template = get_dialogue_template("no_system")
    dialogue_template.messages = messages
    formatted_prompt = dialogue_template.get_inference_prompt_nl_to_pl()
    # Debug
    # print(formatted_prompt)
    # get completion from code lm
    output = generate_text(
        model,
        tokenizer,
        formatted_prompt,
        args,
        eos_token_id=tokenizer.convert_tokens_to_ids(dialogue_template.end_token),
    )
    completion = output[0]["generated_text"]
    # post-processing
    completion_lines = completion.split("\n")
    processed_completion = ""
    for line in completion_lines:
        if line.startswith("    "):
            processed_completion += line + "\n"
    # remove extra docstring
    # find all occurrences of three consecutive double quotes
    res = [i for i in range(len(processed_completion)) if processed_completion.startswith('"""', i)]
    # if res is empty, check for both single quotes
    if not res:
        res = [i for i in range(len(processed_completion)) if processed_completion.startswith("'''", i)]
    # if found an extra docstring, remove it
    if res:
        # get end position of the extra docstring, remove everything before it
        try:
            end_position = res[1] + 3
            processed_completion = processed_completion[end_position:]
            if processed_completion.startswith("\n"):
                processed_completion = processed_completion[1:]
        except IndexError:
            pass

    # Debug
    print(processed_completion)
    return processed_completion


def get_completion_starchat_pl_to_nl(prompt, user_input, model, tokenizer, args):
    # select the correct in-context learning prompt based on the task
    messages = prompt + [{"role": "user", "content": user_input}]
    try:
        dialogue_template = DialogueTemplate.from_pretrained(args.model_name_or_path)
    except Exception:
        print("No dialogue template found in model repo. Defaulting to the `no_system` template.")
        dialogue_template = get_dialogue_template("no_system")
    dialogue_template.messages = messages
    formatted_prompt = dialogue_template.get_inference_prompt_pl_to_nl()
    # Debug
    # print(formatted_prompt)
    # get completion from code lm
    output = generate_text(
        model,
        tokenizer,
        formatted_prompt,
        args,
        eos_token_id=tokenizer.convert_tokens_to_ids(dialogue_template.end_token),
    )
    completion = output[0]["generated_text"]
    # post-processing: extract the docstring
    completion = completion.replace("python", "")
    completion_parts = completion.split("```")
    if len(completion_parts) > 1:
        completion = completion_parts[1]
    completion_parts = completion.split('"""')
    if len(completion_parts) > 1:
        completion = completion_parts[1]
    completion_parts = completion.split("'''")
    if len(completion_parts) > 1:
        completion = completion_parts[1]

    # double check
    if not completion.startswith('"""'):
        completion = '"""' + completion
    if not completion.endswith('"""'):
        completion = completion + '\n"""'
    completion_lines = completion.split("\n")
    for idx, line in enumerate(completion_lines):
        if not line.startswith("    "):
            completion_lines[idx] = "    " + line
    completion = "\n".join(completion_lines)
    # Debug
    print(completion)
    return completion


def get_completion_codellama_instruct_nl_to_pl(
    prompt, user_input, model, tokenizer, args
):  # reference: https://github.com/facebookresearch/codellama/blob/main/llama/generation.py
    # select the correct in-context learning prompt based on the task
    messages = prompt + [{"role": "user", "content": user_input}]
    formatted_prompt = ""
    for msg in messages:
        if msg["role"] == "user":
            content = msg["content"].strip()
            formatted_prompt += tokenizer.bos_token + f"{B_INST_CLLAMA} " + content + f" {E_INST_CLLAMA} "
        elif msg["role"] == "assistant":
            formatted_prompt += " " + msg["content"].strip() + " " + tokenizer.eos_token
        # system prompt doesn't work well for Code Llama-Instructs
        # elif msg["role"] == "system":
        #     formatted_prompt += f"{B_SYS_CLLAMA}" + msg["content"] + f"{E_SYS_CLLAMA}"
    # Debug
    # print(formatted_prompt)
    output = generate_text(model, tokenizer, formatted_prompt, args)
    completion = output[0]["generated_text"]

    # post-processing
    completion_lines = completion.split("\n")
    processed_completion = ""
    for line in completion_lines:
        if line.startswith("    "):
            processed_completion += line + "\n"

    # remove extra docstring
    # find all occurrences of three consecutive double quotes
    res = [i for i in range(len(processed_completion)) if processed_completion.startswith('"""', i)]
    # if res is empty, check for both single quotes
    if not res:
        res = [i for i in range(len(processed_completion)) if processed_completion.startswith("'''", i)]
    # if found an extra docstring, remove it
    if res:
        # get end position of the extra docstring, remove everything before it
        try:
            end_position = res[1] + 3
            processed_completion = processed_completion[end_position:]
            if processed_completion.startswith("\n"):
                processed_completion = processed_completion[1:]
        except IndexError:
            pass

    # Debug
    print(processed_completion)
    return processed_completion


def get_completion_codellama_instruct_pl_to_nl(prompt, user_input, model, tokenizer, args):
    # select the correct in-context learning prompt based on the task
    messages = prompt + [{"role": "user", "content": user_input}]
    formatted_prompt = ""
    for msg in messages:
        if msg["role"] == "user":
            if args.input_path.endswith("EvalPlus-Mini-v0.1.6_reformatted.jsonl"):
                content = (
                    msg["content"]
                    + "\n\nWhat should be the docstring of the above function? Please only write down the docstring with some examples."
                )
            elif args.input_path.endswith("MBPP-S_test_reformatted.jsonl"):
                content = (
                    msg["content"]
                    + "\n\nWhat should be the docstring of the above function? Please write down the docstring only in words without any examples!"
                )
            else:
                raise ValueError(f"Input file {args.input_path} not supported")
            formatted_prompt += tokenizer.bos_token + "[INST] " + content + " [/INST] "
        elif msg["role"] == "assistant":
            formatted_prompt += " " + msg["content"].strip() + " " + tokenizer.eos_token
    # Debug
    # print(formatted_prompt)
    output = generate_text(model, tokenizer, formatted_prompt, args)
    completion = output[0]["generated_text"]
    # post-processing
    completion_lines = completion.split("\n")
    for idx, line in enumerate(completion_lines):
        if not line.startswith("    "):
            completion_lines[idx] = "    " + line.lstrip()
    completion = "\n".join(completion_lines)
    # add docstring guards if not present
    if completion.startswith('    """') and not completion.endswith('"""'):
        completion = completion + '"""'
    elif completion.startswith("    '''") and not completion.endswith("'''"):
        completion = completion + "'''"
    # Debug
    print(completion)
    return completion


def get_completion_codellama(
    prompt, user_input, model, tokenizer, args
):  # prompt is ONE_SHOT_HUMANEVAL or ONE_SHOT_MBPP
    user_input = prompt + user_input
    output = generate_text(model, tokenizer, user_input, args)
    completion = output[0]["generated_text"]
    # post-processing: extract the function body
    processed_completion = ""
    completion_lines = completion.split("\n")
    for line in completion_lines:
        if line.startswith("    "):
            processed_completion += line + "\n"
        else:
            break
    # Debug
    print(processed_completion)
    return processed_completion


def get_completion_codellama_fim(
    prompt, function_signature, function_body, model, tokenizer, args
):  # prompt is ONE_SHOT_HUMANEVAL or ONE_SHOT_MBPP
    function_signature = prompt + function_signature
    fim_prompt = ""
    # check indent
    fim_prompt += (
        " <PRE>" + function_signature + "    \"\"\"\n    " + " <SUF>" + "    \"\"\"\n" + function_body + " <MID>"
    )
    # Debug
    # print(fim_prompt)
    output = generate_text(model, tokenizer, fim_prompt, args)
    completion = output[0]["generated_text"]
    completion = "    \"\"\"\n    " + completion + "    \"\"\"\n"
    # Debug
    print(completion)
    return completion


def get_completion_starcoder(
    prompt, user_input, model, tokenizer, args
):  # prompt is ONE_SHOT_HUMANEVAL or ONE_SHOT_MBPP
    user_input = prompt + user_input
    output = generate_text(model, tokenizer, user_input.strip(), args)
    completion = output[0]["generated_text"]
    # post-processing: extract the function body
    processed_completion = ""
    completion_lines = completion.split("\n")
    start = False
    for line in completion_lines:
        if line.startswith("    "):
            start = True
            processed_completion += line + "\n"
        else:
            if start:
                break
    # Debug
    print(processed_completion)
    return processed_completion


def get_completion_starcoder_fim(
    prompt, function_signature, function_body, model, tokenizer, args
):  # prompt is ONE_SHOT_HUMANEVAL or ONE_SHOT_MBPP
    function_signature = prompt + function_signature
    fim_prompt = ""
    # TODO check indent
    fim_prompt += (
        "<fim_prefix>"
        + function_signature
        + "    \"\"\""
        + "<fim_suffix>"
        + "\"\"\"\n"
        + function_body
        + "<fim_middle>"
    )
    output = generate_text(model, tokenizer, fim_prompt, args)
    completion = output[0]["generated_text"]
    completion = "    \"\"\"" + completion + "\"\"\"\n"
    # Debug
    print(completion)
    return completion



def evaluate_clarifying_questions(
    missing_information='',
    clarifying_questions='',
    problem=''
):
    print("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print('!!!!!!! 2nd evaluate_clarifying_questions START !!!!!!!!!!!')
    topn = 1
    temperature = 1.0
    model = 'gpt-3.5-turbo-0125' #'gpt-3.5-turbo'
    content = PROMPT_EVALUATE_QUESTIONS.format(
                missing_information=missing_information,
                clarifying_questions=clarifying_questions,
                problem=problem
            )
    completion = openai.ChatCompletion.create(
        model=model,
        n=topn,
        temperature=temperature,
        messages=[{
            "role": "user",
            "content": content,
        }]
    )
    print('!!!!!!!PROMPT_EVALUATE_QUESTIONS='+content)
    print('!!!!!!!Completion='+completion['choices'][0]['message']['content'])
    # Convert completion content to a string if it's not already a string
    completion_content = str(completion['choices'][0]['message']['content'])

    # Use re.findall() with the completion content
    question_quality = re.findall(r'QUALITY\s*=?\s*(\d+)', completion_content)
    answers = re.findall(r'ANSWERS\s*=?\s*```(.+?)```', completion_content, flags=re.DOTALL)
    answer_str = answers[0] if answers else ""
    question_quality_str = question_quality[0] if question_quality else ""
    print('!!!!!!!answer_str',answer_str)
    print('!!!!!!!question_quality_str',question_quality_str)
    
    print('!!!!!!! 2nd evaluate_clarifying_questions END !!!!!!!!!!!')
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
    return answer_str, question_quality_str

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

# legacy code (randRemove) where only one-round evaluation is enabled
def description_2_code_one_round(prompt, model, topn, temperature, args, open_source_model, tokenizer):
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

    else:
        messages=[{"role": "user", "content": prompt}]
        response_list = generate_response(model, messages, topn, temperature, args, open_source_model, tokenizer)
    code_list = []
    qq_list = []
    for i in range(len(response_list)):
        code = response_2_code(response)
        code_list.append(code)
        qq_list.append('0')
    return response_list, code_list, qq_list

def generate_response_str(model, msgs, temperature, args, open_source_model, tokenizer):
    response_list = generate_response(model, msgs, 1, temperature, args, open_source_model, tokenizer)
    return response_list[0]
    
def generate_response(model, msgs, topn, temperature, args, open_source_model, tokenizer):
    if model == 'OpenSourceModel':
        user_input = tokenizer.apply_chat_template(msgs, tokenize=False)
        response_list = []
        for i in range(topn):
            response_list.append(get_completion_starcoder('', user_input, open_source_model, tokenizer, args))
        return response_list        
    else:
        completion = openai.ChatCompletion.create(
            model=model,
            n=topn,
            temperature=temperature,
            messages=msgs
        )
        response_list = []
        for i in completion['choices']:
            response_list.append(i['message']['content'])
        return response_list

def description_2_code_multi_rounds(prompt, user_input, original_prompt, model, topn, temperature, args, open_source_model, tokenizer):
    ## 1st round: initial code generation
    full_prompt = prompt + user_input
    print("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print('!!!!!!!!!!!!! prompt:\n' + full_prompt)
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
    messages = []
    response_list = []
    model_2nd_round = model
    if model == 'Okanagan':
        # this code assume topn=1
        # set the real model used by Okanagan
        ok_model = 'gpt-3.5-turbo-0125'
        model_2nd_round = ok_model
        messages.append({"role": "user","content": OK_PROMPT_CODEGEN + user_input})
        coder_response = generate_response_str(ok_model, messages, temperature, args, open_source_model, tokenizer)
        messages.append({"role": "assistant","content": coder_response})
        messages.append({"role": "user","content": OK_PROMPT_CLARIFY_Q})
        # Reflection
        communicator_response = generate_response_str(ok_model, messages, temperature, args, open_source_model, tokenizer)
        messages.append({"role": "assistant","content": communicator_response})
        if  re.search('no_questions', communicator_response, re.IGNORECASE):
            response_list.append(coder_response)
        else:
            response_list.append(communicator_response)
    else:
        messages.append({"role": "user","content": full_prompt})
        response_list = generate_response(model, messages, topn, temperature, args, open_source_model, tokenizer)
    code_list = []
    qq_list = []
    for i in range(len(response_list)):
        response = response_list[i]
        code = response_2_code_if_no_text(response)
        
        print("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print('!!!!!!!!!!!!! 1st CodeLLM response:\n' + response)
        print('!!!!!!!!!!!!! 1st CodeLLM response code:\n' + code)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
        question_quality = '0'
        if code == '':
            ## 2nd round: question & answer round
            
            # use LLM-based Evaluator to
            # 1) generate answer,
            # 2) evaluate quality of clarifying questions,
            # 3) generate new code with Q&A
            answer, question_quality = evaluate_clarifying_questions(original_prompt,response,full_prompt)
            
            ## 3rd round: generate final code: generate 2nd-round code with chat history (Q&A)
            msgs_i = messages.copy()
            msgs_i.append({"role":"assistant","content": response})
            msgs_i.append({"role":"user","content": answer + PROMPT_2ND_ROUND})
            
            response_2nd = generate_response(model_2nd_round, msgs_i, 1, temperature, args, open_source_model, tokenizer)
            code = response_2_code_if_no_text(response_2nd[0])
            
            print("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print('!!!!!!!!!!!!! 3rd CodeLLM response:\n', response_2nd)
            print('!!!!!!!!!!!!! 3rd CodeLLM input messages:\n', msgs_i)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
        qq_list.append(question_quality)
        code_list.append(code)
    return response_list, code_list, qq_list

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

# TODO(jwu): bug this code return last triple code snippet. 
def response_2_code(response):
    code_template = re.compile('```.*\n([\s\S]+?)\n```', re.M)
    code = code_template.findall(response)
    if len(code) > 0:
        return code[-1]
    else:
        return ''

# returns code only if the response consists solely of code with markups
def response_2_code_if_no_text(response):
     # adding optional spaces (`\s*`) allowed surrounding the markup. Was using ^```.*\n([\s\S]+?)\n```$ 
    code_template = re.compile(r'^\s*```.*?\n([\s\S]+?)\n```\s*$', re.M)
    code = code_template.findall(response)
    if len(code) > 0:
        return code[-1]
    return ''
        
def HumanEval_experiment(dataset, dataset_loc, option, model, sequence, topn, temperature, args, open_source_model, tokenizer):
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
            if args.max_num_problems >= 0 and line_cnt==args.max_num_problems:
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
            if input_prompt not in problem:
                continue
            
            print("********************************************************************")
            print("****** new problem (input_prompt="+input_prompt+") ******")
            print("********************************************************************\n\n")
            description = problem[input_prompt]
            try:
                prompt = create_prompt(description, option, remove_percentage)
                if option.startswith('randRemove'):
                    # legacy part
                    response_list, code_list, qq_list = description_2_code_one_round(prompt, model, topn, temperature, args, open_source_model, tokenizer)
                else:
                    original_prompt = PROMPT_START_3_v2 + problem['prompt']
                    response_list, code_list, qq_list = description_2_code_multi_rounds(PROMPT_START_3_v2, description, original_prompt, model, topn, temperature, args, open_source_model, tokenizer)
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
                    'code': code_list[i],
                    'question_quality': qq_list[i],
                }
                print('response %s is writting into file' % (i), flush=True)
                json_str = json.dumps(res)
                with open(log_file, 'a') as f:
                    f.write(json_str + '\n')
            print('%s finish!' % (problem['task_id']), flush=True)
    print('Done!', flush=True)

def test_starcoder(tokenizer, model):
    device = 'cpu'
    inputs = tokenizer.encode(
        "def helloworld():",
        # compute a + b 
        #"def print_hello_world():", 
        return_tensors="pt"
        ).to(device)
    outputs = model.generate(inputs)
    print('!!!!!!!!!!')
    print(tokenizer.decode(outputs[0]))
    print('!!!!!!!!!!')

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
        default=1,
    )
    parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        help="Set the temperature",
        required=True,
        default='1',
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
    parser.add_argument(
        "-maxp",
        "--max_num_problems",
        type=int,
        help="Max number of problems to run",
        required=True,
        default=-1,
    )
    
    # args from open sources models

    parser.add_argument('--model_name_or_path', type=str, help='Path to the model')
    parser.add_argument('--hf_dir', type=str, help='Path to the huggingface cache directory')
    parser.add_argument('--input_path', type=str, help='Path to the input file')
    parser.add_argument('--output_dir', type=str, help='Path to the output directory')
    parser.add_argument('--chain_length', type=int, default=5, help='Number of steps in the Identity Chain')
    parser.add_argument('--seq_length', type=int, default=2048, help='max length of the sequence')
    parser.add_argument('--gen_length', type=int, default=None, help='max length of the generated sequence')
    parser.add_argument('--do_sample', action='store_true', help='whether to do sampling')
    parser.add_argument('--greedy_early_stop', action='store_true', help='whether to stop inference when fixed point')
    #parser.add_argument('--temperature', type=float, default=0, help='temperature for sampling')
    parser.add_argument('--top_k', type=int, default=0, help='top k for sampling')
    parser.add_argument('--top_p', type=float, default=1, help='top p for sampling')
    parser.add_argument('--num_return_sequences', type=int, default=1, help='number of return sequences')
    parser.add_argument('--num_beams', type=int, default=1, help='number of beams for beam search')
    parser.add_argument('--use_int8', action='store_true', help='whether to use int8 quantization')
    parser.add_argument('--use_fp16', action='store_true', help='whether to use fp16 precision')
    parser.add_argument('--pass_only', action='store_true', help='whether to only pass the input to the next step')
    parser.add_argument('--mask_func_name', action='store_true', help='whether to mask the function name')
    parser.add_argument('--bootstrap_method', type=str, default='problem', help='method to bootstrap the chain')
    parser.add_argument('--resume_task_bs', type=int, default=0, help='task to resume at when bootstrapping')
    parser.add_argument('--resume_task_run', type=int, default=0, help='task to resume at')
    parser.add_argument('--skip_bootstrap', action='store_true', help='whether to skip the bootstrap stage')
    parser.add_argument('--version', type=str, default='v1', help='version of the identity chain')

    args = parser.parse_args()
    model = None
    tokenizer = None
    if args.model == 'OpenSourceModel':
        # set huggingface cache directory
        HF_HOME = args.hf_dir
        offload_folder = "D:\Study\Research\Projects\huggingface\offload_folder"
        print("Loading model...")
        # if specified, use int8 quantization
        if args.use_int8:
            print("**********************************")
            print("**** Using 8-bit quantization ****")
            print("**********************************")
            model = AutoModelForCausalLM.from_pretrained(
                args.model_name_or_path,
                load_in_8bit=True,
                device_map="auto",
                cache_dir=HF_HOME,
                offload_folder=offload_folder,     
            )
        # if specified, use fp16 precision
        elif args.use_fp16:
            print("**********************************")
            print("****** Using fp16 precision ******")
            print("**********************************")
            model = AutoModelForCausalLM.from_pretrained(
                args.model_name_or_path,
                device_map="auto",
                torch_dtype=torch.float16,
                cache_dir=HF_HOME,
                offload_folder=offload_folder,     
            )
        # otherwise, use default precision
        else:
            model = AutoModelForCausalLM.from_pretrained(
                args.model_name_or_path,
                device_map="auto",
                cache_dir=HF_HOME,
                offload_folder=offload_folder,            
            )

        # configure tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            args.model_name_or_path,
            model_max_length=args.seq_length,
            # Bug: A decoder-only architecture is being used, but right-padding was detected! For correct generation results, please set `padding_side='left'` when initializing the tokenizer.
            # setting padding_side='left' doesn't fix the issue.
            padding_side="right",
            use_fast=False,
            trust_remote_code=True,
            cache_dir=HF_HOME,
            offload_folder=offload_folder,
        )

    # test_starcoder(tokenizer, model)
    
    if args.dataset.startswith('HumanEval'):
        HumanEval_experiment(args.dataset, './HumanEval/'+args.dataset+'.jsonl', args.option, args.model, args.sequence, args.topn, args.temperature, args, model, tokenizer)
