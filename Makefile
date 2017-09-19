################################################################################
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


################################################################################
# GLOBAL VARIABLES
#
# This section lays out some global and high-level commands for the Makefile;
# you can edit them if you like
################################################################################

# ----- You can edit these if you want ------
PY_INTERP = python # this may need to be python3 on your machine
PDF_VIEWER = Preview # change this to your PDF viewer of choice
JUP_INTERP = jupyter nbconvert --execute --ExecutePreprocessor.timeout=-1  # Probably don't change this

# ----- Define the directories -- better not to edit ------
FIGDIR=_figs
DERIVEDDIR=_data/derived
IDXDIR=_data/indices
RAINDIR=_data/rainfall
CLIMDIR=_data/reanalysis
S2SDIR=_data/s2s

GETDIR=01-Get
PROCDIR=02-Process
PLTDIR=03-Analyze-Plot
WRITEDIR=04-Writeup

# ----- Make commands you can run -----

## Create required folders, set up conda environment pyfloods, and activate it. RUN ONLY YOUR FIRST TIME.
setup	:	dirs environment

## Get data, process it, and create plots
output	: get process plot

## View all figures
viewfigs:
	open -a $(PDF_VIEWER) $(FIGDIR)/*.pdf

## Create a draft of the article from latex
tex: plot
	latexmk -cd -e -f -pdf -interaction=nonstopmode "$(WRITEDIR)/paper.tex"

################################################################################
# SETUP
#
# This section defines commands to create the desired conda environment
# and to create all required folders
################################################################################

# running make dirs will create these directories if they don't exist already
dirs	:
	mkdir -p $(FIGDIR)
	mkdir -p $(DERIVEDDIR) # derived data
	mkdir -p $(IDXDIR) # daily and monthly climate indices
	mkdir -p $(RAINDIR)/raw $(RAINDIR)/subset # rainfall data
	mkdir -p $(CLIMDIR)/raw $(CLIMDIR)/subset # reanalysis data
	mkdir -p $(S2SDIR) # s2s model data

# running make environment will create the custom conda environment
environment	:
	conda env create --f environment.yml
	source activate pyfloods
	conda install -c conda-forge cartopy eofs netcdf4 windspharm
	pip install git+git://github.com/jdossgollin/paraguayfloodspy@master

################################################################################
# STEP 01: GET RAW DATA
#
# This section defiines steps to access raw data
################################################################################

# The names of the files
PSI_RAW=$(wildcard $(CLIMDIR/raw/streamfunc_850_*.nc)) # raw yearly global 850 hPa streamfunction
RAIN_RAW=$(wildcard $(RAINDIR/raw/cpc_*.nc)) # raw yearly global CPC rain data
DAILYIDX=$(IDXDIR)/daily_indices.csv # daily MJO indices
MONTHLYIDX=$(IDXDIR)/monthly_indices.csv # monthly ENSO indices
S2SAA=$(S2SDIR)/AreaAvg.nc # Area-averaged S2S forecasts over target region

$(PSI_RAW)	:	$(GETDIR)/Reanalysis.py
	$(PY_INTERP) $<
	touch $@
$(RAIN_RAW)	:	$(GETDIR)/Rainfall.py
	$(PY_INTERP) $<
	touch $@
$(DAILYIDX)	:	$(GETDIR)/DailyIndices.py
	$(PY_INTERP) $<
$(MONTHLYIDX)	:	$(GETDIR)/MonthlyIndices.py
	$(PY_INTERP) $<
$(S2SAA)	:	$(GETDIR)/S2S-Data.py
	$(PY_INTERP) $<
	touch $@

# Get raw data
get	: $(DAILYIDX) $(PSI_RAW) $(RAIN_RAW) $(DAILYIDX) $(MONTHLYIDX) $(S2SAA)

################################################################################
# STEP 02: PROCESS DATA TO GET DERIVED DATA
#
# Get climatology/anomalies of data over a useful area, and
# perform weather typing
################################################################################

WTYPES=$(DERIVEDDIR)/WeatherTypes.csv
RAINSUB=$(RAINDIR)/*.nc
CLIMSUB=$(CLIMDIR)/*.nc

$(WTYPES)	:	$(PROCDIR)/Get-WTs.ipynb
	$(JUP_INTERP) $<
$(RAINSUB) $(CLIMSUB)	:	$(PROCDIR)/Anomalies.py
	$(PY_INTERP) $<
	touch $@

# get derived variables
process	:	get $(WTYPES) $(RAINSUB) $(CLIMSUB)

################################################################################
# STEP 03: RUN ALL THE JUPYTER NOTEBOOKS in 03-Analyze-Plot
#
# This wil generate the required figures
################################################################################

nbs = $(wildcard $(PLTDIR)/*.ipynb)
nb_htmls = $(nbs:%.ipynb=%.html)
$(PLTDIR)/%.html	: $(PLTDIR)/%.ipynb
	$(JUP_INTERP) $<

# create analysis and plots
plot	:	get process $(nb_htmls)


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
