# General Imports
import os
import sys
import subprocess
import glob
# Project Imports
from clarifycoder_run.core import utils


class AgentCoderRunner:
    def __init__(self):
        self._workspace = os.getcwd()

        # Load configuration
        config_path = f'{self._workspace}/config/agentcoder_gemini.yml'
        self._config = utils.load_config(config_path)

        # Set configuration variables
        self._model_name = self._config['model']['name']
        self._agent_path = self._config['model']['agent_path']
        self._gemini_api_key = self._config['evaluator']['gemini_api_key']
        self._evaluator_model = self._config['evaluator']['model']
        self._dataset = self._config['experiment']['dataset']
        self._min_problem = self._config['experiment']['min_problem']
        self._max_problem = self._config['experiment']['max_problem']
        self._temperature = self._config['phases']['temperature']
        self._top_n = self._config['phases']['top_n']
        self._option = self._config['phases']['option']
        self._eval_protocol = self._config['phases']['eval_protocol']
        self._openai_key = self._config.get('api_keys', {}).get('openai_key', '')
        self._openai_api_key = self._config.get('api_keys', {}).get('openai_api_key', '')

        self._setup_environment()
        self._setup_logging()

        # Set working directory to parent (main project root)
        os.chdir(os.path.dirname(self._workspace))

    def _setup_environment(self):
        if self._gemini_api_key and self._gemini_api_key != "your-gemini-api-key-here":
            os.environ['GEMINI_API_KEY'] = self._gemini_api_key
            print("Gemini API key configured")
        else:
            print("Warning: Update gemini_api_key in config file")

        # Set OpenAI API keys (required by generate_response.py even if using Gemini)
        # Use dummy values if not using OpenAI (empty string or not provided)
        openai_key = self._openai_key if self._openai_key and self._openai_key.strip() else "dummy"
        openai_api_key = self._openai_api_key if self._openai_api_key and self._openai_api_key.strip() else "dummy"

        os.environ['OPENAI_KEY'] = openai_key
        os.environ['OPENAI_API_KEY'] = openai_api_key

        if openai_key != "dummy":
            print("OpenAI keys configured for use")
        else:
            print("OpenAI keys set to dummy (using Gemini instead)")

        os.environ['EVALUATOR_MODEL'] = self._evaluator_model
        print(f"Evaluator model: {self._evaluator_model}")

    def _setup_logging(self):
        
        log_dir = f'{self._workspace}/logs'
        os.makedirs(log_dir, exist_ok=True)

    def run_experiment(self, phases=None):
        
        if phases is None:
            phases = [0, 1, 2, 3]

        print(f"Starting AgentCoder experiment: AgentCoder with Gemini")
        print(f"Running phases: {phases}")

        for phase in phases:
            print(f"Running Phase {phase}...")
            self._run_phase(phase)
            print(f"Completed Phase {phase}")

        print("Experiment completed!")

    def _run_phase(self, phase: int):
        
        if phase == 0:
            self._run_phase_0()
        elif phase == 1:
            self._run_phase_1()
        elif phase == 2:
            self._run_phase_2()
        elif phase == 3:
            self._run_phase_3()
        else:
            print(f"Phase {phase} not implemented")

    def _run_phase_0(self):
        cmd = [
            sys.executable, "generate_response.py",
            "--dataset", self._dataset,
            "--model", self._model_name,
            "--topn", str(self._top_n),
            "--temperature", str(self._temperature),
            "--option", self._option,
            "--log_phase_output", "1"
        ]

        # Add problem range
        if self._min_problem >= 0:
            cmd.extend(["--min_problem_idx", str(self._min_problem)])
        if self._max_problem >= 0:
            cmd.extend(["--max_num_problems", str(self._max_problem + 1)])

        # Add model path if specified
        if self._agent_path and self._agent_path != "":
            cmd.extend(["--model_name_or_path", self._agent_path])

        self._run_command(cmd)

    def _run_phase_1(self):
        
        cmd = [
            sys.executable, "generate_response.py",
            "--dataset", self._dataset,
            "--model", self._model_name,
            "--topn", "1",
            "--temperature", "1.0",
            "--option", "manualRemove",
            "--log_phase_input", "1",
            "--log_phase_output", "2",
            "--eval_protocol", self._eval_protocol
        ]

        # Add problem range
        if self._min_problem >= 0:
            cmd.extend(["--min_problem_idx", str(self._min_problem)])
        if self._max_problem >= 0:
            cmd.extend(["--max_num_problems", str(self._max_problem + 1)])

        # Add model path if specified
        if self._agent_path and self._agent_path != "":
            cmd.extend(["--model_name_or_path", self._agent_path])

        self._run_command(cmd)

    def _run_phase_2(self):
        cmd = [
            sys.executable, "generate_response.py",
            "--dataset", self._dataset,
            "--model", self._model_name,
            "--topn", "1",
            "--temperature", str(self._temperature),
            "--option", "manualRemove",
            "--log_phase_input", "2",
            "--log_phase_output", "3",
            "--eval_protocol", self._eval_protocol
        ]

        # Add problem range
        if self._min_problem >= 0:
            cmd.extend(["--min_problem_idx", str(self._min_problem)])
        if self._max_problem >= 0:
            cmd.extend(["--max_num_problems", str(self._max_problem + 1)])

        # Add model path if specified
        if self._agent_path and self._agent_path != "":
            cmd.extend(["--model_name_or_path", self._agent_path])

        self._run_command(cmd)

    def _run_phase_3(self):
        
        # Find the log file from phase 2
        log_pattern = f"manualRemove_dataset_{self._dataset}_model_*_topn_1_temperature_*.log_3"
        log_dir = "./log"
        log_files = glob.glob(f"{log_dir}/{log_pattern.replace('*', '*')}")

        if not log_files:
            print("No log files found for analysis")
            return

        # Get the most recent log file
        log_file = max(log_files, key=os.path.getmtime)

        cmd = [
            sys.executable, "intermedia_analyze.py",
            "--file", log_file,
            "--topn", str(self._top_n)
        ]

        self._run_command(cmd)

    def _run_command(self, cmd):
        
        print(f"Running: {' '.join(cmd)}")

        # Show output in terminal AND log to file
        log_file = f'{self._workspace}/logs/experiment.log'
        print("=" * 80)

        try:
            with open(log_file, 'a') as f:
                f.write(f"\n=== Running: {' '.join(cmd)} ===\n")
                # Run command with real-time output to console (no redirection)
                result = subprocess.run(cmd, check=True, text=True)
                print("=" * 80)
                print(f"✓ Command completed successfully")
        except subprocess.CalledProcessError as e:
            print("=" * 80)
            print(f"✗ Command failed with return code {e.returncode}")
            raise


def main():
    print("=== ClarifyCoder Experiment Runner ===")
    print("Loading configuration from config/agentcoder_gemini.yml")

    try:
        runner = AgentCoderRunner()
        runner.run_experiment()
    except Exception as e:
        print(f"Experiment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()