import urllib.request
import json

def inspect_latest_run(repo):
    try:
        runs_url = f"https://api.github.com/repos/WrdCstlg/{repo}/actions/runs?per_page=1"
        req = urllib.request.Request(runs_url, headers={"User-Agent": "CI-Check"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            runs = data.get("workflow_runs", [])
            if not runs:
                print(f"No runs found for {repo}")
                return
            latest = runs[0]
            print(f"\n=== {repo} Latest Run #{latest.get('run_number')}: '{latest.get('name')}' ===")
            print(f"  Overall Status: {latest.get('status')} | Conclusion: {latest.get('conclusion')}")
            print(f"  Commit: {latest.get('head_commit', {}).get('message')}")
            print(f"  URL: {latest.get('html_url')}")

            jobs_url = latest.get("jobs_url")
            j_req = urllib.request.Request(jobs_url, headers={"User-Agent": "CI-Check"})
            with urllib.request.urlopen(j_req) as j_resp:
                j_data = json.loads(j_resp.read().decode("utf-8"))
                for j in j_data.get("jobs", []):
                    print(f"    Job: '{j.get('name')}' -> Status: {j.get('status')} | Conclusion: {j.get('conclusion')}")
                    for s in j.get("steps", []):
                        print(f"        Step [{s.get('number')}]: {s.get('name')} -> {s.get('status')} ({s.get('conclusion')})")
    except Exception as e:
        print(f"Error checking {repo}:", e)

if __name__ == "__main__":
    inspect_latest_run("Calculator")
    inspect_latest_run("alphabet-safari")
