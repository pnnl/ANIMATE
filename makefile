PROJECT_DIR := /qfs/projects/animate/parallel_sim_tests/test_2
RESULTS_DIR := $(PROJECT_DIR)/results
THIS_DIR	:= $(PROJECT_DIR)/test_cases/verif_mtd_pp
RUNEPLUS	:= /qfs/projects/BECP/bin/runeplus

INPUT_DIR	:= $(THIS_DIR)
OUTPUT_DIR	:= $(THIS_DIR)/idfs
MASK := /ASHRAE
WEATHER_DIR	:= /qfs/projects/BECP/weather/EnergyPlus/tmy3.new/all

IN_FILES    	:= $(notdir $(wildcard $(INPUT_DIR)/ASHRAE*.json))
OUT_FILES   	:= $(subst .json,_md.json,$(IN_FILES))

$(RESULTS_DIR)/%_md.json: $(INPUT_DIR)/%.json
	@cd ./src/; python ./run_sim_for_cases.py $(INPUT_DIR)/`basename $<`
	@mkdir $(subst .json,,./test_cases/verif_mtd_pp/idfs/`basename $<`_injected_BatchVerification)
	@/qfs/projects/BECP/bin/qwait -A animate $(RUNEPLUS) -w $(WEATHER_DIR) -v 9.0 -x eso,mtd,mtr,mdd,bnd,svg,zsz,ssz -o eplusout -i $(INPUT_DIR)/idfs -p $(INPUT_DIR)/idfs/$(basename $(<F))_injected_BatchVerification $(basename $(<F))_injected_BatchVerification.idf
	@mv $(INPUT_DIR)/idfs/$(basename $(<F))_injected_BatchVerification.idf $(INPUT_DIR)/idfs/$(basename $(<F))_injected_BatchVerification/in.idf
	@cd ./src/; python ./run_verification_case.py $(INPUT_DIR)/$(basename $(<F)).json

out: $(addprefix $(RESULTS_DIR)/,$(OUT_FILES))

all:
	cd ./test_cases/verif_mtd_pp/; python ./create_test_cases.py
	cd ./src/; python ./verification_cases_split.py;
	$(MAKE) -k -j 10 out
	cd ./src/; python ./summarize_md.py
