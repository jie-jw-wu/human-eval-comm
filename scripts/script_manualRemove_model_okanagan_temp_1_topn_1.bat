
python generate_response.py -d HumanEvalComm -m Okanagan -n 1 -t 1 -s 0 -o manualRemove -maxp -1

python intermedia_analyze.py -f log/manualRemove_dataset_HumanEvalComm_model_Okanagan_topn_1_temperature_1.0.log_0 -n 1

rem python syntactic_similarity_OER.py -e manualRemove_dataset_HumanEvalComm -m gpt-3.5-turbo-0125 -t 1 -o R1 -n 1

rem python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m gpt-3.5-turbo-0125 -t 1 -n 1
