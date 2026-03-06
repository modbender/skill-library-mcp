import argparse, subprocess, sys, os

parser = argparse.ArgumentParser()
parser.add_argument('--tests', default='tests', help='Path to tests (dir or file)')
parser.add_argument('--run', required=True, help='Command to run after tests pass')
args = parser.parse_args()

TEST_CMD = os.getenv('TEST_CMD') or f"pytest {args.tests}" if os.path.isdir(args.tests) else f"pytest {args.tests}"

print(f"Running tests: {TEST_CMD}")
res = subprocess.run(TEST_CMD, shell=True)
if res.returncode != 0:
    print("Tests failed or missing. Aborting run.")
    sys.exit(res.returncode or 1)

if os.getenv('WARN_AS_ERROR') == '1':
    lint = os.getenv('LINT_CMD') or "ruff ."
    print(f"Running lint: {lint}")
    lint_res = subprocess.run(lint, shell=True)
    if lint_res.returncode != 0:
        print("Lint/warnings failed. Aborting run.")
        sys.exit(lint_res.returncode or 1)

print("Tests green. Running target...")
run_res = subprocess.run(args.run, shell=True)
sys.exit(run_res.returncode)
