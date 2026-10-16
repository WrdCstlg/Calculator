import urllib.request
import json

url = "https://api.github.com/repos/WrdCstlg/alphabet-safari/actions/runs/38847313346/jobs"
req = urllib.request.Request(url, headers={"User-Agent": "CI-Check"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    for j in data.get("jobs", []):
        if j.get("conclusion") == "failure":
            print(f"Failed Job: {j.get('name')}")
            for s in j.get("steps", []):
                print(f"  Step: '{s.get('name')}' -> {s.get('conclusion')}")
