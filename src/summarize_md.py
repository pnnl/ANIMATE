import json, os, sys, glob
from tqdm import tqdm

md_dict_dump = {}


def keystoint(x):
    return {int(k): v for k, v in x.items()}


for md_file in glob.glob("../results/*_md.json"):
    with open(md_file) as fr:
        md_dict = json.load(fr, object_hook=keystoint)
    md_dict_dump.update(md_dict)

md_full_string0 = """
# Verification Results:

| Case No.                                       | Outcome Summary |
| ---------------------------------------------- | --------------- |
"""

# md_full_string1 = """
#
# ----
#
# """

caseids_sorted = sorted(md_dict_dump)
# md_sorted = [md_dict_dump[s] for s in sorted(md_dict_dump)]
# table_rows = []

for caseid in caseids_sorted:
    outcome = md_dict_dump[caseid][1]
#     mdtable_row = f"""
# | [{caseid}](#results-for-verification-case-id-{caseid}) | {outcome} |
# """
    mdtable_row = f"| [{caseid}](./case-{caseid}.md) | {outcome} |\n"
    md_full_string0 += mdtable_row

    md_section = md_dict_dump[caseid][0]
    # md_full_string1 += md_section

    md_section += "[Back](results.md)"
    with open(f"../results/case-{caseid}.md", "w") as casew:
        casew.write(md_section)

md_full_string = md_full_string0# + md_full_string1

with open("../results/results.md", "w") as fw:
    fw.write(md_full_string)
