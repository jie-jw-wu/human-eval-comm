import argparse
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import nltk
import os
import tokenize
import scipy.stats as stats
from nltk.translate.bleu_score import sentence_bleu
from difflib import SequenceMatcher

def get_ask_question_rate(input_string):
    if len(input_string) == 0:
        return 1
    else:
        return 0

def get_ask_question_rate_with_qq(question_quality):
    if question_quality <= 1:
        return 0
    else:
        return 1

def analyze_among_top0_5(experiment, model, temperature):
    save_dir = './result_data/%s_%s_%s/' % (experiment, model, temperature)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    def syntatic_similarity(problem_dic, name, code_candidates, case_status_list):
        same_output_between_5 = []
        same_output_between_5_correct = []
        same_output_between_5_timeout = []
        same_output_between_5_exception = []
        same_output_between_5_execution_error = []
        Levenshtein_edit_distance = []
        for i in range(len(case_status_list[0])):
            output_set = set()
            for j in range(len(problem_dic[name]['code_candidates'])):
                output_set.add(case_status_list[j][i])
            # print(output_set)
            if len(output_set) == 1:
                same_output_between_5.append(i)
                if list(output_set)[0] == 'timeout':
                    same_output_between_5_timeout.append(i)
                elif 'execution error' in list(output_set)[0]:
                    same_output_between_5_execution_error.append(i)
                elif list(output_set)[0] == 'exception' or sum([len(case) for case in code_candidates]) == 0:
                    same_output_between_5_exception.append(i)
                else:
                    same_output_between_5_correct.append(i)

        for i in range(len(problem_dic[name]['code_candidates'])):
            if i == 0:
                continue
            Levenshtein_edit_distance.append(nltk.edit_distance(code_candidates[0], code_candidates[i]))
        problem_dic[name]['syntatic_similarity'] = {
            'same_output_between_5': same_output_between_5,
            'same_output_between_5_correct': same_output_between_5_correct,
            'same_output_between_5_timeout': same_output_between_5_timeout,
            'same_output_between_5_exception': same_output_between_5_exception,
            'same_output_between_5_execution_error': same_output_between_5_execution_error,
            'Levenshtein_edit_distance': Levenshtein_edit_distance
        }
        total_test_case_num = len(problem_dic[name]['code_candidates'][0]['case_status'])
        if total_test_case_num == 0:
            syntatic_similarity_res = {
                'same_output_between_5': 0,
                'same_output_between_5_correct': 0,
                'same_output_between_5_timeout': 0,
                'same_output_between_5_exception': 0,
                'same_output_between_5_execution_error': 0,
                'Levenshtein_edit_distance': Levenshtein_edit_distance
            }
        else:
            syntatic_similarity_res = {
                'same_output_between_5': len(problem_dic[name]['syntatic_similarity']['same_output_between_5']) / total_test_case_num,
                'same_output_between_5_correct': len(problem_dic[name]['syntatic_similarity']['same_output_between_5_correct']) / total_test_case_num,
                'same_output_between_5_timeout': len(problem_dic[name]['syntatic_similarity']['same_output_between_5_timeout']) / total_test_case_num,
                'same_output_between_5_exception': len(problem_dic[name]['syntatic_similarity']['same_output_between_5_exception']) / total_test_case_num,
                'same_output_between_5_execution_error': len(problem_dic[name]['syntatic_similarity']['same_output_between_5_execution_error']) / total_test_case_num,
                'Levenshtein_edit_distance': Levenshtein_edit_distance
            }
        return syntatic_similarity_res

    def LCS(list1, list2):
        matcher = SequenceMatcher(None, list1, list2)
        match = matcher.find_longest_match(0, len(list1), 0, len(list2))
        return list1[match.a: match.a + match.size]

    def test_case_pass_rate_top5(code_candidates):
        # test_case_pass_rate = []
        tmp_test_case_pass_rate = []

        #  BLEU score with correct solution as reference
        tmp_list = []
        for code in code_candidates:
            if len(code['case_status'])!=0:
                tmp_test_case_pass_rate.append(float(len(code['passed_case']) / (len(code['case_status']))))
            else:
                tmp_test_case_pass_rate.append(float(0))
        # test_case_pass_rate.append(tmp_test_case_pass_rate)
        return tmp_test_case_pass_rate

    problem_dic = {}
    for seq in range(5):
        with open('log/record/%s_model_%s_topn_5_temperature_%s.0.log_%s' % (experiment, model, temperature, seq), 'r') as f:
            for line in f.readlines():
                content = json.loads(line)
                name = content['name']
                if name not in problem_dic:
                    problem_dic[name] = {'code_candidates': []}
                index_num = content['index_num']
                code_candidates = content['code_candidates']
                code = code_candidates[0]
                problem_dic[name]['code_candidates'].append(code)

                if seq == 4:
                    code_candidates = []
                    code_reference = []
                    case_status_list = []
                    ask_question_rate = []
                    for code_res in problem_dic[name]['code_candidates']:
                        code_candidates.append(code_res['code'].split())
                        code_reference.append(code_res['code'])
                        case_status_list.append(code_res['case_status'])
                        ask_question_rate.append(get_ask_question_rate(code_res['code']))
                    # output equivalence rate
                    test_case_pass_rate = test_case_pass_rate_top5(problem_dic[name]['code_candidates'])
                    syntatic_similarity_res = syntatic_similarity(problem_dic, name, code_candidates, case_status_list)
                    problem_dic[name]['syntatic_similarity'] = syntatic_similarity_res
                    # LCS
                    LCS_list = []
                    for i in range(1, len(code_candidates)):
                        # BLEU score among 5 code candidates
                        # the first one is important
                        if len(code_candidates[0])!=0:
                            LCS_rate = len(LCS(code_candidates[0], code_candidates[i]))/len(code_candidates[0])
                        else:
                            LCS_rate = 0
                        LCS_list.append(LCS_rate)
                    problem_dic[name]['test_case_pass_rate'] = test_case_pass_rate
                    problem_dic[name]['LCS'] = LCS_list
                    problem_dic[name]['ask_question_rate'] = ask_question_rate
                    problem_dic[name].pop('code_candidates')
    json_str = json.dumps(problem_dic)
    with open(save_dir+'intermediate_result_top0_5.json', 'w') as f:
        f.write(json_str)

