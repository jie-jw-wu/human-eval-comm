# HumanEvalComm: Evaluating the Communication Skill of Code LLM and LLM Agent

## Overview
Large language models (LLMs) have significantly improved their ability to perform tasks in the field of code generation. However, there
is still a gap between LLMs being capable coders and being top-tier software engineers. The most recent trends are using agent-based
LLMs to iterate the code generation process. Based on the observation that top-level software engineers often ask clarifying questions
to reduce ambiguity in both requirements and coding solutions, we argue that the same should be applied to LLMs for code generation
tasks. For this purpose, we define communication skills of LLMs as “being able to ask clarifying questions when the description
of the code generation problem has issues”. In this study, we restrict these issues to three matters from the software requirement
engineering field: inconsistent requirements, ambiguous requirements, and incomplete requirements. By asking probing questions
about requirements of problem descriptions before generating the final code, the challenges of programming with LLMs, such as
unclear intent specification may be alleviated, resulting to a correct code in the initial iterations.

In this work, we conducted an empirical study on the benchmark and analysis of the communication skills of LLMs for code
generation. We created a new benchmark, HumanEvalComm, by modifying problem descriptions according to three issues mentioned
above, inconsistency, ambiguity, incompleteness. We then experimented on HumanEvalComm with different Code LLMs, and a new
LLM Agent approach, Code Clarification and Generation Agent (Okanagan), to identify and ask questions in ambiguous parts from code
and descriptions for further refining the generated code. We defined Communication Rate and Good Question Rate as the evaluation
metrics to represent the ratio of questions asked and questions with good quality in responses. We found that 95% of responses from
Code LLMs still generate code even when half of the problem descriptions are randomly removed. More than 80% of responses from
Code LLMs still generate code even when the problem descriptions are manually modified according to the taxonomy of clarification
types, with a lower test pass rate due to a lack of necessary information. Compared with Code LLMs, we also found that the proposed
LLM Agent approach, Okaganan, effectively increased Communication Rate and Good Question Rate by an absolute 59% and 5%,
respectively. This resulted in an increase in Test Pass Rate and Pass@1 by 25% and 15%, respectively. This indicates more effective
communication capability for LLM Agent compared with Code LLMs.

## Acknowledgements
This code is heavily influenced by the Nondeterminism evaluation research of ChatGPT (https://github.com/CodeHero0/Nondeterminism-of-ChatGPT-in-Code-Generation), and by IdentityChain(https://github.com/marcusm117/IdentityChain/tree/main) on testing models including StarCoderBase and CodeLlama.

## Reference
Wu, Jie JW, Fatemeh Hendijani Fard. "Benchmarking the Communication Competence of Code Generation for LLMs and LLM Agents." In Arxiv.
