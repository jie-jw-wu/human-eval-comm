rem Example: 
rem XXX.bat 0 165 gpt-3.5-turbo-0125
rem XXX.bat 0 165 Okanagan
rem python generate_response.py -d HumanEvalComm -m %3 -n 1 -t 1 -o manualRemove -minp %1 -maxp %2 --log_phase_input 0 --log_phase_output 1
rem python generate_response.py -d HumanEvalComm -m %3 -n 1 -t 1 -o manualRemove -minp %1 -maxp %2 --log_phase_input 1 --log_phase_output 2
rem python generate_response.py -d HumanEvalComm -m %3 -n 1 -t 1 -o manualRemove -minp %1 -maxp %2 --log_phase_input 2 --log_phase_output 3

python intermedia_analyze.py -f log/manualRemove_dataset_HumanEvalComm_model_%3_topn_1_temperature_1.0.log_3 -n 1

python syntactic_similarity_OER.py -e manualRemove_dataset_HumanEvalComm -m %3 -t 1 -o R1 -n 1 -s 3

python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %3 -t 1 -n 1