def analyze_among_among5(experiment, model, temperature, topn, log_phase):
    save_dir = './result_data/%s_%s_%s/' % (experiment, model, temperature)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    def syntatic_similarity(problem_dic, name, code_candidates, case_status_list):
        same_output_between_5 = []
        same_output_between_5_correct = []
        same_output_between_5_timeout = []
        same_output_between_5_exception = []
        same_output_between_5_execution_error = []
        Levenshtein_edit_distance = []
        for i in range(len(case_status_list[0])):
            output_set = set()
            for j in range(len(problem_dic[name]['code_candidates'])):
                output_set.add(case_status_list[j][i])
            # print(output_set)
            if len(output_set) == 1:
                same_output_between_5.append(i)
                if list(output_set)[0] == 'timeout':
                    same_output_between_5_timeout.append(i)
                elif 'execution error' in list(output_set)[0]:
                    same_output_between_5_execution_error.append(i)
                elif list(output_set)[0] == 'exception' or sum([len(case) for case in code_candidates]) == 0:
                    same_output_between_5_exception.append(i)
                else:
                    same_output_between_5_correct.append(i)

        for i in range(len(problem_dic[name]['code_candidates'])):
            if i == 0:
                continue
            Levenshtein_edit_distance.append(nltk.edit_distance(code_candidates[0], code_candidates[i]))
        problem_dic[name]['syntatic_similarity'] = {
            'same_output_between_5': same_output_between_5,
            'same_output_between_5_correct': same_output_between_5_correct,
            'same_output_between_5_timeout': same_output_between_5_timeout,
            'same_output_between_5_exception': same_output_between_5_exception,
            'same_output_between_5_execution_error': same_output_between_5_execution_error,
            'Levenshtein_edit_distance': Levenshtein_edit_distance
        }
        total_test_case_num = len(problem_dic[name]['code_candidates'][0]['case_status'])
        if total_test_case_num == 0:
            syntatic_similarity_res = {
                'same_output_between_5': 0,
                'same_output_between_5_correct': 0,
                'same_output_between_5_timeout': 0,
                'same_output_between_5_exception': 0,
                'same_output_between_5_execution_error': 0,
                'Levenshtein_edit_distance': Levenshtein_edit_distance
            }
        else:
            syntatic_similarity_res = {
                'same_output_between_5': len(problem_dic[name]['syntatic_similarity']['same_output_between_5']) / total_test_case_num,
                'same_output_between_5_correct': len(problem_dic[name]['syntatic_similarity']['same_output_between_5_correct']) / total_test_case_num,
                'same_output_between_5_timeout': len(problem_dic[name]['syntatic_similarity']['same_output_between_5_timeout']) / total_test_case_num,
                'same_output_between_5_exception': len(problem_dic[name]['syntatic_similarity']['same_output_between_5_exception']) / total_test_case_num,
                'same_output_between_5_execution_error': len(problem_dic[name]['syntatic_similarity']['same_output_between_5_execution_error']) / total_test_case_num,
                'Levenshtein_edit_distance': Levenshtein_edit_distance
            }
        return syntatic_similarity_res

    def LCS(list1, list2):
        matcher = SequenceMatcher(None, list1, list2)
        match = matcher.find_longest_match(0, len(list1), 0, len(list2))
        return list1[match.a: match.a + match.size]

    def test_case_pass_rate_among5(code_candidates):
        # test_case_pass_rate = []
        tmp_test_case_pass_rate = []

        #  BLEU score with correct solution as reference
        tmp_list = []
        for code in code_candidates:
            if len(code['case_status'])!=0:
                tmp_test_case_pass_rate.append(float(len(code['passed_case']) / (len(code['case_status']))))
            else:
                tmp_test_case_pass_rate.append(float(0))
        # test_case_pass_rate.append(tmp_test_case_pass_rate)
        return tmp_test_case_pass_rate

    problem_dic = {}
    with open('log/record/%s_model_%s_topn_%s_temperature_%s.0.log_%s' % (experiment, model, topn, temperature, log_phase), 'r') as f:
        for line in f.readlines():
            content = json.loads(line)
            name = content['name']
            if name not in problem_dic:
                problem_dic[name] = {'code_candidates': []}
            code_candidates = content['code_candidates']
            # code = code_candidates[0]
            for code in code_candidates:
                #print('debug:')
                #print(name)
                #print(problem_dic[name])
                problem_dic[name]['code_candidates'].append(code)

            code_candidates = []
            code_reference = []
            case_status_list = []
            ask_question_rate = []
            question_quality = []
            for code_res in problem_dic[name]['code_candidates']:
                qq = int(code_res['question_quality'])
                code_candidates.append(code_res['code'].split())
                code_reference.append(code_res['code'])
                case_status_list.append(code_res['case_status'])
                ask_question_rate.append(get_ask_question_rate_with_qq(qq)) 
                question_quality.append(qq)
            test_case_pass_rate = test_case_pass_rate_among5(problem_dic[name]['code_candidates'])
            syntatic_similarity_res = syntatic_similarity(problem_dic, name, code_candidates, case_status_list)
            problem_dic[name]['syntatic_similarity'] = syntatic_similarity_res
            # LCS
            LCS_list = []
            for i in range(1, len(code_candidates)):
                # BLEU score among 5 code candidates
                # the first one is important
                if len(code_candidates[0])!=0:
                    LCS_rate = len(LCS(code_candidates[0], code_candidates[i]))/len(code_candidates[0])
                else:
                    LCS_rate = 0
                LCS_list.append(LCS_rate)
            problem_dic[name]['test_case_pass_rate'] = test_case_pass_rate
            problem_dic[name]['LCS'] = LCS_list
            problem_dic[name]['ask_question_rate'] = ask_question_rate
            problem_dic[name]['question_quality'] = question_quality
            problem_dic[name].pop('code_candidates')

        json_str = json.dumps(problem_dic)
        with open(save_dir+'intermediate_result_among5.json', 'w') as f:
            f.write(json_str)

# input: file in ./log/record/
# output: file in ./result_data/
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--experiment",
        type=str,
        help="Choose experiment",
        required=True,
    )
    # 0, 1, 2
    parser.add_argument(
        "-t",
        "--temperature",
        type=str,
        help="Choose temperature",
        required=True,
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-o",
        "--option",
        type=str,
        choices=['R1', 'R2'],
        help="Choose the mode of the experiment",
        required=True,
        # default='original'
    )
    parser.add_argument(
        "-n",
        "--topn",
        type=int,
        help="Top N candidates",
        default=5,
    )

    parser.add_argument(
        "-s", # legacy
        "--log_phase_input",
        choices=[0,1,2,3],
        type=int,
        help="If not 0, this split the process into phase 1 (1st round LLM response),2 (2nd, answers to questions),3 (3rd, final code generation given chat history). This is name of input log file",
        default=0
    )

    args = parser.parse_args()
    if args.option == 'R1':
        analyze_among_among5(args.experiment, args.model, args.temperature, args.topn, args.log_phase_input)
    elif args.option == 'R2':
        analyze_among_top0_5(args.experiment, args.model, args.temperature)

