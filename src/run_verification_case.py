from workflowsteps import *
from library import *
from datetimeep import DateTimeEP
import sys, os, json
from tqdm import tqdm


def run_verification_case(item_dict, run_path_postfix=""):
    item = build_an_item(item_dict)
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
        run_path = f"{run_path}{run_path_postfix}_injected_BatchVerification"

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
    # outcome = verification_obj.get_checks
    # verification_obj.plot(plot_option)
    md_content = verification_obj.add_md(None, "../results/imgs", "./imgs", item_dict)
    return {int(item_dict["no"]): md_content}


def main():
    num_argv = len(sys.argv)
    if num_argv == 1:
        print("No command line argument provided, ABORT!")
        return
    cases_path = sys.argv[1]
    lib_items_path = "../schema/library.json"
    items = assemble_verification_items(
        cases_path=cases_path, lib_items_path=lib_items_path
    )

    if num_argv == 2:
        print(f"Running all verification cases in {cases_path}")
    elif num_argv == 3:
        case_no = int(sys.argv[2])
        items = [items[case_no]]
        print(
            f"Running verification case sequence no {case_no} (not case id) for {cases_path}"
        )
    elif num_argv == 4:
        cases_no_start = int(sys.argv[2])
        cases_no_stop = int(sys.argv[3])
        items = items[cases_no_start:cases_no_stop]
        print(
            f"Running verification cases sequence no ranging from {cases_no_start} to {cases_no_stop} (not case id) for {cases_path}"
        )
    else:
        print(f"Error: Invalid number of arguments provided: {sys.argv}")
        return

    rp_postfix = "_" + cases_path.strip().replace(".json", "").split("_")[-1]

    md_dict = {}
    for item in tqdm(items):
        print(json.dumps(item, indent=2))
        this_dict = run_verification_case(item, run_path_postfix=rp_postfix)
        md_dict.update(this_dict)

    cases_name = cases_path.split("/")[-1].replace(".json", "").strip()
    cases_file = f"../results/{cases_name}_md.json"

    print(f"DONE! Saving markdown results to {cases_file}")
    with open(cases_file, "w") as fw:
        json.dump(md_dict, fw)


if __name__ == "__main__":
    main()
