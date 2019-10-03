import os
import json

for fname in [f for f in os.listdir(os.path.join(os.path.dirname(__file__), "cassettes")) if "offline" not in f]:
    rfname = os.path.join(os.path.dirname(__file__), "cassettes", fname)
    offline_fname = os.path.join(os.path.dirname(__file__), "cassettes", fname.replace("online", "offline"))

    data = open(rfname, "r").read()
    replacements = json.load(open(os.path.dirname(__file__) + "/credentials.json"))["replacements"]
    for fro, to in replacements.items():
        data = data.replace(fro, to)
    open(offline_fname, "w").write(data)
