rem generate results of original prompt (4 examples).
python3 generate_response.py -d HumanEval -m gpt-4 -n 5 -t 1 -s 0 -o original
python3 intermedia_analyze.py -f log/dataset_HumanEval_model_gpt-4_topn_5_temperature_1.0.log_0
python3 syntactic_similarity_OER.py  -e dataset_HumanEval  -m gpt-4 -t 0 -o R1

rem Now, continue to remove 30% content and generate results:
python3 generate_response.py -d HumanEval -m gpt-4 -n 5 -t 1 -s 0 -o randRemove_50
python3 intermedia_analyze.py -f log/randRemove_50_dataset_HumanEval_model_gpt-4_topn_5_temperature_1.0.log_0 -of log/record/dataset_HumanEval_model_gpt-4_topn_5_temperature_1.0.log_0

rem Now, I will run syntactic_similarity_OER.py to get results.
python3 syntactic_similarity_OER.py  -e randRemove_50_dataset_HumanEval  -m gpt-4 -t 1 -o R1
