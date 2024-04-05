rem .\scripts\script_manualRemove_temp_1_topn_1_prompt_type.bat gpt-3.5-turbo-0125

python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %1 -t 1 -n 1 -pt prompt1a
python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %1 -t 1 -n 1 -pt prompt1c
python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %1 -t 1 -n 1 -pt prompt1p
python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %1 -t 1 -n 1 -pt prompt2ac
python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %1 -t 1 -n 1 -pt prompt2ap
python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %1 -t 1 -n 1 -pt prompt2cp
python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %1 -t 1 -n 1 -pt prompt3acp
