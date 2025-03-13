import json
import re
import argparse
import os

# Set up argument parsing
parser = argparse.ArgumentParser(description="Read and parse JSON-formatted log files in the /log/ folder.")

# Parse the arguments
args = parser.parse_args()

# Construct the log file suffix dynamically
log_file_suffix = 'gpt-4o-mini'

# Get the list of files in the /log/ directory
log_directory = './log/'
log_files = [f for f in os.listdir(log_directory) if f.endswith(log_file_suffix)]

for log_file in log_files:
    log_file_path = os.path.join(log_directory, log_file)
    try:
        # Read and parse each line as JSON
        with open(log_file_path, "r", encoding="utf-8") as file:
            all_problems = [json.loads(line) for line in file]

        # Initialize result dictionary
        result_dict = {
            "prompt1a": {"comm_rate": 0, "good_question_rate": 0, "total_count": 0},
            "prompt1c": {"comm_rate": 0, "good_question_rate": 0, "total_count": 0},
            "prompt1p": {"comm_rate": 0, "good_question_rate": 0, "total_count": 0},
            "prompt2ac": {"comm_rate": 0, "good_question_rate": 0, "total_count": 0},
            "prompt2ap": {"comm_rate": 0, "good_question_rate": 0, "total_count": 0},
            "prompt2cp": {"comm_rate": 0, "good_question_rate": 0, "total_count": 0},
            "prompt3acp": {"comm_rate": 0, "good_question_rate": 0, "total_count": 0},
            "overall": {"comm_rate": 0, "good_question_rate": 0, "total_count": 0}
        }

        for problem in all_problems:
            current_problem_type = problem.get("prompt_type")
            current_problem_answer = problem.get("answer")
            
            pattern = r"comm_rate_(\d+)_question_quality_v2_(\d+)"

            # Search for matches
            match = re.search(pattern, current_problem_answer)
            if match:
                current_problem_comm_rate = int(match.group(1))  # Extract and convert to integer
                current_problem_qq = int(match.group(2))    # Extract and convert to integer
            else: 
                current_problem_comm_rate = 0
                current_problem_qq = 0

            result_dict[current_problem_type]["total_count"] += 1
            result_dict[current_problem_type]["comm_rate"] += current_problem_comm_rate
            result_dict[current_problem_type]["good_question_rate"] += current_problem_qq

            result_dict["overall"]["total_count"] += 1
            result_dict["overall"]["comm_rate"] += current_problem_comm_rate
            result_dict["overall"]["good_question_rate"] += current_problem_qq

        for prompt in result_dict:
            if result_dict[prompt]["total_count"] > 0:
                result_dict[prompt]["good_question_rate"] = result_dict[prompt]["good_question_rate"] * 100 / (result_dict[prompt]["total_count"] * 2)
                result_dict[prompt]["comm_rate"] = result_dict[prompt]["comm_rate"] * 100 / result_dict[prompt]["total_count"]
            print(f"For file: {log_file}, prompt type: {prompt}, the good question rate is {result_dict[prompt]['good_question_rate']}, comm rate is {result_dict[prompt]['comm_rate']}")
    except FileNotFoundError:
        print(f"Error: The file {log_file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON in file {log_file_path}. Ensure the log file is properly formatted.")
