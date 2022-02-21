PROJECT_DIR := $(PWD)
RESULTS_DIR := $(PROJECT_DIR)/results
THIS_DIR	:= $(PROJECT_DIR)/cases
RUNEPLUS	:= /qfs/projects/BECP/doe_bldg_tools_V2/bin/runeplus

INPUT_DIR	:= $(THIS_DIR)
OUTPUT_DIR	:= ../buildings
WEATHER_DIR	:= ../weather_files

IN_FILES    	:= $(notdir $(wildcard $(INPUT_DIR)/base*.json))
OUT_FILES   	:= $(subst .json,_md.json,$(IN_FILES))

$(RESULTS_DIR)/%_md.json: $(INPUT_DIR)/%.json
	@cd ./src/; python ./run_sim_for_cases.py $(INPUT_DIR)/`basename $<`
	@mkdir -p $(subst .json,,../buildings/`basename $<`_injected_BatchVerification)
	/qfs/projects/BECP/bin/qwait -A animate $(RUNEPLUS) -w $(WEATHER_DIR) -v 9.6.0 -x eso,mtd,mtr,mdd,bnd,svg,zsz,ssz -o eplusout -i ../buildings -p ../buildings/$(basename $(<F))_injected_BatchVerification $(basename $(<F))_injected_BatchVerification.idf
	@mv ../buildings/$(basename $(<F))_injected_BatchVerification.idf ../buildings/$(basename $(<F))_injected_BatchVerification/in.idf
	@cd ./src/; python ./run_verification_case.py $(INPUT_DIR)/$(basename $(<F)).json

out: $(addprefix $(RESULTS_DIR)/,$(OUT_FILES))

all:
	cd ./src/; python ./verification_cases_split.py;
	$(MAKE) -k -j 1 out
	cd ./src/; python ./summarize_md.py
