#!/usr/bin/env python3

import argparse
import json
import os

args = argparse.ArgumentParser()
args.add_argument("dir", action="store", help="specify json directory")
args.add_argument("id", action="store", help="id of recipe to adjust")
args.add_argument("level", action="store", help="what activity level to shift it to")
args_dict = vars(args.parse_args())


def gen_new(path):
    change = False
    with open(path, "r") as json_file:
        json_data = json.load(json_file)
        for jo in json_data:
            # We only want JsonObjects
            if type(jo) is str:
                return None

            # We need a type to discriminate
            if not "type" in jo:
                return None

            # specifically, only recipes and uncrafts
            kind = jo["type"]
            if kind != "recipe" and kind != "uncraft":
                return None

            # Also, make sure it has a 'result'
            if not "result" in jo:
                return None

            # We don't want to change obsolete recipes
            if "obsolete" in jo and jo["obsolete"]:
                return None

            if jo["result"] == args_dict["id"]:
                # Already got this one
                if jo["activity_level"] != "fake":
                    print("skipping {skipped} - value is {val}, currently on {current}".format(skipped=jo["result"], val=jo["activity_level"], current=args_dict["id"]))
                    return None
                jo["activity_level"] = args_dict["level"]
                change = True

    return json_data if change else None


for root, directories, filenames in os.walk(args_dict["dir"]):
    for filename in filenames:
        path = os.path.join(root, filename)
        if path.endswith(".json"):
            new = gen_new(path)
            if new is not None:
                with open(path, "w") as jf:
                    json.dump(new, jf, ensure_ascii=False)
                os.system(f"./tools/format/json_formatter.cgi {path}")
