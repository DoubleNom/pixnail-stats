import json


def load_json_file(filename: str):
    with open(filename, "r") as f:
        return json.loads(f.read())
