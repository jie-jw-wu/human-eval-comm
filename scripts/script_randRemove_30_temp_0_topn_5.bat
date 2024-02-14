rem generate results of original prompt (4 examples).
python3 generate_response.py -d HumanEval -m gpt-3.5-turbo -n 5 -t 0 -s 0 -o original
rem extract code and run test cases for results.
python3 intermedia_analyze.py -f log/dataset_HumanEval_model_gpt-3.5-turbo_topn_5_temperature_0.0.log_0
rem compute test pass rate and comm. rate.
python3 syntactic_similarity_OER.py  -e dataset_HumanEval  -m gpt-3.5-turbo -t 0 -o R1

rem Now, continue to remove 30% content and generate results:
python3 generate_response.py -d HumanEval -m gpt-3.5-turbo -n 5 -t 0 -s 0 -o randRemove_30
python3 intermedia_analyze.py -f log/randRemove_30_dataset_HumanEval_model_gpt-3.5-turbo_topn_5_temperature_0.0.log_0 -of log/record/dataset_HumanEval_model_gpt-3.5-turbo_topn_5_temperature_0.0.log_0

rem Now, I will run syntactic_similarity_OER.py to get results.
python3 syntactic_similarity_OER.py  -e randRemove_30_dataset_HumanEval  -m gpt-3.5-turbo -t 0 -o R1
