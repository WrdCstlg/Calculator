import urllib.request
import json
import subprocess

def get_auth_token():
    try:
        token_output = subprocess.check_output(
            "git credential fill",
            input=b"protocol=https\nhost=github.com\n",
            shell=True
        ).decode()
        return [l.split("=")[1].strip() for l in token_output.splitlines() if l.startswith("password=")][0]
    except Exception:
        return None

def inspect_repo_runs(repo, max_runs=2):
    token = get_auth_token()
    headers = {"User-Agent": "CI-Check"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        runs_url = f"https://api.github.com/repos/WrdCstlg/{repo}/actions/runs?per_page={max_runs}"
        req = urllib.request.Request(runs_url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            runs = data.get("workflow_runs", [])
            for r in runs:
                print(f"\n=== {repo} Run #{r.get('run_number')}: '{r.get('name')}' ===")
                print(f"  Status: {r.get('status')} | Conclusion: {r.get('conclusion')} | Commit: {r.get('head_commit', {}).get('message')}")
                print(f"  URL: {r.get('html_url')}")

                jobs_url = r.get("jobs_url")
                j_req = urllib.request.Request(jobs_url, headers=headers)
                with urllib.request.urlopen(j_req) as j_resp:
                    j_data = json.loads(j_resp.read().decode("utf-8"))
                    for j in j_data.get("jobs", []):
                        print(f"    Job: '{j.get('name')}' -> Status: {j.get('status')} | Conclusion: {j.get('conclusion')}")
                        for s in j.get("steps", []):
                            print(f"        Step [{s.get('number')}]: {s.get('name')} -> {s.get('status')} ({s.get('conclusion')})")
    except Exception as e:
        print(f"Error checking {repo}:", e)

if __name__ == "__main__":
    inspect_repo_runs("alphabet-safari", 2)
