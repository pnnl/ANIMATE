#%% Load Framework and library
import os, sys

# %%
from workflowsteps import *
from library import *
from libcases import *
from datetimeep import DateTimeEP

import matplotlib.pyplot as plt

# %% Load and assemble verification items
cases_path = "../test_cases/verif_mtd_pp/verification_cases.json"
lib_items_path = "../schema/library.json"
items = assemble_verification_items(
    cases_path=cases_path, lib_items_path=lib_items_path
)

# %%
plt.rcParams["figure.figsize"] = [16, 4 * 2]
run_libcase(items[30])
# %%
