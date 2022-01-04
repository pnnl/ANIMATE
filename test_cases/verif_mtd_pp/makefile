THIS_DIR	:= /qfs/projects/animate/parallel_sim_tests/test_1/test_cases/verif_mtd_pp
RUNEPLUS	:= /qfs/projects/BECP/bin/runeplus

INPUT_DIR	:= $(THIS_DIR)/idfs
OUTPUT_DIR	:= $(THIS_DIR)/idfs
WEATHER_DIR	:= /qfs/projects/BECP/weather/EnergyPlus/tmy3.new/all

IN_FILES    	:= $(notdir $(wildcard $(INPUT_DIR)/*.idf))	
OUT_FILES   	:= $(subst .idf,.table.csv.gz,$(IN_FILES))

$(OUTPUT_DIR)/%.table.csv.gz: $(INPUT_DIR)/%.idf
	@mkdir $(subst .idf,,./idfs/`basename $<`)
	@/qfs/projects/BECP/bin/qwait -A animate $(RUNEPLUS) -w $(WEATHER_DIR) -v 9.0 -x eso,mtd,mtr,mdd,bnd,svg,zsz,ssz -z -o $* -i $(INPUT_DIR) -p $(subst .idf,,./idfs/`basename $<`) `basename $<`

out: $(addprefix $(OUTPUT_DIR)/,$(OUT_FILES))

all:
	$(MAKE) -k -j 2 out
	
