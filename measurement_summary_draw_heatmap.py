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
    return (count/len(list))

def semantic_syntactic_structural_similarity():
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

def get_boxplot(dataset):
    test_pass_rate, OER, OER_ow, Levenshieten, LCS, United_Diff, Tree_Diff, ask_question_rate, question_quality = semantic_syntactic_structural_similarity()
    
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

def get_correlation():
    # store all the fine-grained measurement in the dic named correlation (for later draw the heatmap)

    test_pass_rate, OER, OER_ow, Levenshieten, LCS, United_Diff, Tree_Diff, ask_question_rate, question_quality = semantic_syntactic_structural_similarity()
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
    data[0].append(np.mean(correlation['test pass rate mean']))
    data[0].append(np.mean(correlation['test pass rate variance']))
    data[0].append(np.mean(correlation['test pass rate max diff']))
    data[0].append(ratio_of_worst(correlation['test pass rate max diff'], 1))

    data[0].append(np.mean(correlation['ask question rate mean']))
    data[0].append(np.mean(correlation['ask question rate variance']))
    data[0].append(np.mean(correlation['ask question rate max diff']))
    data[0].append(ratio_of_worst(correlation['ask question rate max diff'], 1))

    data[0].append(np.mean(correlation['question quality mean']))
    data[0].append(np.mean(correlation['question quality variance']))
    data[0].append(np.mean(correlation['question quality max diff']))
    data[0].append(ratio_of_worst(correlation['question quality max diff'], 1))

    passk = np.mean(correlation['pass@k'])
    print("pass@k is", passk)
    data[0].append(passk)

    for row in data:
        sheet.append(row)
    workbook.save('./tables/result_'+file_suffix+'.xlsx')

def draw_heatmap(correlation, save_dir):
    correlation_rank = []
    high_relavent = []
    problem_features = ['description length', 'difficulty', 'time_limit', 'cf_rating']
    for case in correlation_rank:
        if (case[0] in problem_features or case[1] in problem_features) and case[2][1] < 0.05:
            high_relavent.append(case)
            # print('%s & %s\'s correlation: %s' % (list(correlation.keys())[i],
            #                                       list(correlation.keys())[j],
            #                                       stats.pearsonr(correlation[list(correlation.keys())[i]], correlation[list(correlation.keys())[j]])
            #                                       )
            #       )
    correlation_list = []
    # test pass rate
    correlation_list.append(correlation['test pass rate mean'])
    correlation_list.append(correlation['test pass rate variance'])
    correlation_list.append(correlation['test pass rate max diff'])
    # output equivalence rate
    correlation_list.append(correlation['OER'])
    correlation_list.append(correlation['OER_ow'])
    # LCS
    correlation_list.append(correlation['LCS mean'])
    # correlation_list.append(correlation['LCS variance'])
    correlation_list.append(correlation['LCS min'])
    # Levenshieten
    correlation_list.append(correlation['LED mean'])
    # correlation_list.append(correlation['Levenshieten variance'])
    correlation_list.append(correlation['LED max'])
    # United_Diff
    correlation_list.append(correlation['United_Diff mean'])
    # correlation_list.append(correlation['United_Diff variance'])
    correlation_list.append(correlation['United_Diff min'])
    # Tree_Diff
    correlation_list.append(correlation['Tree_Diff mean'])
    # correlation_list.append(correlation['Tree_Diff variance'])
    correlation_list.append(correlation['Tree_Diff min'])
    # problem features
    correlation_list.append(correlation['description length'])
    if dataset == 'code_contest':
        correlation_list.append(correlation['difficulty'])
        correlation_list.append(correlation['time_limit'])
        correlation_list.append(correlation['cf_rating'])

    if dataset == 'code_contest':
        column_names = ['TPR mean value',
                        'TPR mean variance',
                        'TPR mean max diff',

                        'OER mean',
                        'OER (no ex.) mean',

                        'LCS mean',
                        'LCS worst',

                        'LED mean',
                        'LED worst',

                        'United_Diff mean',
                        'United_Diff worst',

                        'Tree_Diff mean',
                        'Tree_Diff worst',

                        'description length',
                        'difficulty',
                        'time_limit',
                        'cf_rating'
                        ]
    else:
        column_names = ['TPR mean value',
                        'TPR mean variance',
                        'TPR mean max diff',

                        'OER mean',
                        'OER_ow mean',

                        'LCS mean',
                        'LCS worst',

                        'LED mean',
                        'LED worst',

                        'United_Diff mean',
                        'United_Diff worst',

                        'Tree_Diff mean',
                        'Tree_Diff worst',

                        'description length'
                        ]

    p_values = []
    correlation_values = []
    empty_values = []
    for i in range(len(column_names)):
        p_tmp = []
        c_tmp = []
        e_tmp = []
        for j in range(len(column_names)):
            p_tmp.append(stats.pearsonr(correlation_list[i], correlation_list[j])[1])
            c_tmp.append(stats.pearsonr(correlation_list[i], correlation_list[j])[0])
            e_tmp.append(0)
        p_values.append(p_tmp)
        correlation_values.append(c_tmp)
        empty_values.append(e_tmp)

    for i in range(len(column_names)):
        for j in range(len(column_names)):
            if p_values[i][j] > 0.05:
                empty_values[i][j] = '-'
            else:
                empty_values[i][j] = round(correlation_values[i][j], 2)


    fig, ax = plt.subplots(figsize=(20, 20))
    fig.subplots_adjust(top=0.98, bottom=0.18, left=0.18)
    p1 = sns.heatmap(correlation_values, annot=empty_values, cmap='Greys',
                     xticklabels=column_names, yticklabels=column_names, annot_kws={"fontsize": 18}, fmt='')

    cbar = p1.collections[0].colorbar
    # Set the font size of the color bar labels
    cbar.ax.tick_params(labelsize=20)
    #
    p1.set_xticklabels(p1.get_xticklabels(), fontsize=25)
    p1.tick_params(axis='y', labelsize=25)

    # plt.show()
    plt.savefig(save_dir + 'heatmap_metric.pdf')

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


        correlation = get_correlation()
        output_file = '%s_dataset_%s_model_%s_topn_%s_temperature_%s' % \
                   (experiment, dataset, model, topn, temperature)
        store_data_in_xlsx(correlation, output_file)
        get_boxplot(dataset)
        #draw_heatmap(correlation, './')
