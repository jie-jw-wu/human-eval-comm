python generate_response.py -d HumanEvalComm -m gpt-3.5-turbo-0125 -n 1 -t 1 -o manualRemove -minp %1 -maxp %2 --log_phase_input 0 --log_phase_output 1
python generate_response.py -d HumanEvalComm -m gpt-3.5-turbo-0125 -n 1 -t 1 -o manualRemove -minp %1 -maxp %2 --log_phase_input 1 --log_phase_output 2
python generate_response.py -d HumanEvalComm -m gpt-3.5-turbo-0125 -n 1 -t 1 -o manualRemove -minp %1 -maxp %2 --log_phase_input 2 --log_phase_output 3

rem python generate_response.py -d HumanEvalComm -m CodeLlama-7b-Instruct-hf -n 1 -t 1 -o manualRemove -minp 0 -maxp 165 --log_phase_input 1 --log_phase_output 2

rem save models to local files
rem export HF_HOME=/arc/project/st-fhendija-1/jwu/hf_dir_cache
rem python generate_response.py -d HumanEvalComm -m CodeLlama-13b-Instruct-hf -n 1 -t 1 -s 0 -o manualRemove --hf_dir /arc/project/st-fhendija-1/jwu/hf_dir_cache --model_name_or_path codellama/CodeLlama-13b-Instruct-hf --saved_model_path /arc/project/st-fhendija-1/jwu/codellama/CodeLlama-13b-Instruct-hf -maxp -1 --do_save_model