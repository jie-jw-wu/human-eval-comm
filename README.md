![1632041413-huge-scaled-1-1440x466](https://github.com/jie-jw-wu/human-eval-comm/assets/122728498/14395bdb-c82d-42a6-a2d6-8b9453d9e321)

# HumanEvalComm: Evaluating the Communication Skill of Code LLMs and LLM Agent (Okanagan)

## Overview

Large language models (LLMs) have significantly improved their ability to perform tasks in the field of code generation. However, there is still a gap between LLMs being capable coders and being top-tier software engineers. The most recent trends involve using LLM-based agents to iterate the code generation process.
Based on the observation that top-level software engineers often ask clarifying questions to reduce *Ambiguity* in both requirements and coding solutions, we argue that the same should be applied to LLMs for code generation tasks. For this purpose, we define the communication skills of LLMs as "being able to ask clarifying questions when the description of the code generation problem has issues." In this study, we restrict these issues to three matters from the software requirement engineering field: inconsistent requirements, ambiguous requirements, and incomplete requirements. By asking probing questions about the requirements of problem descriptions before generating the final code, the challenges of programming with LLMs, such as unclear intent specification, may be alleviated, resulting in correct code in the initial iterations.


In this work, we conducted an empirical study on the benchmark and analysis of the communication skills of LLMs for code generation. We created a new benchmark, HumanEvalComm, by modifying problem descriptions according to three issues mentioned above: *Inconsistency*, *Ambiguity*, and *Incompleteness*. We then experimented on HumanEvalComm with different Code LLMs and a new LLM agent approach, **C<ins>o</ins>de <ins>C</ins>l<ins>a</ins>rificatio<ins>n</ins> <ins>a</ins>nd <ins>G</ins>eneration <ins>A</ins>ge<ins>n</ins>t (Okanagan)**, to identify and ask questions in ambiguous parts of code and descriptions for further refining the generated code.
In the evaluation, we introduced an *LLM-based evaluator* and created *Communication Rate* and *Good Question Rate* as the evaluation metrics to represent the ratio of questions asked and questions with good quality in responses. We found that more than 60% of responses from Code LLMs still generate code rather than ask questions when the problem descriptions are manually modified according to different clarification categories.
The Pass@1 and Test Pass Rate of most Code LLMs drop by 35% to 52% and by 17% to 35% respectively, with statistical significance in each category for over 75% numbers. Okanagan, as an LLM agent approach that uses LLMs such as ChatGPT 3.5, effectively increases the Communication Rate and Good Question Rate by an absolute 58% and 38% respectively, and thus boosts Pass@1 and Test Pass Rate by an absolute 8% and 7% respectively, when the problem descriptions are modified based on given clarification categories. This indicates the potential for achieving more effective communication capability using the LLM agent.



<img width="1501" alt="HumanEvalComm" src="https://github.com/jie-jw-wu/human-eval-comm/assets/122728498/9a7d2142-7ac5-4f64-8557-225e8b221dc7">

## Acknowledgements
This code is heavily influenced by the Nondeterminism evaluation research of ChatGPT (https://github.com/CodeHero0/Nondeterminism-of-ChatGPT-in-Code-Generation), and by IdentityChain(https://github.com/marcusm117/IdentityChain/tree/main) on testing models including StarCoderBase and CodeLlama.

## Reference
Wu, Jie JW, Fatemeh Hendijani Fard. "Benchmarking the Communication Competence of Code Generation for LLMs and LLM Agents." In Arxiv.
