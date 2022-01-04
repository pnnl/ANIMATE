from workflowsteps import *
from library import *
from datetimeep import DateTimeEP
import sys, os


def run_verification_case(item, plot_option="all-compact"):
    need_injection = True
    run_sim = True
    if need_injection and run_sim:
        original_idf_path = item.item["simulation_IO"]["idf"].strip()
        idd_path = item.item["simulation_IO"]["idd"].strip()
        if ".idf" in original_idf_path.lower():
            run_path = f"{original_idf_path[:-4]}"
        elif ".epjson" in original_idf_path.lower():
            run_path = f"{original_idf_path[:-7]}"
        else:
            run_path = original_idf_path

    if need_injection:
        run_path = f"{run_path}_injected_BatchVerification"

    if run_sim:
        df = DateTimeEP(
            item.read_points_values(
                csv_path=f"{run_path}/eplusout.csv",
                idf_path=f"{run_path}/in.idf",
                idd_path=idd_path,
            ),
            year=2000,
        ).transform()
    else:
        df = DateTimeEP(
            item.read_points_values(
                csv_path=f"../resources/{item.item['simulation_IO']['output']}"
            )
        ).transform()
    verification_class = item.item["verification_class"]
    cls = globals()[verification_class]
    parameters = (
        item.item["datapoints_source"]["parameters"]
        if ("parameters" in item.item["datapoints_source"])
        else None
    )
    verification_obj = cls(df, parameters, f"{run_path}")
    outcome = verification_obj.get_checks
    verification_obj.plot(plot_option)


def main():
    num_argv = len(sys.argv)
    cases_path = "../test_cases/verif_mtd_pp/verification_cases.json"
    lib_items_path = "../schema/library.json"
    items = assemble_verification_items(
        cases_path=cases_path, lib_items_path=lib_items_path
    )
    if num_argv == 1:
        print(
            f"No command line argument provided, running all {len(items)} verification cases from {cases_path} sequentially with one thread"
        )
    elif num_argv == 2:
        case_no = int(sys.argv[1])
        items = [items[case_no]]
        print(f"Running verification case {case_no}")
    elif num_argv == 3:
        cases_no_start = int(sys.argv[1])
        cases_no_stop = int(sys.argv[2])
        items = items[cases_no_start:cases_no_stop]
        print(
            f"Running verification cases ranging from {cases_no_start} to {cases_no_stop}"
        )
    else:
        print(f"Error: Invalid number of arguments provided: {sys.argv}")
        return

