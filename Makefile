################################################################################
# GLOBAL VARIABLES
#
# This section lays out some global and high-level commands for the Makefile;
# you can edit them if you like
################################################################################

# commands to run
PY_INTERP = python
PDF_VIEWER = Preview
TEX_INTERP = latexmk -cd -e -f -pdf -interaction=nonstopmode

## Get data, process it, and create plots
output	: get derive plot

## View all figures
viewfigs:
	open -a $(PDF_VIEWER) $(DIR_FIG)/*.pdf

## create everything in the analysis
all: dirs get

################################################################################
# MAKE SETUP
#
# This section defines commands to create the desired conda environment
# and to create all required folders
################################################################################

# Define the directory structure
DIR_DATA=data
DIR_FIG=figs
DIR_CONFIG=config
DIR_SRC=src

# Input parameters from other files
include config/*.mk

## Create all directories that the system expects
dirs	:
	mkdir -p $(DIR_FIG) $(DIR_ACCESSED)

## Create and activate a conda environment pyfloods
environment	:
	conda update -y conda;\
	conda env create --file environment.yml;\
	conda activate pyfloods

################################################################################
# MAKE GET
#
# get all data from external sources that is required
################################################################################

CPC_RAW: $(patsubst %,data/external/cpc_rain_%.nc,$(YEARS))
data/external/cpc_rain_%.nc : src/download_cpc_year.py
	$(PY_INTERP) $< --year $* --outfile $@

UWND_RAW: $(patsubst %,data/external/reanalysisv2_uwnd_850_%.nc,$(YEARS))
data/external/reanalysisv2_uwnd_850_%.nc : src/download_reanalysis_year.py
	$(PY_INTERP) $< --year $* --coord_system pressure --var uwnd --level 850 --outfile $@

VWND_RAW: $(patsubst %,data/external/reanalysisv2_vwnd_850_%.nc,$(YEARS))
data/external/reanalysisv2_vwnd_850_%.nc : src/download_reanalysis_year.py
	$(PY_INTERP) $< --year $* --coord_system pressure --var vwnd --level 850 --outfile $@

data/external/elevation.nc	:
	wget -o $@ http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NGDC/.GLOBE/.topo/X/-180/0.025/180/GRID/Y/-90/0.025/90/GRID/data.nc

data/external/ssta_cmb.nc	:	src/download_ssta.py
	$(PY_INTERP) $< --outfile $@

data/external/mjo.nc	: src/download_mjo.py
	$(PY_INTERP) $< --syear $(SYEAR) --eyear $(EYEAR) --outfile $@

data/external/nino34.nc	: src/download_nino34.py
	$(PY_INTERP) $< --syear $(SYEAR) --eyear $(EYEAR) --outfile $@

data/external/s2s_area_avg.nc	: src/download_s2s_area_avg.py config/rain_region.mk
	$(PY_INTERP) $< --outfile $@ --year 2015 --X0 $(RAINX0) --X1 $(RAINX1) --Y0 $(RAINY0) --Y1 $(RAINY1)

## Download all external data
get: CPC_RAW UWND_RAW VWND_RAW data/external/elevation.nc data/external/ssta_cmb.nc data/external/mjo.nc data/external/nino34.nc data/external/s2s_area_avg.nc

################################################################################
# PROCESSED DATA
#
# Get derived variables, calculate anomalies, and get time series for specific regions
################################################################################

PSI_RAW: $(patsubst %,data/processed/reanalysisv2_psi_850_%.nc,$(YEARS))
data/processed/reanalysisv2_psi_850_%.nc : src/calculate_streamfunction.py data/external/reanalysisv2_uwnd_850_%.nc data/external/reanalysisv2_vwnd_850_%.nc
	$(PY_INTERP) $< --uwnd data/external/reanalysisv2_uwnd_850_$*.nc --vwnd data/external/reanalysisv2_vwnd_850_$*.nc --outfile $@

data/processed/rain.nc	:	src/make_anomaly.py data/external/cpc_rain_*.nc config/time.mk config/rain_region.mk
	$(PY_INTERP) $< --syear $(SYEAR) --eyear $(EYEAR) --path "data/external/cpc_rain_*.nc" --X0 $(RAINX0) --X1 $(RAINX1) --Y0 $(RAINY0) --Y1 $(RAINY1) --outfile $@

data/processed/streamfunction.nc	:	src/make_anomaly.py data/processed/reanalysisv2_psi_850_*.nc config/time.mk config/reanalysis_region.mk
	$(PY_INTERP) $< --syear $(SYEAR) --eyear $(EYEAR) --path "data/processed/reanalysisv2_psi_850_*.nc" --X0 $(RNLSX0) --X1 $(RNLSX1) --Y0 $(RNLSY0) --Y1 $(RNLSY1) --outfile $@

processed: PSI_RAW data/processed/rain.nc data/processed/streamfunction.nc

################################################################################
# Self-Documenting Help Commands
#
# This section contains codes to build automatic help in the makefile
# Copied nearly verbatim from cookiecutter-data-science, in turn taken from
# <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
################################################################################

.DEFAULT_GOAL := help

# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
