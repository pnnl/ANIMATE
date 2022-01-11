import json, os, sys, glob
from tqdm import tqdm

md_dict_dump = {}
for md_file in glob.glob("../results/*_md.json"):
    with open(md_file) as fr:
        md_dict = json.load(fr)
    md_dict_dump.update(md_dict)

md_full_string = """
Verification Results:


"""

md_sorted = {md_dict_dump[s] for s in sorted(md_dict_dump)}

for md in md_sorted:
    md_full_string += md

with open("../results/results.md", "w") as fw:
    fw.write(md_full_string)
