# The AgentFramework baseline

- The original AgentCoder framework, as described in the paper "AgentCoder: Multi-Agent Code Generation with Effective Testing and Self-Optimisation", is adapted for use with HumanEvalComm to generate code with clarifying questions.
- Relevant Links: 
    - [Paper link](https://arxiv.org/abs/2312.13010) 
    - [GitHub Link](https://github.com/huangd1999/AgentCoder).
- AgentCoder is one of the leading agent-based code generation pipelines, with reported pass@1 scores on the HumanEval benchmark of 96.3 using GPT4 and 79.9 using chatGPT, making it ideal for use as a baseline for our project.
- AgentCoder consists of three steps:
    - programmer.py : Generates code based on the given problem
    - designer.py: Generates test cases for the problem
    - executor.py: Runs the code generated by "programmer.py" locally on the test cases generated by "designer.py" and improves the code.

## Running AgentCoder baseline

- AgentCoder requires a functional installation of the CodeGeeX library. To set up the environment:
- Inside the human-eval-comm directory, run the following command to clone the CodeGeeX repository:
```
git clone https://github.com/THUDM/CodeGeeX
```
- Then, navigate to CodeGeeX and install the required dependencies:
```
pip install -r requirements.txt
```
- Then navigate to CodeGeeX/codegeex/benchmark/execution.py and make the following changes:
    - change every instance of "test_code" to "full_code"
    - change every instance of "generation" to "completion"
- These changes accommodate updates made to the CodeGeeX library after the original release of AgentCoder. More details on this issue can be found in this [GitHub discussion.](https://github.com/huangd1999/AgentCoder/issues/1)

- Now, navigate to human-eval-comm/ and run the following steps to run AgentCoder on HumanEvalComm
```
./scripts/script_stepwise_phase123_unix.sh "AgentCoder" 0 0 164
./scripts/script_stepwise_phase123_unix.sh "AgentCoder" 1 0 164
./scripts/script_stepwise_phase123_unix.sh "AgentCoder" 2 0 164
```

- The first step runs AgentCoder on round 1, asking the model to either generate code or clarifying questions. For this step, we had to change the functioning of AgentCoder. Originally made to run on the HumanEval dataset, we wish to run AgentCoder on our own created HumanEvalComm dataset, which has modified prompts which ask the model to generate clarifying questions.
- Due to this, for round 1, we use only programmer.py from AgentCoder since the response is not limited to code but to clarifying questions. This leads to the generation of a completion list that contains either clarifying questions or code.
- For round 2, we generate answers to these questions.
- For round 3, we run the entirety of AgentCoder, with all the context from the previous two rounds.

## Changes made to the original repository

- "max_workers" was set to "1" from an original value of "5" since our code only sends one request at a time to AgentCoder to avoid concurrency issues and ensuring that responses are processed sequentially.
-  Instead of loading the HumanEval dataset from HuggingFace, we pass the HumanEvalComm data as a list of dictionaries directly into AgentCoder.
- File names now include the task_id to monitor individual entries in the HumanEvalComm dataset, allowing precise tracking of each task's results.
- We changed the original prompt to programmer.py to include a "clarity_prompt", enabling the model to generate clarifying questions instead of code when necessary.
- In executor.py, we reduced the number of epochs to 1 to limit LLM calls and manage our budget efficiently.
- Since our data modified the problem statements to have functions by the name of "candidate", we add checks in executor.py to ensure that either the "entry_point" is the original function name or "candidate".
- Robust error handling mechanisms were introduced throughout the code to ensure smooth execution and prevent unexpected crashes.

## Attribution and Licensing
- Authors: Dong Huang, Jie M. Zhang, Michael Luck, Qingwen Bu, Yuhao Qing, Heming Cui
- License: MIT License