import os
import json

for fname in os.listdir(os.path.join(os.path.dirname(__file__), "cassettes")):
    fname=os.path.join(os.path.dirname(__file__), "cassettes",fname)
    data = open(fname, "r").read()
    replacements = json.load(open(os.path.dirname(__file__) + "/credentials.json"))["replacements"]
    for fro, to in replacements.items():
        data = data.replace(fro, to)
    open(fname, "w").write(data)
