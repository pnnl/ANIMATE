PROJECT_DIR := $(PWD)
RESULTS_DIR := $(PROJECT_DIR)/results
THIS_DIR	:= $(PROJECT_DIR)/test_cases/verif_mtd_pp
THIS_DIR_REL := test_cases/verif_mtd_pp
SINGULARITY := /share/apps/singularity/3.6.3/bin/singularity
EPLUS_VERSION := 9.6.0

INPUT_DIR	:= $(THIS_DIR)
OUTPUT_DIR	:= $(THIS_DIR)/idfs
OUTPUT_DIR_REL := $(THIS_DIR_REL)/idfs

IN_FILES    	:= $(notdir $(wildcard $(INPUT_DIR)/base*.json))
OUT_FILES   	:= $(subst .json,_md.json,$(IN_FILES))
SIM_FOLDERS   := $(subst .json,_injected_BatchVerification,$(IN_FILES))

$(OUTPUT_DIR)/%_injected_BatchVerification: $(INPUT_DIR)/%.json
	@cd ./src/; python ./run_sim_for_cases.py $(INPUT_DIR)/`basename $<`
	@mkdir -p ../buildings/$(basename $(<F))_injected_BatchVerification

$(RESULTS_DIR)/%_md.json: $(INPUT_DIR)/%.json
	@/qfs/projects/BECP/bin/qwait -A animate $(SINGULARITY) exec -B $(PROJECT_DIR)/..:/tmp ./energyplus_$(EPLUS_VERSION).sif energyplus -w /tmp/buildings/$(basename $(<F))_injected_BatchVerification.epw -r -p eplus -d /tmp/buildings/$(basename $(<F))_injected_BatchVerification /tmp/buildings/$(basename $(<F))_injected_BatchVerification.idf
	@mv ../buildings/$(basename $(<F))_injected_BatchVerification.idf ../buildings/$(basename $(<F))_injected_BatchVerification/in.idf
	@cd ./src/; cp ./run_verification_case.py ./run_verification_case_$(basename $(<F)).py; python ./run_verification_case_$(basename $(<F)).py $(INPUT_DIR)/$(basename $(<F)).json

prep: $(addprefix $(OUTPUT_DIR)/,$(SIM_FOLDERS))

sims_verifs: $(addprefix $(RESULTS_DIR)/,$(OUT_FILES))

all:
	cd $(THIS_DIR); python ./create_test_cases.py                                           # Create verification
	cd ./src/; python ./verification_cases_split.py;                                        # Split verification cases
	mv $(THIS_DIR)/verification_cases.json ./results/verification_cases.json                # Move verification cases
	$(MAKE) -k -j 240 prep                                                                  # Initialize verification cases
	$(SINGULARITY) pull docker://nrel/energyplus:$(EPLUS_VERSION)                           # Retrieve EnergyPlus Singularity image (only works on constance7a)
	$(MAKE) -k -j 240 sims_verifs                                                           # Run "injected" simulations and perform verifications
	cd ./src/; python ./summarize_md.py                                                     # Create summary
