import json
import re
import numpy as np
import scipy.stats as stats
import os
import argparse
import openpyxl
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import math

MAX_NUM_PROBLEMS = 0 # from generate_response.py

def create_boxplot(data, title, xlabel, ylabel):
    """
    Create a boxplot to visualize the distribution of an array.

    :param data: The array whose distribution is to be plotted.
    :param title: Title for the plot (default is "Box Plot").
    """
    plt.boxplot(data)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()

def ratio_of_worst(list, target):
    # calculating the ratio of worst cases happened in dataset
    # sepecially for test pass rate, OER, OER_ow
    count = 0
    for case in list:
        if case == target:
            count += 1

    # print(dataset)
    # print(temperature)
    # print(count/len(list))
    if len(list) == 0:
        return -1
    else:
        return (count/len(list))

def semantic_syntactic_structural_similarity(prompt_type):
    # get all measurement of semantic, syntactic, and structural similarity
    # where all the file_path could be modified directly with line 'with open(x) as f:'

    # get semantic similarity and syntactic similarity
    if dataset != 'code_contest':
        if request_way == 'R1':
            with open(file_path + '/%s_dataset_%s_%s_%s/intermediate_result_among5.json' % (experiment, dataset, model, temperature), 'r') as f:
                intermediate_result = json.load(f)
        else:
            with open(file_path + '/%s_dataset_%s_%s_%s/intermediate_result_top0_5.json' % (experiment, dataset, model, temperature), 'r') as f:
                intermediate_result = json.load(f)
    else:
        if request_way == 'R1':
            with open(file_path + '/%s_dataset_%s_%s_%s/intermediate_result_among5.json' % (experiment, dataset, model, temperature), 'r') as f:
                intermediate_result = json.load(f)
        else:
            with open(file_path + '/%s_dataset_%s_%s_%s/intermediate_result_top0_5.json' % (experiment, dataset, model, temperature), 'r') as f:
                intermediate_result = json.load(f)

    test_case_pass_rate = []
    OER = []
    OER_ow = []
    LCS = []
    Levenshieten = []
    ask_question_rate = []
    question_quality = []
    # if request_way == 'R1':
    #     Levenshieten.append(intermediate_result['syntatic_similarity']['Levenshtein_edit_distance'])
    for case in intermediate_result:
        # if request_way == 'R1':
        #     OER.append(intermediate_result[case]['syntatic_similarity']['same_output_between_5'])
        #     OER_ow.append(intermediate_result[case]['syntatic_similarity']['same_output_between_5_correct'])
        # else:
        
        #print('case=',case)
        if prompt_type != '' and not case.endswith(prompt_type):
            continue
        OER.append(intermediate_result[case]['syntatic_similarity']['same_output_between_5'])
        OER_ow.append(intermediate_result[case]['syntatic_similarity']['same_output_between_5_correct'])
        Levenshieten.append(intermediate_result[case]['syntatic_similarity']['Levenshtein_edit_distance'])
        test_case_pass_rate.append(intermediate_result[case]['test_case_pass_rate'])
        LCS.append(intermediate_result[case]['LCS'])
        ask_question_rate.append(intermediate_result[case]['ask_question_rate'])
        question_quality.append(intermediate_result[case]['question_quality'])

    # get structural similarity
    United_Diff = []
    Tree_Diff = []

    return test_case_pass_rate, OER, OER_ow, Levenshieten, LCS, United_Diff, Tree_Diff, ask_question_rate, question_quality

def get_boxplot(dataset, prompt_type):
    test_pass_rate, OER, OER_ow, Levenshieten, LCS, United_Diff, Tree_Diff, ask_question_rate, question_quality = semantic_syntactic_structural_similarity(prompt_type)
    
    test_pass_rate_mean = [np.mean(i) for i in test_pass_rate]
    test_pass_rate_var = [np.var(i) for i in test_pass_rate]
    test_pass_rate_max_diff = [max(i) - min(i) for i in test_pass_rate]
    ask_question_rate_mean = [np.mean(i) for i in ask_question_rate]
    ask_question_rate_var = [np.var(i) for i in ask_question_rate]
    ask_question_rate_max_diff = [max(i) - min(i) for i in ask_question_rate]
    question_quality_mean = [np.mean(i) for i in question_quality]
    question_quality_var = [np.var(i) for i in question_quality]
    question_quality_max_diff = [max(i) - min(i) for i in question_quality]
    create_boxplot(test_pass_rate_mean, "Box Plot of Test Pass Rate", dataset, "Mean")
    create_boxplot(test_pass_rate_var, "Box Plot of Test Pass Rate", dataset, "Variance")
    create_boxplot(test_pass_rate_max_diff, "Box Plot of Test Pass Rate", dataset, "Max Diff")
    create_boxplot(ask_question_rate_mean, "Box Plot of Communication Rate", dataset, "Mean")
    create_boxplot(ask_question_rate_var, "Box Plot of Communication Rate", dataset, "Variance")
    create_boxplot(ask_question_rate_max_diff, "Box Plot of Communication Rate", dataset, "Max Diff")
    create_boxplot(question_quality_mean, "Box Plot of Question Quality", dataset, "Mean")
    create_boxplot(question_quality_var, "Box Plot of Question Quality", dataset, "Variance")
    create_boxplot(question_quality_max_diff, "Box Plot of Question Quality", dataset, "Max Diff")

