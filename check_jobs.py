import urllib.request
import json

def check_run_jobs(repo, run_id):
    url = f"https://api.github.com/repos/WrdCstlg/{repo}/actions/runs/{run_id}/jobs"
    req = urllib.request.Request(url, headers={"User-Agent": "CI-Check"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            jobs = data.get("jobs", [])
            for j in jobs:
                print(f"  Job: '{j.get('name')}' -> Status: {j.get('status')} | Conclusion: {j.get('conclusion')}")
                for s in j.get('steps', []):
                    status = s.get('status')
                    conclusion = s.get('conclusion')
                    print(f"      Step [{s.get('number')}]: {s.get('name')} -> {status} ({conclusion})")
    except Exception as e:
        print(f"Error checking jobs for {repo}:", e)

print("=== Calculator Run 38847440804 ===")
check_run_jobs("Calculator", 38847440804)

print("\n=== Alphabet Safari Run 38847444303 ===")
check_run_jobs("alphabet-safari", 38847444303)
