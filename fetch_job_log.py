import urllib.request
import json

url = "https://api.github.com/repos/WrdCstlg/alphabet-safari/actions/runs/38847313346/jobs"
req = urllib.request.Request(url, headers={"User-Agent": "CI-Check"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    for j in data.get("jobs", []):
        if j.get("name") == "Docker Web Server Live Verification":
            print("Job ID:", j.get("id"))
            # Fetch log
            log_url = f"https://api.github.com/repos/WrdCstlg/alphabet-safari/actions/jobs/{j.get('id')}/logs"
            try:
                l_req = urllib.request.Request(log_url, headers={"User-Agent": "CI-Check"})
                with urllib.request.urlopen(l_req) as l_resp:
                    print(l_resp.read().decode("utf-8")[:1000])
            except Exception as e:
                print("Log fetch error:", e)
