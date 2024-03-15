python generate_response.py -d HumanEvalComm -m starcoderbase-1b -n 1 -t 1 -s 0 -o manualRemove --hf_dir D:\Study\Research\Projects\huggingface --model_name_or_path bigcode/starcoderbase-1b -maxp -1

rem for sockeye:  python generate_response.py -d HumanEvalComm -m starcoderbase-1b -ndir /scratch/st-fhendija-1/jwu/cache --model_name_or_path bigcode/starcoderbase-1b -maxp -1


rem python generate_response.py -d HumanEvalComm -m CodeLlama-7b-hf -n 1 -t 1 -s 0 -o manualRemove --hf_dir D:\Study\Research\Projects\huggingface --model_name_or_path codellama/CodeLlama-7b-hf -maxp -1
rem bigcode/starcoderbase-1b

rem python intermedia_analyze.py -f log/manualRemove_dataset_HumanEvalComm_model_CodeLlama_topn_1_temperature_1.0.log_0 -n 1

rem python syntactic_similarity_OER.py -e manualRemove_dataset_HumanEvalComm -m CodeLlama -t 1 -o R1 -n 1

rem python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m CodeLlama -t 1 -n 1
