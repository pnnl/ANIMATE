PROJECT_DIR 	:= $(PWD)
RESULTS_DIR 	:= $(PROJECT_DIR)/results
INPUT_DIR		:= $(PROJECT_DIR)/../buildings
SINGULARITY 	:= /share/apps/singularity/3.6.3/bin/singularity
EPLUS_VERSION 	:= 9.6.0
IN_FILES    	:= $(notdir $(wildcard $(INPUT_DIR)/base*.json))
OUT_FILES   	:= $(subst .json,_md.json,$(IN_FILES))

$(RESULTS_DIR)/%_md.json: $(INPUT_DIR)/%.json
	@cd ./src/; python ./run_sim_for_cases.py $(INPUT_DIR)/`basename $<`
	@mkdir -p ../buildings/$(basename $(<F))_injected_BatchVerification
	@/qfs/projects/BECP/bin/qwait -A animate $(SINGULARITY) exec -B $(PROJECT_DIR)/..:/tmp ./energyplus_$(EPLUS_VERSION).sif energyplus -w /tmp/buildings/$(basename $(<F))_injected_BatchVerification.epw -r -p eplus -d /tmp/buildings/$(basename $(<F))_injected_BatchVerification /tmp/buildings/$(basename $(<F))_injected_BatchVerification.idf
	@mv ../buildings/$(basename $(<F))_injected_BatchVerification.idf ../buildings/$(basename $(<F))_injected_BatchVerification/in.idf
	@cd ./src/; python ./run_verification_case.py $(INPUT_DIR)/$(basename $(<F)).json

out: $(addprefix $(RESULTS_DIR)/,$(OUT_FILES))

all:
	cd ./src/; python ./verification_cases_split.py;
	$(SINGULARITY) pull -F docker://nrel/energyplus:$(EPLUS_VERSION)
	$(MAKE) -k -j 240 out
	cd ./src/; python ./summarize_md.py
