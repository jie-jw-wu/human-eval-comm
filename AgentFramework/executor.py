# This file contains code copied and modified from the following repository:
# Repository: https://github.com/huangd1999/AgentCoder/tree/main
# Original Author: Dong Huang, Jie M.Zhang, Michael Luck, Qingwen Bu, Yuhao Qing, Heming Cui
# License: MIT
import json
import random
from typing import Optional, Callable, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import sys
sys.path.append('./CodeGeeX/')
import contextlib
import io
import signal
import concurrent.futures
from tqdm import tqdm
from tqdm import tqdm
from AgentFramework.programmer import call_fetch_completion_helper
from AgentFramework.designer import call_fetch_test_completion_helper
from CodeGeeX.codegeex.benchmark.utils import read_dataset, IMPORT_HELPER
from CodeGeeX.codegeex.benchmark.execution import check_correctness
import tempfile
correct_doctest = 0
correct_before_doctest = 0
correct_after_doctest = 0
result_original = 0
result_canonical_solution = 0
result_fuzzer = 0
result_fuzzer_canonical_solution = 0
idx_run_tests_orginal = []
idx_run_tests_canonical_solution = []
idx_run_tests_fuzzer = []
idx_run_tests_fuzzer_canonical_solution = []

language = ["python","cpp","js","go","js"]


class TimeoutException(Exception):
    pass
class WriteOnlyStringIO(io.StringIO):
    """ StringIO that throws an exception when it's read from """

    def read(self, *args, **kwargs):
        raise IOError

    def readline(self, *args, **kwargs):
        raise IOError

    def readlines(self, *args, **kwargs):
        raise IOError

    def readable(self, *args, **kwargs):
        """ Returns True if the IO object can be read. """
        return False
class redirect_stdin(contextlib._RedirectStream):  # type: ignore
    _stream = 'stdin'

@contextlib.contextmanager
def swallow_io():
    stream = WriteOnlyStringIO()
    with contextlib.redirect_stdout(stream):
        with contextlib.redirect_stderr(stream):
            with redirect_stdin(stream):
                yield

@contextlib.contextmanager
def time_limit(seconds: float):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.setitimer(signal.ITIMER_REAL, seconds)
    signal.signal(signal.SIGALRM, signal_handler)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)

def process_humaneval_test(sample, problems, example_test=False,language=language, test_case=True):
    task_id = sample["task_id"]
    task_id = problems.index(sample)
    prompt = sample["prompt"]
    if example_test and "example_test" in problems[task_id] and problems[task_id]["example_test"] != "":
        test = problems[task_id]["example_test"]
    else:
        test = problems[task_id]["test"]
    if test_case:
        test = problems[task_id]["test_case"]
    code = sample["completion"]
    # Pre-process for different languages
    if language == "python":
        test_setup = "\n".join(IMPORT_HELPER["python"]) + "\n"
        if f"class sample['entry_point']" in code:
            test_string = test_setup + code + "\n" + test + "\n" + f"check({sample['entry_point']})"
        else:
            test_string = test_setup + prompt + code + "\n" + test + "\n" + f"check({sample['entry_point']})"
    return test_string



def preprocess_data(task,lg):
    if f"```{lg}" in task["completion"]:
        task["completion"] = task["completion"][task["completion"].find(f"```{lg}") +len(f"```{lg}"):]
        task["completion"] = task["completion"][:task["completion"].find("```")]
    elif "```" in task["completion"]:
        task["completion"] = task["completion"][task["completion"].find("```") +3:]
        task["completion"] = task["completion"][:task["completion"].find("```")]

    if f"```{lg}" in task["prompt"]:
        task["prompt"] = task["prompt"][task["prompt"].find(f"```{lg}") +len(f"```{lg}"):]
        task["prompt"] = task["prompt"][:task["prompt"].find("```")]
    elif "```" in task["prompt"]:
        task["prompt"] = task["prompt"][task["prompt"].find("```") +3:]
        task["prompt"] = task["prompt"][:task["prompt"].find("```")]

    if "assert" in task["prompt"]:
        task["prompt"] = task["prompt"][:task["prompt"].find("assert")]
    return task
                