def get_correlation(prompt_type):
    # store all the fine-grained measurement in the dic named correlation (for later draw the heatmap)

    test_pass_rate, OER, OER_ow, Levenshieten, LCS, United_Diff, Tree_Diff, ask_question_rate, question_quality = semantic_syntactic_structural_similarity(prompt_type)
    correlation = {'problem': [],
                   'test pass rate mean': [],
                   'test pass rate variance': [],
                   'test pass rate max diff': [],
                   'description length': [],
                   'difficulty': [],
                   'time_limit': [],
                   'cf_rating': [],
                   'ask question rate mean': [],
                   'ask question rate variance': [],
                   'ask question rate max diff': [],
                   'question quality mean': [],
                   'question quality variance': [],
                   'question quality max diff': [],
                   'pass@k': [],
                   }

    test_pass_rate_var = [np.var(i) for i in test_pass_rate]
    test_pass_rate_var_avg = np.mean(test_pass_rate_var)
    test_pass_rate_max_diff = [max(i) - min(i) for i in test_pass_rate]
    test_pass_rate_max_diff_avg = np.mean(test_pass_rate_max_diff)

    print('sizes')
    print(len(problem_list))
    print(len(test_pass_rate))
    if dataset == 'HumanEvalComm':
        for i in range(len(test_pass_rate)):
            correlation['test pass rate mean'].append(np.mean(test_pass_rate[i]))
            correlation['test pass rate variance'].append(np.var(test_pass_rate[i]))
            correlation['test pass rate max diff'].append(max(test_pass_rate[i])-min(test_pass_rate[i]))
            passPerProblem = 1.0 if (math.isclose(max(test_pass_rate[i]), 1.0)) else 0.0
            correlation['pass@k'].append(passPerProblem)

            correlation['ask question rate mean'].append(np.mean(ask_question_rate[i]))
            correlation['ask question rate variance'].append(np.var(ask_question_rate[i]))
            correlation['ask question rate max diff'].append(max(ask_question_rate[i])-min(ask_question_rate[i]))

            correlation['question quality mean'].append(np.mean(question_quality[i]))
            correlation['question quality variance'].append(np.var(question_quality[i]))
            correlation['question quality max diff'].append(max(question_quality[i])-min(question_quality[i]))

    else:
        for i in range(len(problem_list)):
            problem = problem_list[i]

            if dataset == 'HumanEval':
                correlation['problem'].append(problem['task_id'])
                correlation['description length'].append(len(problem['prompt']))

            elif dataset == 'APPS':
                correlation['problem'].append(problem['name'])
                correlation['description length'].append(len(problem['description']))
            else:
                correlation['problem'].append(problem['name'])
                correlation['description length'].append(len(problem['description']))
                correlation['difficulty'].append(problem['difficulty'])

                pattern = re.compile(r'(?<=seconds:=)*\d+')
                time_limit = pattern.findall(problem['time_limit'].split('\n')[0])[0]
                if 'seconds' in problem['time_limit']:
                    correlation['time_limit'].append(int(time_limit))
                else:
                    correlation['time_limit'].append(3)
                correlation['cf_rating'].append(problem['cf_rating'])
            
            if MAX_NUM_PROBLEMS > 0 and i == MAX_NUM_PROBLEMS:
                break

            correlation['test pass rate mean'].append(np.mean(test_pass_rate[i]))
            correlation['test pass rate variance'].append(np.var(test_pass_rate[i]))
            correlation['test pass rate max diff'].append(max(test_pass_rate[i])-min(test_pass_rate[i]))

            correlation['ask question rate mean'].append(np.mean(ask_question_rate[i]))
            correlation['ask question rate variance'].append(np.var(ask_question_rate[i]))
            correlation['ask question rate max diff'].append(max(ask_question_rate[i])-min(ask_question_rate[i]))

    correlation['OER'] = OER
    correlation['OER_ow'] = OER_ow

    correlation['LCS mean'] = []
    # correlation['LCS variance'] = []
    correlation['LCS min'] = []

    correlation['LED mean'] = []
    # correlation['Levenshieten variance'] = []
    correlation['LED max'] = []

    correlation['United_Diff mean'] = []
    # correlation['United_Diff variance'] = []
    correlation['United_Diff min'] = []

    correlation['Tree_Diff mean'] = []
    # correlation['Tree_Diff variance'] = []
    correlation['Tree_Diff min'] = []

    for case in LCS:
        if case:
            correlation['LCS mean'].append(np.mean(case))
            # correlation['LCS variance'].append(np.var(case))
            correlation['LCS min'].append(min(case))

    for case in Levenshieten:
        if case:
            correlation['LED mean'].append(np.mean(case))
            # correlation['Levenshieten variance'].append(np.var(case))
            correlation['LED max'].append(max(case))

    for case in United_Diff:
        correlation['United_Diff mean'].append(np.mean([i[0] for i in case]))
        # correlation['United_Diff variance'].append(np.var([i[0] for i in case]))
        correlation['United_Diff min'].append(min([i[0] for i in case]))

    for case in Tree_Diff:
        correlation['Tree_Diff mean'].append(np.mean([i[0] for i in case]))
        # correlation['Tree_Diff variance'].append(np.var([i[0] for i in case]))
        correlation['Tree_Diff min'].append(min([i[0] for i in case]))

    return correlation

