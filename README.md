
# HumanEvalComm: Benchmarking the Communication Skills of Code Generation for LLMs and LLM Agent

<div align="center">

<a href='https://huggingface.co/datasets/jie-jw-wu/HumanEvalComm'>
<img src="https://github.com/user-attachments/assets/3f62b151-d08f-4641-8d10-cc53024ec2c4" alt="HumanEvalComm" height=300></img>
</a>
<br></br>

![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg?style=flat-square)
[![Research Paper](https://img.shields.io/badge/Paper-brightgreen.svg?style=flat-square)](https://arxiv.org/abs/2406.00215)
[![Huggingface Dataset](https://img.shields.io/badge/Dataset-blue.svg?style=flat-square)](https://huggingface.co/datasets/jie-jw-wu/HumanEvalComm)
</div>

## Dataset Description

HumanEvalComm is a benchmark dataset for evaluating the communication skills of Large Language Models (LLMs) in code generation tasks. It is built upon the widely used [HumanEval benchmark](https://github.com/openai/human-eval). HumanEvalComm contains 762 modified problem descriptions based on the 164 problems in the HumanEval dataset. The modifications are created by applying one or a combination of the aforementioned clarification types. Each modified problem description is manually verified to ensure it triggers clarifying questions. The goal of HumanEvalComm is to evaluate the ability of LLMs to ask clarifying questions when faced with incomplete, inconsistent, or ambiguous requirements in coding problems:
- Ambiguity: Statements in the problem descriptions are modified to have multiple interpretations. For example, changing "sort the array descendingly" to "sort the array (descendingly or ascendingly)".
- Inconsistency: Modifications are made to create contradictions between the problem description and examples. For instance, changing the output of test examples to contradict the provided textual description.
- Incompleteness: Parts of the problem description are removed to make it incomplete, requiring the model to ask questions to recover the missing content.

| Clarification Category | *Ambiguity* | *Inconsistency* | *Incompleteness* | **Count** |
|------------------------|:-----------:|:---------------:|:----------------:|:---------:|
| 1a                     |      ✔️      |                 |                  |    164    |
| 1c                     |              |       ✔️        |                  |    164    |
| 1p                     |              |                 |        ✔️        |    164    |
| 2ac                    |      ✔️      |       ✔️        |                  |    162    |
| 2cp                    |              |       ✔️        |        ✔️        |     34    |
| 2ap                    |      ✔️      |                 |        ✔️        |     74    |
| **Total**              |     --     |      --        |        --       |    762    |
<sub>
*Note*: The smaller size for 2ac (same applies for 2cp and 2ap) is because we directly applied a combination of two clarification types from 1a, 1c strictly, and we create a new modified problem as 2ac only if applying a combination of 1a and 1c leads to a new problem description that is different from either 1a or 1c. 2cp and 2ap have smaller counts because the ambiguous (a) or inconsistent (c) parts are removed in (p) for a large number of problems.
</sub>

## Example
Below is an example of HumanEvalComm built upon HumanEval. The modified problem descriptions are shown in this table for problem number 42 of HumanEval. Specifically, the descriptions of the problem were modified to be inconsistent, ambiguous, or incomplete. The main goal of the HumanEvalComm dataset is to evaluate the degree of communication.

<img width="728" alt="ex" src="https://github.com/user-attachments/assets/123a2de8-0da5-429b-80e3-a9637caafcaa" />

## Getting Started
### Setup
To use LLM-based evaluator, you need to set `OPENAI_KEY` variables. 
```bash
export OPENAI_KEY='...'
```

### Install the necessary requirements
Install the dependencies that you need to run the code:
```bash
pip install requirements.txt
```

### Inference and Evaluation
The main script to run the evaluation is `./scripts/script_stepwise_phase123.bat`. Below is the command:
```bash
./scripts/script_stepwise_phase123.bat {models} {phase} {starting_problem_num} {ending_problem_num}
```
`{models}` must point to the model that you want to use to run the evaluation.
`{phase}` defines the phase to be executed in the evaluation. Below are the values of `phase` in the 
`{starting_problem_num} {ending_problem_num}` define the indices of the first and last problems that the evaluation must be run on.

evaluation:
- 0: run models to get the initial response of the given model for either HumanEvalComm or HumanEval. output: file in log/
- 1: the initial responses of the model from the previous step are evaluated by the LLM-based evaluator (for HumanEvalComm only). output: file in log/
- 2: run models again to get the 2nd response based on the responses got from LLM-based evaluator output (for HumanEvalComm only). output: file in log/
- 3: extract code and run test cases and other metrics for each problem. input: file in log/  output: file in log/record/
- 4: compute more metrics for each problem, such as test pass rate, question quality rate, comm. rate, etc. input: file in ./log/record/ output: file in ./result_data/
- 5: aggregate and display metrics for all problems. output: files in table/
- 6: aggregate and display metrics for each clarification category for all problems. output: files in table/ 

Here are some examples:
```bash
#phase 0:
    ./scripts/script_stepwise_phase123.bat "gpt-3.5-turbo-0125 Okanagan" 0 0 5 HumanEval
#phase 1:
    ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat Meta-Llama-3-8B-Instruct CodeLlama-13b-Instruct-hf" 1 0 -1 HumanEvalComm prompt1
#phase 2 (for HumanEvalComm):
    ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat CodeLlama-13b-Instruct-hf CodeQwen1.5-7B-Chat" 2 0 5 HumanEvalComm
#analyze remaining open models (on HumanEvalComm):
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

If you want to run the same commands but for linux environment, you must change the script_stepwise_phase123.bat file with script_stepwise_phase123_unix.sh

The steps 0 and 2 require GPU in order to run the model inference while evaluating on the provided benchmark. The rest of the steps do not require GPU power, and can be simply run on CPU.

For that reason, we present below scripts on how to run the steps 0 and 2 on GPU.
If you want to run an evaluation in Alliance Canada servers (or possibly other servers that support job running using sbatch) use the following commands:

In order to run the step 0 (do the initial evaluation using your model) you should use the file scripts/alliance_scripts/submit_evaluation_step_0.sh. Before running, please make the necessary modifications in them such as specifying the your model file path, etc.

Use the following command to run step 0

```
sbatch scripts/alliance_scripts/submit_evaluation_step_0.sh
```

Use the following command to run step 2

```
sbatch scripts/alliance_scripts/submit_evaluation_step_2.sh
```

For all other steps, the command is the same as mentioned above.


## Evaluation Methods and Results
The figure below shows the flowchart for the evaluation of models. For each programming problem in the HumanEvalComm, there are up to six modified problem descriptions as described earlier in Table 1. For
each modified problem, a prompt is used as the input of the model to either generate code or ask clarifying questions if needed. Then, if the model asks clarifying questions rather than generates code directly, the questions are sent to
an LLM-based Evaluator, which evaluates the questions and generates a reply to answer the questions, based on all of the available information, including the modified problem, original problem, and the clarifying questions. Finally, the
answers and the previous conversations are sent to the model to generate the code again directly. 

Besides the LLMs, we also released and evaluated a LLM agent approach, *Code Clarification and Generation Agent* (**Okanagan**), as an LLM-based agent with a multi-round structure and customized prompt for the code generation task. A key feature of Okanagan is the ability to ask clarifying questions about the input problem descriptions needed for generating correct code.

<p align="center">
  <img width="1000" alt="HumanEvalComm" src="https://github.com/jie-jw-wu/human-eval-comm/assets/122728498/9a7d2142-7ac5-4f64-8557-225e8b221dc7">
  <br>
  <i>Figure: Flowchart for the evaluation of models, either Code LLMs or Okanagan (LLM agent), in communication capability.</i>
</p>


The table below shows the evaluation result across all clarification categories on Pass@1, Test Pass Rate, communication rate, and Good Question Rate with different models on HumanEvalComm (*HmEvalComm* in the table). Additionally, the Pass@1 and Test Pass Rate on the original problems in HumanEval (*HmEval* in the table) are also shown. Top 4 results are marked as **bold**.

| Model                            | **Pass@1** | **Pass@1** | **Test Pass Rate** | **Test Pass Rate** | **Comm. Rate** | **Good Question Rate** |
|----------------------------------|------------|------------|--------------------|--------------------|----------------|------------------------|
|                                  | *HmEval*   | *HmEvalComm* | *HmEval*          | *HmEvalComm*       |            |          |
| **ChatGPT**                      | 65.58%     | 31.34%     | 76.42%             | 49.39%             | 14.21%         | 13.43%                 |
| **CodeLlama**                    | 29.88%     | 19.35%     | 45.71%             | 37.79%             | 10.16%         | 37.55%                 |
| **CodeQwen1.5 Chat**             | 76.83%     | **47.61%** | 84.4%              | **62.89%**         | 4.82%          | 41.68%                 |
| **DeepSeek Coder**               | 71.78%     | **45.68%** | 79.44%             | **62.25%**         | **30.76%**     | **61.42%**             |
| **DeepSeek Chat**                | 12.8%      | 26.32%     | 13.86%             | 44.52%             | **37.93%**     | **58.71%**             |
| **Okanagan (Base=ChatGPT)**      | 27.45%     | **39.62%** | 33.45%             | **56.98%**         | **72.73%**     | **52.24%**             |
| **Okanagan (Base=DeepSeek Coder)** | 21.25%     | **38.06%** | 24.3%              | **52.72%**         | **82.51%**     | **60.13%**             |

The figure below shows the comparison of the effectiveness of the models in Communication Rate, Good Question Rate (left), and Pass@1, Test Pass Rate (right). Note that in the right figure, the stars represent the original performance of the corresponding model with the same color in the HumanEval benchmark. This shows visually how the performance has changed when the problem description is modified.

<p align="center">
 <img width="1718" alt="scatter_plot" src="https://github.com/user-attachments/assets/c08f3d7b-e0e4-453f-93a8-8a63a8119e20" />
</p>

**_Key Finding_: More than 60% of responses from Code LLMs still generate code rather than ask questions when the problem descriptions are manually modified according to different clarification categories. Incompleteness category results in higher communication rates and Good Question Rates, but lower Pass@1 and Test Pass Rate for Code LLMs.**

## Acknowledgements
This code is heavily influenced by the Nondeterminism evaluation research of ChatGPT (https://github.com/CodeHero0/Nondeterminism-of-ChatGPT-in-Code-Generation), and by IdentityChain(https://github.com/marcusm117/IdentityChain/tree/main) on testing models including CodeLlama.

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
