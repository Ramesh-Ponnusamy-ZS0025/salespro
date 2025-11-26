"""
Quick test for scraper worker
"""
import subprocess
import sys
import json
from pathlib import Path

worker_script = Path(__file__).parent / "scraper_worker.py"
user_id = "test_user"

print(f"Testing worker script: {worker_script}")
print(f"User ID: {user_id}")
print("-" * 60)

# Run the worker
process = subprocess.Popen(
    [sys.executable, str(worker_script), user_id],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=str(worker_script.parent)
)

print("Worker process started, waiting for completion...")
print("This may take 3-5 minutes...\n")

try:
    stdout, stderr = process.communicate(timeout=600)

    print("STDOUT:")
    print(stdout)
    print("\nSTDERR:")
    print(stderr)

    # Try to parse JSON result
    lines = stdout.strip().split('\n')
    for line in reversed(lines):
        try:
            result = json.loads(line)
            print("\n" + "=" * 60)
            print("RESULT:")
            print(json.dumps(result, indent=2))
            print("=" * 60)
            break
        except json.JSONDecodeError:
            continue

except subprocess.TimeoutExpired:
    print("Timeout! Killing process...")
    process.kill()
    stdout, stderr = process.communicate()
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
