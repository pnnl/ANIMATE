#%% Load Framework and library
import json
import os, sys

# %%
from workflowsteps import *
from library import *
from libcases import *
from datetimeep import DateTimeEP

import matplotlib.pyplot as plt

# %% Load and assemble verification items
cases_path = "../test_cases/verif_mtd_pp/verification_cases.json"

with open(cases_path) as cases_file:
    cases_dict = json.load(cases_file)
items = [case for case in cases_dict["cases"]]

unique_idfs_to_items = {}
no_idfs_items = []
i = 0
for item in items:
    idf_path = None
    if item["run_simulation"]:
        idf_path = item["simulation_IO"]["idf"]
        if idf_path not in unique_idfs_to_items:
            unique_idfs_to_items[idf_path] = []
        unique_idfs_to_items[idf_path].append(item)
    else:
        no_idfs_items.append(item)

print("Saving files:")
for k, v in unique_idfs_to_items.items():
    print(k)
    writer_path = f"../test_cases/verif_mtd_pp/{k.split('.idf')[0].split('/')[-1]}.json"
    with open(writer_path, "w") as fw:
        json.dump({"cases": v}, fw, indent=4)
with open("../test_cases/verif_mtd_pp/no_idfs_items.json", "w") as fw:
    json.dump({"cases": no_idfs_items}, fw, indent=4)
print("Complete!")
