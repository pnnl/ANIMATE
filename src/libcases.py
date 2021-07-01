# %% Import packages
from workflowsteps import *
from library import *
from datetimeep import DateTimeEP


def run_libcase(item_dict):
    """Library case runner

    Args:
        item_dict (Dict): verification item dict loaded from json files through `assemble_verification_items`
    """

    item = build_an_item(item_dict)
    print(f"===========\nRunning case - {item.item['verification_class']}\n===========")

    idf_outputs = []
    idf_outputs.extend(read_injection_points(item))
    unique_output = combine_injection_points(idf_outputs)

    if "idf_objects" in item.points.keys():
        need_injection = True
    else:
        need_injection = False
    run_sim = item.item["run_simulation"]

    if need_injection or run_sim:
        original_idf_path = item.item["simulation_IO"]["idf"].strip()
        idd_path = item.item["simulation_IO"]["idd"].strip()
        run_path = f"{original_idf_path.split('.idf')[0]}"

    if need_injection:
        instrumented_idf_path = f"{original_idf_path.split('.idf')[0]}_injected.idf"
        run_path = f"{run_path}_injected"
        inject_idf(
            iddpath=idd_path,
            idfpath_in=original_idf_path,
            objstoinject=unique_output,
            idfpath_out=instrumented_idf_path,
        )
        run_idf_path = instrumented_idf_path
    elif run_sim:
        run_idf_path = original_idf_path

    if run_sim:
        weather_path = item.item["simulation_IO"]["weather"].strip()
        run_simulation(idfpath=run_idf_path, weatherpath=weather_path)
        print("simulation done")

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
    outcome = cls(df, parameters).get_checks


def main():
    cases_path = "../schema/library_verification_cases.json"
    lib_items_path = "../schema/library.json"
    items = assemble_verification_items(
        cases_path=cases_path, lib_items_path=lib_items_path
    )
    for item in items:
        run_libcase(item_dict=item)


if __name__ == "__main__":
    main()