def test_report(dataset,lg):
    correct = 0
    test_setup = "\n".join(IMPORT_HELPER["python"]) + "\n"
    for i in tqdm(range(len(dataset))):
        try:
            with swallow_io():
                with time_limit(2.0):
                    try:
                        exec(test_setup + "\n" + dataset[i]["completion"] + "\n" + dataset[i]["test"] + "\n" + f"check({dataset[i]['entry_point']})")
                    except NameError:
                        exec(test_setup + "\n" + dataset[i]["completion"] + "\n" + dataset[i]["test"] + "\n" + f"check(candidate)")
                correct+=1
        except Exception as exc:
            pass
    print("==============Start Report Testing==============")
    print(f"test_report: {(correct/len(dataset)*100):.1f}")

def test_agent_concurrency(dataset, lg):
    test_setup = "\n".join(IMPORT_HELPER["python"]) + "\n"
    # total_correct = 0
    _for_completion = 0
    def process_item(i):
        if "need_reproduce" in dataset[i].keys() and dataset[i]["need_reproduce"]==False:
            # dataset[i]["need_reproduce"] = True
            return dataset[i]["max_correct"], dataset[i]["idx"]
        completion_list = dataset[i]["completion_list"]
        test_case_list = dataset[i]["test_case_list"]
        correct_list = []
        # Randomly sample one completion to initialize the "completion" entry
        dataset[i]["completion"] = random.choice(completion_list)
        # this entry is needed by check_correctness() to run properly

        for j in range(len(completion_list)):
            correct = 0
            if f"def {dataset[i]['entry_point']}" and f"def candidate" not in completion_list[j]:
                correct_list.append(correct)
                continue
            for k in range(len(test_case_list)):
                if f"assert {dataset[i]['entry_point']}(" and f"assert candidate(" not in test_case_list[k]:
                    continue
                dataset[i]["full_code"] = test_setup + "\n" + completion_list[j] + "\n" + test_case_list[k]
                try:
                    result = check_correctness(dataset[i]["task_id"], dataset[i], lg, 3, "./tmp")
                except NameError:
                    dataset[i]["full_code"] = test_setup + "\n" + completion_list[j].replace(entry_point, "candidate") + "\n" + test_case_list[k].replace(entry_point, "candidate")
                    result = check_correctness(dataset[i]["task_id"], dataset[i], lg, 3, "./tmp")
                if result["passed"]:
                    correct += 1
            correct_list.append(correct)

        max_correct = max(correct_list)
        idx = correct_list.index(max_correct)
        return max_correct, idx

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_item, i) for i in range(len(dataset))]

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(dataset)):
            max_correct, idx = future.result()
            if max_correct >= 3: # GPT-3.5-turbo-1106's test case accuracy is about 67%. So we choice 60% as the bar.
                i = futures.index(future)
                dataset[i]["completion"] = dataset[i]["completion_list"][idx]
                print("created completion list")
                dataset[i]["need_reproduce"] = False
                dataset[i]["idx"] = idx
                dataset[i]["max_correct"] = max_correct
                _for_completion += 1
            else:
                i = futures.index(future)
                dataset[i]["completion"] = dataset[i]["completion_list"][idx]

    return dataset

def executor_main(task_id):
    model_list = ["AgentCoder"]
    language = ["python"]
    for model in model_list:
        for lg in language:
            path = f"./dataset/{model}_{lg}_{task_id}.json"
            with open(path, "r") as f:
                dataset = json.load(f)
            # epoch = 1
            # for current_epoch in range(epoch):
            # # We choose to run only one epoch for our baseline
            dataset = test_agent_concurrency(dataset,lg)
            test_report(dataset,lg)
            dataset = call_fetch_completion_helper(dataset,model,lg)
            dataset = call_fetch_test_completion_helper(dataset,model,lg)
            with open(f"./dataset/{model}_{task_id}.json", "w") as f:
                json.dump(dataset, f, indent=4)
            dataset = test_agent_concurrency(dataset,lg)
            test_report(dataset,lg)
    return dataset
