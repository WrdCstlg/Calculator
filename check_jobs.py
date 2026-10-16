import urllib.request
import json
import time

def check_run_jobs(repo, run_id):
    url = f"https://api.github.com/repos/WrdCstlg/{repo}/actions/runs/{run_id}/jobs"
    req = urllib.request.Request(url, headers={"User-Agent": "CI-Check"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            jobs = data.get("jobs", [])
            for j in jobs:
                print(f"    Job: '{j.get('name')}' -> Status: {j.get('status')} | Conclusion: {j.get('conclusion')}")
    except Exception as e:
        print("Error checking jobs:", e)

print("Checking Calculator Run 38847309904:")
check_run_jobs("Calculator", 38847309904)

print("\nChecking Alphabet Safari Run 38847313346:")
check_run_jobs("alphabet-safari", 38847313346)
