import json
import re
import pycode_similar
import os

def summarize(func_ast_diff_list):
    sum_total_count = sum(func_diff_info.total_count for func_diff_info in func_ast_diff_list)
    sum_plagiarism_count = sum(func_diff_info.plagiarism_count for func_diff_info in func_ast_diff_list)
    if sum_total_count == 0:
        sum_plagiarism_percent = 0
    else:
        sum_plagiarism_percent = sum_plagiarism_count / float(sum_total_count)
    return sum_plagiarism_percent, sum_plagiarism_count, sum_total_count

def modify_code(code):
    prefix = 'def main():\n'
    tab = '    '
    sufix = '\n\nif __name__ == "__main__":\n' + tab + 'main()'
    code_list = code.split('\n')
    code_list = [tab + i for i in code_list]
    res_0 = '\n'.join(i for i in code_list)
    res = prefix + res_0 + sufix
    return res

def structual_similarity(problem_dic, name, code_reference):
    # code_reference = [referenced_code_str, candidate_code_str1, candidate_code_str2, ...]
    if code_reference[0] == '':
        problem_dic[name]['structual_similarity'] = {
            'structual_similarity_UnifiedDiff': [-1, -1, -1, -1],
            'structual_similarity_TreeDiff': [-1, -1, -1, -1]
        }
        return
    try:
        results_UnifiedDiff = pycode_similar.detect(code_reference,
                                    diff_method=pycode_similar.UnifiedDiff, keep_prints=True, module_level=False)
    except pycode_similar.NoFuncException:
        # code_reference[0] = modify_code(code_reference[0])
        for i in range(5):
            if "__main__" not in code_reference[i]:
                code_reference[i] = modify_code(code_reference[i])
        try:
            results_UnifiedDiff = pycode_similar.detect(code_reference,
                                                        diff_method=pycode_similar.UnifiedDiff, keep_prints=True,
                                                        module_level=False)
        except Exception as e:
            problem_dic[name]['structual_similarity'] = {
                'structual_similarity_UnifiedDiff': [-2, -2, -2, -2],
                'structual_similarity_TreeDiff': [-2, -2, -2, -2]
            }
            return
    except Exception as e:
        problem_dic[name]['structual_similarity'] = {
            'structual_similarity_UnifiedDiff': [-2, -2, -2, -2],
            'structual_similarity_TreeDiff': [-2, -2, -2, -2]
        }
        return


    try:
        results_TreeDiff = pycode_similar.detect(code_reference,
                                                 diff_method=pycode_similar.TreeDiff, keep_prints=True,
                                                 module_level=False)
    except pycode_similar.NoFuncException:
        # code_reference[0] = modify_code(code_reference[0])
        for i in range(5):
            if "__main__" not in code_reference[i]:
                code_reference[i] = modify_code(code_reference[i])
        try:
            results_TreeDiff = pycode_similar.detect(code_reference,
                                                     diff_method=pycode_similar.TreeDiff, keep_prints=True,
                                                     module_level=False)
        except Exception as e:
            problem_dic[name]['structual_similarity'] = {
                'structual_similarity_UnifiedDiff': [-3, -3, -3, -3],
                'structual_similarity_TreeDiff': [-3, -3, -3, -3]
            }
            print(e)
            return

    except Exception as e:
        problem_dic[name]['structual_similarity'] = {
            'structual_similarity_UnifiedDiff': [-3, -3, -3, -3],
            'structual_similarity_TreeDiff': [-3, -3, -3, -3]
        }
        print(e)
        return
    structual_similarity_UnifiedDiff = []
    structual_similarity_TreeDiff = []
    for index, func_ast_diff_list in results_UnifiedDiff:
        sum_similarity_percent, sum_similarity_count, sum_total_count = summarize(func_ast_diff_list)
        structual_similarity_UnifiedDiff.append([sum_similarity_percent, sum_similarity_count, sum_total_count])

    for index, func_ast_diff_list in results_TreeDiff:
        sum_similarity_percent, sum_similarity_count, sum_total_count = summarize(func_ast_diff_list)
        structual_similarity_TreeDiff.append([sum_similarity_percent, sum_similarity_count, sum_total_count])
    problem_dic[name]['structual_similarity'] = {
        'structual_similarity_UnifiedDiff': structual_similarity_UnifiedDiff,
        'structual_similarity_TreeDiff': structual_similarity_TreeDiff
    }

def response_2_code(response):
    code_template = re.compile('```.*\n([\s\S]+?)\n```', re.M)
    code = code_template.findall(response)
    if len(code) > 0:
        return code[-1]
    else:
        return ''

if __name__ == "__main__":
    # config
    # 'APPS','code_contest',  'HumanEval'
    # dataset_ = ['code_contest','APPS', 'HumanEval']
    dataset_ = ['HumanEval']
    # 0, 1, 2
    temperature_ = [0, 1]
    # R1, R2
    request_way = 'R1'
    model = 'gpt-4'

    # main logic
    for dataset in dataset_:
        for temperature in temperature_:
            print('----------------------------------------', flush=True)
            print('Dataset: %s, temperature: %s' % (dataset, temperature), flush=True)
            print('----------------------------------------', flush=True)
            save_dir = './result_data/structural_similarity/'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            # save_dir = './structural_similarity/'
            problem_dic = {}
            with open('./log/dataset_%s_model_%s_topn_5_temperature_%s.0.log_%s' % (dataset, model, temperature, 0), 'r') as f:
                for line in f.readlines():
                    tmp = json.loads(line)
                    problem_dic[tmp['name']] = {'code_list':[]}

            length = len(problem_dic)
            code_list = []
            if request_way == "R1":
                with open('./log/dataset_%s_model_%s_topn_5_temperature_%s.0.log_%s' % (dataset, model, temperature, 0),
                          'r') as f:
                    for line in f.readlines():
                        tmp = json.loads(line)
                        problem_dic[tmp['name']]['code_list'].append(response_2_code(tmp['response']))
            elif request_way == "R2":
                for i in range(5):
                    with open('./log/dataset_%s_model_%s_topn_5_temperature_%s.0.log_%s' % (dataset, model, temperature, i), 'r') as f:
                        for line in f.readlines():
                            tmp = json.loads(line)
                            if tmp['index'] == 0:
                                problem_dic[tmp['name']]['code_list'].append(response_2_code(tmp['response']))

            for key in problem_dic:
                print('problem: %s' % (key), flush=True)
                structual_similarity(problem_dic, key, problem_dic[key]['code_list'])
                problem_dic[key].pop('code_list')

            json_str = json.dumps(problem_dic)
            if request_way == "R1":
                with open(save_dir+'%s_%s_structual_similarity_among5.json' % (dataset, temperature), 'w') as f:
                    f.write(json_str)
            elif request_way == "R2":
                with open(save_dir+'%s_%s_structual_similarity_top0_5.json' % (dataset, temperature), 'w') as f:
                    f.write(json_str)