def store_data_in_xlsx(correlation, file_suffix):
    # store in .xlsx
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    data = [[]]
    data[0].append(np.mean(correlation['test pass rate mean'])) #A
    data[0].append(np.mean(correlation['test pass rate variance'])) #B
    data[0].append(np.mean(correlation['test pass rate max diff'])) #C
    data[0].append(ratio_of_worst(correlation['test pass rate max diff'], 1)) #D

    data[0].append(np.mean(correlation['ask question rate mean'])) #E
    data[0].append(np.mean(correlation['ask question rate variance'])) #F
    data[0].append(np.mean(correlation['ask question rate max diff'])) #G
    data[0].append(ratio_of_worst(correlation['ask question rate max diff'], 1)) #H

    data[0].append(np.mean(correlation['question quality mean'])) #I
    data[0].append(np.mean(correlation['question quality variance'])) #J
    data[0].append(np.mean(correlation['question quality max diff'])) #K
    data[0].append(ratio_of_worst(correlation['question quality max diff'], 1)) #L

    passk = np.mean(correlation['pass@k'])
    print("pass@k is", passk)
    data[0].append(passk) #M

    for row in data:
        sheet.append(row)
    workbook.save('./tables/result_'+file_suffix+'.xlsx')

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
        "-e",
        "--experiment",
        type=str,
        help="Experiment (input file suffix in /result_data)",
        required=True,
    )
    parser.add_argument(
        "-t",
        "--temperature",
        type=str,
        help="Set the temperature",
        required=True,
    )
    parser.add_argument(
        "-pt",
        "--prompt_type",
        type=str,
        choices=['', 'prompt1a', 'prompt1c', 'prompt1p', 'prompt2ac','prompt2ap','prompt2cp','prompt3acp'],
        help="output results for a certain prompt type if not empty",
        default='',
    )
    args = parser.parse_args()

    for i in range(1):
        print(i)
        # config (change to apply)
        dataset_ = ['code_contest', 'APPS', 'HumanEval']
        # dataset_* is removed, so experiment = e.g. randRemove_50
        #experiment_ = ['dataset_HumanEval', 'randRemove_30_dataset_HumanEval', 'randRemove_50_dataset_HumanEval', 'randRemove_90_dataset_HumanEval']
        experiment_ = ['randRemove_50_dataset_HumanEval']
        request_way_ = ['R1', 'R2']
        request_way = request_way_[0]
        #temperature_ = [1,1,1,1]
        temperature_ = [1]
        problem_list = []
        # customized
        file_path = './result_data'
        # gpt-3.5-turbo or gpt-4
        #model = 'gpt-3.5-turbo' 'gpt-4' 'comm'

        experiment = args.experiment
        dataset = args.dataset
        temperature = args.temperature
        model = args.model
        topn = args.topn
        prompt_type = args.prompt_type

        if dataset == 'code_contest':
            # with open('./tmp2/code_contests_test.json', 'r') as f:
            with open('./dataset/code_contests_test.json', 'r') as f:
                problem_list = json.load(f)
        elif dataset == 'HumanEval' or dataset == 'HumanEvalComm':
            with open('./HumanEval/HumanEval.jsonl', 'r') as f:
                for line in f.readlines():
                    problem_list.append(json.loads(line))
        elif dataset == 'APPS':
            path = './APPS/test/'
            for dirpath, dirnames, filenames in os.walk(path):
                # iterating for every problem
                for dirname in dirnames[:500]:
                    # description
                    with open(path + dirname + '/question.txt', 'r', encoding='utf-8') as f:
                        description = f.read()
                    problem_list.append({'name': dirname, 'description': description})

        correlation = get_correlation(prompt_type)
        output_file = '%s_dataset_%s_model_%s_topn_%s_temperature_%s%s' % \
                   (experiment, dataset, model, topn, temperature, prompt_type)
        store_data_in_xlsx(correlation, output_file)
        #get_boxplot(dataset, prompt_type)
