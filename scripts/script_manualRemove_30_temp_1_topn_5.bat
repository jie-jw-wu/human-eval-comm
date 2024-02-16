rem Now, continue to remove 30% content and generate results:
python3 generate_response.py -d HumanEvalComm -m gpt-3.5-turbo -n 1 -t 1 -s 0 -o manualRemove
python3 intermedia_analyze.py -f log/manualRemove_dataset_HumanEvalComm_model_gpt-3.5-turbo_topn_1_temperature_1.0.log_0 -n 1

rem Now, I will run syntactic_similarity_OER.py to get results.
python3 syntactic_similarity_OER.py  -e manualRemove_dataset_HumanEvalComm  -m gpt-3.5-turbo -t 1 -o R1 -n 1
