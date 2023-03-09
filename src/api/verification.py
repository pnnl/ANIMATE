import sys, logging, multiprocessing, os

from typing import Dict, List, Tuple, Union

sys.path.append("..")

from .verification_case import *
from run_verification_case import *
from workflowsteps import *
from libcases import *


class Verification:
    def __init__(self, verification: VerificationCase = None):
        self.cases = None
        if verification is None:
            logging.error("A verification should be provided.")
        else:
            if isinstance(verification, VerificationCase):
                if len(verification.case_suite) == 0:
                    logging.error(f"The verification case suite is empty.")
                    return None
                else:
                    self.cases = verification.case_suite
            else:
                logging.error(
                    f"A VerificationCase should be provided not a {type(verification)}."
                )
                return None

    def configure(
        self,
        output_path: str = None,
        lib_items_path: str = None,
        plot_option: str = None,
        fig_size: tuple = None,
        num_threads: int = 1,
    ) -> None:
        if self.cases is None or len(self.cases) == 0:
            logging.error(
                "The verification case suite is empty, there is nothing to configure."
            )
            return None
        if lib_items_path is None:
            logging.error(
                "A path to the library of verification cases should be provided."
            )
            return None
        elif not isinstance(lib_items_path, str):
            logging.error("The path to the library of verification cases is not valid.")
            return None
        elif not os.path.isfile(lib_items_path):
            logging.error("The path to the library of verification cases is not valid.")
            return None

        if not plot_option in [
            None,
            "all-compact",
            "all-expand",
            "day-compact",
            "day-expand",
        ]:
            logging.error(
                f"The plot_option argument should either be all-compact, all-expand, day-compact, or day-expand, not {plot_option}."
            )

        if isinstance(fig_size, tuple):
            if not (
                (isinstance(fig_size[0], int) or isinstance(fig_size[0], float))
                and (isinstance(fig_size[1], int) or isinstance(fig_size[1], float))
            ):
                logging.error(
                    "The fig_size argument should be a tuple of integers or floats."
                )
                return None
        elif not fig_size is None:
            logging.error(
                f"The fig_size argument should be a tuple of integers or floats. Here is the variable type that was passed {type(fig_size)}."
            )
            return None

        if (isinstance(num_threads, int) and num_threads < 1) or (
            not isinstance(num_threads, int)
        ):
            logging.error("The number of threads should be an integer greater than 1.")

        self.output_path = output_path
        self.lib_items_path = lib_items_path
        self.plot_option = plot_option
        self.fig_size = fig_size
        self.num_threads = num_threads

    def run_single_verification(self, case):
        # Run verification
        items = assemble_verification_items(
            cases=case, lib_items_path=self.lib_items_path
        )
        results = run_libcase(
            item_dict=items[0],
            plot_option=self.plot_option,
            output_path=self.output_path,
            fig_size=self.fig_size,
            produce_outputs=True,
        )

        # Output case summary
        cases_file = f"{self.output_path}/{case['no']}.md"
        with open(cases_file, "w") as fw:
            fw.write(results[list(results.keys())[0]]["md_content"])

    def run(self) -> None:
        # Input validation
        if self.output_path is None:
            self.output_path = ""
        if self.cases is None or len(self.cases) == 0:
            logging.error(
                "The verification case suite is empty, there is nothing to configure."
            )
            return None

        # Run verifications
        with multiprocessing.Pool(len(self.cases)) as c:
            c.map(self.run_single_verification, self.cases.values())
