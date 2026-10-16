import urllib.request
import json
import time

for repo in ["Calculator", "alphabet-safari"]:
    try:
        url = f"https://api.github.com/repos/WrdCstlg/{repo}/actions/runs"
        req = urllib.request.Request(url, headers={"User-Agent": "CI-Check"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            runs = data.get("workflow_runs", [])
            print(f"=== {repo} Actions Runs ({len(runs)}) ===")
            for r in runs[:3]:
                print(f"  Run #{r.get('run_number')}: '{r.get('name')}' -> Status: {r.get('status')} | Conclusion: {r.get('conclusion')} | URL: {r.get('html_url')}")
    except Exception as e:
        print(f"Error querying {repo}:", e)
