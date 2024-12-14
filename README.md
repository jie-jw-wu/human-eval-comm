
# HumanEvalComm: Evaluating the Communication Skill of Code LLMs and LLM Agent
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg?style=flat-square)
[![Research Paper](https://img.shields.io/badge/Paper-brightgreen.svg?style=flat-square)](https://arxiv.org/abs/2406.00215)
[![Huggingface Dataset](https://img.shields.io/badge/Dataset-blue.svg?style=flat-square)](https://huggingface.co/datasets/)

## Dataset Description

HumanEvalComm is a benchmark dataset for evaluating the communication skills of Large Language Models (LLMs) in code generation tasks. It is built upon the widely used [HumanEval benchmark](https://github.com/openai/human-eval) and focuses on evaluating the degree of communication skills when generating code.

HumanEvalComm modifies the original problem descriptions in the HumanEval dataset to trigger clarifying questions, which are necessary to generate the correct code. This modification is done using a taxonomy of clarification types: Ambiguity, Inconsistency, and Incompleteness.
- Ambiguity: Statements in the problem descriptions are modified to have multiple interpretations. For example, changing "sort the array descendingly" to "sort the array (descendingly or ascendingly)".
- Inconsistency: Modifications are made to create contradictions between the problem description and examples. For instance, changing the output of test examples to contradict the provided textual description.
- Incompleteness: Parts of the problem description are removed to make it incomplete, requiring the model to ask questions to recover the missing content.

HumanEvalComm contains 762 modified problem descriptions based on the 164 problems in the HumanEval dataset. The modifications are created by applying one or a combination of the aforementioned clarification types. Each modified problem description is manually verified to ensure it triggers clarifying questions. The goal of HumanEvalComm is to evaluate the ability of LLMs to ask clarifying questions when faced with incomplete, inconsistent, or ambiguous requirements in coding problems.

## Evaluation on HumanEvalComm

Large language models (LLMs) have significantly improved their ability to perform tasks in the field of code generation. However, there is still a gap between LLMs being capable coders and being top-tier software engineers. The most recent trends involve using LLM-based agents to iterate the code generation process.
Based on the observation that top-level software engineers often ask clarifying questions to reduce *Ambiguity* in both requirements and coding solutions, we argue that the same should be applied to LLMs for code generation tasks. For this purpose, we define the communication skills of LLMs as "being able to ask clarifying questions when the description of the code generation problem has issues." In this study, we restrict these issues to three matters from the software requirement engineering field: inconsistent requirements, ambiguous requirements, and incomplete requirements. By asking probing questions about the requirements of problem descriptions before generating the final code, the challenges of programming with LLMs, such as unclear intent specification, may be alleviated, resulting in correct code in the initial iterations.


In this work, we conducted an empirical study on the benchmark and analysis of the communication skills of LLMs for code generation. We created a new benchmark, HumanEvalComm, by modifying problem descriptions according to three issues mentioned above: *Inconsistency*, *Ambiguity*, and *Incompleteness*. We then experimented on HumanEvalComm with different Code LLMs and a new LLM agent approach, **C<ins>o</ins>de <ins>C</ins>l<ins>a</ins>rificatio<ins>n</ins> <ins>a</ins>nd <ins>G</ins>eneration <ins>A</ins>ge<ins>n</ins>t (Okanagan)**, to identify and ask questions in ambiguous parts of code and descriptions for further refining the generated code.
In the evaluation, we introduced an *LLM-based evaluator* and created *Communication Rate* and *Good Question Rate* as the evaluation metrics to represent the ratio of questions asked and questions with good quality in responses. We found that more than 60% of responses from Code LLMs still generate code rather than ask questions when the problem descriptions are manually modified according to different clarification categories.
The Pass@1 and Test Pass Rate of most Code LLMs drop by 35% to 52% and by 17% to 35% respectively, with statistical significance in each category for over 75% numbers. Okanagan, as an LLM agent approach that uses LLMs such as ChatGPT 3.5, effectively increases the Communication Rate and Good Question Rate by an absolute 58% and 38% respectively, and thus boosts Pass@1 and Test Pass Rate by an absolute 8% and 7% respectively, when the problem descriptions are modified based on given clarification categories. This indicates the potential for achieving more effective communication capability using the LLM agent.



<img width="1501" alt="HumanEvalComm" src="https://github.com/jie-jw-wu/human-eval-comm/assets/122728498/9a7d2142-7ac5-4f64-8557-225e8b221dc7">

## Run
The main script to run the evaluation is `./scripts/script_stepwise_phase123.bat`. Below is the command:
```bash
./scripts/script_stepwise_phase123.bat {models} {phase} {starting_problem_num} {ending_problem_num}
```
`{phase}` defines the phase to be executed in the evaluation. Below are the values of `phase` in the evaluation:
- 0: run models to get the initial response for either HumanEvalComm or HumanEval. output: file in log/
- 1: the initial responses are evaluated by the LLM-based evaluator (for HumanEvalComm only). output: file in log/
- 2: run models again to get the 2nd response based on LLM-based evaluator output (for HumanEvalComm only). output: file in log/
- 3: extract code and run test cases and other metrics for each problem. input: file in log/  output: file in log/record/
- 4: compute more metrics for each problem, such as test pass rate, question quality rate, comm. rate, etc. input: file in ./log/record/ output: file in ./result_data/
- 5: aggregate and display metrics for all problems. output: files in table/
- 6: aggregate and display metrics for each clarification category for all problems. output: files in table/ 

Here are some examples:
```bash
#phase 1:
    ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat Meta-Llama-3-8B-Instruct CodeLlama-13b-Instruct-hf" 1 0 165
#phase 1:
    ./scripts/script_stepwise_phase123.bat "gpt-3.5-turbo-0125 Okanagan" 0 0 5 HumanEval
#phase 2:
    ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat CodeLlama-13b-Instruct-hf CodeQwen1.5-7B-Chat" 1 0 165
#analyze remaining open models:
    ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat CodeLlama-13b-Instruct-hf" 3
    ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat CodeLlama-13b-Instruct-hf" 4
    ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat CodeLlama-13b-Instruct-hf" 5
    ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat CodeLlama-13b-Instruct-hf" 6
#run original problem without modification:
    ./scripts/script_stepwise_phase123.bat "gpt-3.5-turbo-0125 Okanagan" 0 0 165 HumanEval
    ./scripts/script_stepwise_phase123.bat "gpt-3.5-turbo-0125 Okanagan" 3-1 0 165 HumanEval
    ./scripts/script_stepwise_phase123.bat "gpt-3.5-turbo-0125 Okanagan" 4-1 0 165 HumanEval
    ./scripts/script_stepwise_phase123.bat "gpt-3.5-turbo-0125 Okanagan" 5-1 0 165 HumanEval
#phase 5:
    ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat CodeLlama-13b-Instruct-hf CodeLlama-7b-Instruct-hf gpt-3.5-turbo-0125 Okanagan" 5

```

In this work, for open-source models in phase 0-2, we run sockeye scripts (./scripts/sockeye_scripts/*.sh) to run model inferences in Sockeye (https://arc.ubc.ca/compute-storage/ubc-arc-sockeye), due to resource limitations of the authors' desktop.

## Acknowledgements
This code is heavily influenced by the Nondeterminism evaluation research of ChatGPT (https://github.com/CodeHero0/Nondeterminism-of-ChatGPT-in-Code-Generation), and by IdentityChain(https://github.com/marcusm117/IdentityChain/tree/main) on testing models including StarCoderBase and CodeLlama.

## Reference
Please consider citing this paper if you find this useful: 

Wu, Jie JW, and Fatemeh H. Fard. "Benchmarking the Communication Competence of Code Generation for LLMs and LLM Agent." arXiv preprint arXiv:2406.00215 (2024).

```
@article{wu2024benchmarking,
  title={Benchmarking the Communication Competence of Code Generation for LLMs and LLM Agent},
  author={Wu, Jie JW and Fard, Fatemeh H},
  journal={arXiv preprint arXiv:2406.00215},
  year={2024}
}
```
