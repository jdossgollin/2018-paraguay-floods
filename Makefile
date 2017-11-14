# MAKEFILE for PYFLOODSPY
#
# This is a Makefile written by James Doss-Gollin (Columbia University)
# Please see README.md for documentation.
# To run:
# - (first time only): make setup
# - to run codes and make plots: make output
# - to view figures: make viewfigs
# - to generate a PDF of our writeup: make tex
# - unsure: make help

################################################################################
# GLOBAL VARIABLES
#
# This section lays out some global and high-level commands for the Makefile;
# you can edit them if you like
################################################################################

# ----- How to run the commands ------
PY_INTERP = python # this may need to be python3 on your machine
PDF_VIEWER = Preview # change this to your PDF viewer of choice
JUP_INTERP = jupyter nbconvert --execute --ExecutePreprocessor.timeout=-1  # Probably don't change this

# ----- Make commands you can run -----

## Create required folders, set up conda environment pyfloods, and activate it. RUN ONLY YOUR FIRST TIME.
setup	:	dirs environment

## Get data, process it, and create plots
output	: get derive plot

## View all figures
viewfigs:
	open -a $(PDF_VIEWER) $(DIR_FIG)/*.pdf

## Create a draft of the article from latex
tex: plot
	latexmk -cd -e -f -pdf -interaction=nonstopmode "$(DIR_TEX)/paper.tex"
	latexmk -cd -e -f -pdf -interaction=nonstopmode "$(DIR_TEX)/Supplement.tex"

################################################################################
# SETUP
#
# This section defines commands to create the desired conda environment
# and to create all required folders
################################################################################

# Define the directories
DIR_ACCESS=scripts/access
DIR_ACCESSED=data/accessed
DIR_DERIVE=scripts/derive
DIR_DERIVED=data/derived
DIR_FIG=figs
DIR_TEX=writeup
DIR_PLT=analysis
DIR_CONFIG=config

# Parameters of the analysis
include $(DIR_CONFIG)/*.mk
YEARS := $(shell seq $(SYEAR) 1 $(EYEAR)) # don't edit this!!

# running make dirs will create these directories if they don't exist already
dirs	:
	mkdir -p $(DIR_FIG)
	mkdir -p $(DIR_ACCESSED)/cpc $(DIR_ACCESSED)/ncar $(DIR_DERIVED)

# running make environment will create the custom conda environment
environment	:
	conda update -y conda;\
	conda env create --file environment.yml;\
	source activate pyfloods;\
	conda install -yc conda-forge cartopy eofs nbstripout netcdf4 windspharm;\
	nbstripout --install --attributes .gitattributes;\
	pip install git+git://github.com/jdossgollin/paraguayfloodspy@master

################################################################################
# STEP 01: GET RAW DATA
#
# This section defiines steps to access raw data
# The make on the PSI_RAW_850 and RAIN_RAW comes from Stack Overflow user @MadScientist
# https://stackoverflow.com/questions/46307292/makefile-generate-target-from-numeric-sequence?stw=2
# Thanks!!!
################################################################################

PSI_RAW_850: $(patsubst %,$(DIR_ACCESSED)/ncar/streamfunc_850_%.nc,$(YEARS)) # The psi files
RAIN_RAW: $(patsubst %,$(DIR_ACCESSED)/cpc/cpc_%.nc,$(YEARS)) # the rain files
DAILYIDX = $(DIR_ACCESSED)/daily_indices.csv # Daily MJO Indices
MONTHLYIDX = $(DIR_ACCESSED)/monthly_indices.csv # monthly ENSO indices
S2SAA = $(DIR_ACCESSED)/AreaAvg.nc # Area-averaged S2S forecasts over target region
ELEV = $(DIR_ACCESSED)/elevation.nc

$(DIR_ACCESSED)/ncar/streamfunc_850_%.nc: $(DIR_ACCESS)/StreamfuncYear.py
	$(PY_INTERP) $< --year $* --level 850 --outfile $@

$(DIR_ACCESSED)/cpc/cpc_%.nc: $(DIR_ACCESS)/CPCRainYear.py
	$(PY_INTERP) $< --year $* --outfile $@

$(DAILYIDX)	:	$(DIR_ACCESS)/DailyIndices.py $(DIR_CONFIG)/Time.mk
	$(PY_INTERP) $< --years $(SYEAR) $(EYEAR) --outfile $@

$(MONTHLYIDX)	:	$(DIR_ACCESS)/MonthlyIndices.py $(DIR_CONFIG)/Time.mk
	$(PY_INTERP) $< --years $(SYEAR) $(EYEAR) --outfile $@

$(S2SAA)	:	$(DIR_ACCESS)/S2S-Data.py $(DIR_CONFIG)/RioParaguay.mk
	$(PY_INTERP) $< --lonlim $(RPEAST) $(RPWEST) --latlim $(RPNORTH) $(RPSOUTH) --outfile $@

$(ELEV)	:	$(DIR_ACCESS)/Elevation.py
	$(PY_INTERP) $< --outfile $@

# Get raw data
get	: PSI_RAW_850 RAIN_RAW $(DAILYIDX) $(DAILYIDX) $(MONTHLYIDX) $(S2SAA) $(ELEV)

################################################################################
# STEP 02: PROCESS DATA TO GET DERIVED DATA
#
# Get climatology/anomalies of data over a useful area, and
# then perform weather typing
################################################################################

PSI_850 = $(DIR_DERIVED)/psi_850.nc # 850 hPa streamfunction over Southern Hemisphere
RAINSUB = $(DIR_DERIVED)/precip.nc # Rainfall over South America
RPYRAIN = $(DIR_DERIVED)/rainfall_rpy.nc # Area-averaged rainfall over Lower Paraguay River Basin
WTYPES = $(DIR_DERIVED)/WeatherTypes.csv # Weather types by date
WTLOG = $(DIR_DERIVED)/wtlog.txt # output from the weather typing function (so it's retained)

$(PSI_850)	:	$(DIR_DERIVE)/Anomalies.py $(DIR_ACCESSED)/ncar/streamfunc_850_*.nc $(DIR_CONFIG)/Reanalysis.mk $(DIR_CONFIG)/Time.mk
	$(PY_INTERP) $< --mode reanalysis --pattern '$(DIR_ACCESSED)/ncar/streamfunc_850_*.nc' --lonlim $(RWEST) $(REAST) --latlim $(RSOUTH) $(RNORTH) --years $(SYEAR) $(EYEAR) --outfile $@
$(RAINSUB)	:	$(DIR_DERIVE)/Anomalies.py $(DIR_ACCESSED)/cpc/cpc_*.nc $(DIR_CONFIG)/Rain.mk $(DIR_CONFIG)/Time.mk
	$(PY_INTERP) $< --mode rain --pattern '$(DIR_ACCESSED)/cpc/cpc_*.nc' --lonlim $(PWEST) $(PEAST) --latlim $(PSOUTH) $(PNORTH) --years $(SYEAR) $(EYEAR) --outfile $@
$(WTLOG) $(WTYPES)	:	$(DIR_DERIVE)/WeatherTypes.py $(PSI_850) config/WeatherTypes.mk
	$(PY_INTERP) $< --psi850 $(PSI_850) --lonlim $(WTEAST) $(WTWEST) --latlim $(WTNORTH) $(WTSOUTH) --ncluster $(WT_NCLUS) --pcscaling $(PC_SCALE) --wtprop $(WT_PROP) --nsim $(WTNSIM) --outfile $@ > $(WTLOG)
	cat $(WTLOG)
$(RPYRAIN)	: $(DIR_DERIVE)/AreaAveragedRain.py	$(RAINSUB) $(DIR_CONFIG)/RioParaguay.mk
	$(PY_INTERP) $< --infile $(RAINSUB) --lonlim $(RPWEST) $(RPEAST) --latlim $(RPNORTH) $(RPSOUTH) --outfile $@

# get derived variables
derive	:	$(PSI_850) $(RAINSUB) $(WTYPES) $(RPYRAIN) $(WTLOG)

################################################################################
# STEP 03: RUN ALL THE JUPYTER NOTEBOOKS TO MAKE PLOTS
#
# This will generate the required figures
# Any time that *any* of the "derived" data is updated, all notebooks will be
# re-executed.
################################################################################

nbs = $(wildcard $(DIR_PLT)/*.ipynb)
nb_htmls = $(nbs:%.ipynb=%.html)
$(DIR_PLT)/%.html	: $(DIR_PLT)/%.ipynb $(PSI_850) $(RAINSUB) $(WTYPES) $(DIR_CONFIG)/PlotParameters.py $(RPYRAIN)
	$(JUP_INTERP) $<

# create analysis and plots
plot	:	$(nb_htmls)


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
