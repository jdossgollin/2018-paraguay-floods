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
	open -a $(PDF_VIEWER) figs/*

## create everything in the analysis
all: dirs get process analyze

################################################################################
# MAKE SETUP
#
# This section defines commands to create the desired conda environment
# and to create all required folders
################################################################################

# Input parameters from other files
include config/*.mk

## Create all directories that the system expects
dirs	:
	mkdir -p figs tables data data/external data/processed

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

# We name these variables because they are called in analysis section
ELEV = data/external/elevation.nc # gridded elevation data
SST = data/external/ssta_cmb.nc # sst anomalies
MJO = data/external/mjo.nc # MJO data
NINO34 = data/external/nino34.nc # NINO 3.4 Index
S2SAA = data/external/s2s_area_avg.nc # ECMWF S2S model area-averaged over LPRB

CPC_RAW: $(patsubst %,data/external/cpc_rain_%.nc,$(YEARS))
data/external/cpc_rain_%.nc : src/get/download_cpc_year.py
	$(PY_INTERP) $< --year $* --outfile $@

UWND_RAW: $(patsubst %,data/external/reanalysisv2_uwnd_850_%.nc,$(YEARS))
data/external/reanalysisv2_uwnd_850_%.nc : src/get/download_reanalysis_year.py
	$(PY_INTERP) $< --year $* --coord_system pressure --var uwnd --level 850 --outfile $@

VWND_RAW: $(patsubst %,data/external/reanalysisv2_vwnd_850_%.nc,$(YEARS))
data/external/reanalysisv2_vwnd_850_%.nc : src/get/download_reanalysis_year.py
	$(PY_INTERP) $< --year $* --coord_system pressure --var vwnd --level 850 --outfile $@

$(ELEV)	: src/get/download_elevation.py
	$(PY_INTERP) $< --outfile $@

$(SST)	:	src/get/download_ssta.py
	$(PY_INTERP) $< --outfile $@

$(MJO)	: src/get/download_mjo.py
	$(PY_INTERP) $< --syear $(SYEAR) --eyear $(EYEAR) --outfile $@

$(NINO34)	: src/get/download_nino34.py
	$(PY_INTERP) $< --syear $(SYEAR) --eyear $(EYEAR) --outfile $@

$(S2SAA)	: src/get/download_s2s_area_avg.py config/rpy_region.mk
	$(PY_INTERP) $< --outfile $@ --year 2015 --X0 $(LPRX0) --X1 $(LPRX1) --Y0 $(LPRY0) --Y1 $(LPRY1)

## Download all external data
get: CPC_RAW UWND_RAW VWND_RAW $(ELEV) $(SST) $(MJO) $(NINO34) $(S2SAA)

################################################################################
# PROCESSED DATA
#
# Get derived variables, calculate anomalies, and get time series for specific regions
################################################################################

PSI_RAW: $(patsubst %,data/processed/reanalysisv2_psi_850_%.nc,$(YEARS))
data/processed/reanalysisv2_psi_850_%.nc : src/process/calculate_streamfunction.py data/external/reanalysisv2_uwnd_850_%.nc data/external/reanalysisv2_vwnd_850_%.nc
	$(PY_INTERP) $< --uwnd "data/external/reanalysisv2_uwnd_850_$*.nc" --vwnd "data/external/reanalysisv2_vwnd_850_$*.nc" --outfile $@

# We name these variables because they are called in analysis section
RAIN = data/processed/rain.nc # rainfall raw + anomaly
PSI = data/processed/streamfunction.nc # streamfunction raw + anomaly
UWND = data/processed/uwnd.nc # zonal wind raw + anomaly
VWND = data/processed/vwnd.nc # meridional wind raw + anomaly
RAIN_RPY = data/processed/rain_rpy.nc # area-averaged rain over LPRB
PSI_WT = data/processed/psi_wtype.nc # streamfunction over WT region
WT = data/processed/weather_type.nc # weather type sequence
DIPOLE = data/processed/scad.nc # south central atlantic dipole

$(RAIN)	:	src/process/make_anomaly.py data/external/cpc_rain_*.nc config/time.mk config/rain_region.mk
	$(PY_INTERP) $< --syear $(SYEAR) --eyear $(EYEAR) --path "data/external/cpc_rain_*.nc" --X0 $(RAINX0) --X1 $(RAINX1) --Y0 $(RAINY0) --Y1 $(RAINY1) --to_daily 0 --outfile $(RAIN)

$(PSI)	:	src/process/make_anomaly.py data/processed/reanalysisv2_psi_850_*.nc config/time.mk config/reanalysis_region.mk
	$(PY_INTERP) $< --syear $(SYEAR) --eyear $(EYEAR) --path "data/processed/reanalysisv2_psi_850_*.nc" --X0 $(RNLSX0) --X1 $(RNLSX1) --Y0 $(RNLSY0) --Y1 $(RNLSY1) --to_daily 1 --outfile $(PSI)

$(UWND)	:	src/process/make_anomaly.py data/external/reanalysisv2_uwnd_850_*.nc config/time.mk config/reanalysis_region.mk
	$(PY_INTERP) $< --syear $(SYEAR) --eyear $(EYEAR) --path "data/external/reanalysisv2_uwnd_850_*.nc" --X0 $(RNLSX0) --X1 $(RNLSX1) --Y0 $(RNLSY0) --Y1 $(RNLSY1) --to_daily 1 --outfile $(UWND)

$(VWND)	:	src/process/make_anomaly.py data/external/reanalysisv2_vwnd_850_*.nc config/time.mk config/reanalysis_region.mk
	$(PY_INTERP) $< --syear $(SYEAR) --eyear $(EYEAR) --path "data/external/reanalysisv2_vwnd_850_*.nc" --X0 $(RNLSX0) --X1 $(RNLSX1) --Y0 $(RNLSY0) --Y1 $(RNLSY1) --to_daily 1 --outfile $(VWND)

$(RAIN_RPY)	: src/process/make_time_series.py $(RAIN)
	$(PY_INTERP) $< --infile $(RAIN) --X0 $(LPRX0) --X1 $(LPRX1) --Y0 $(LPRY0) --Y1 $(LPRY1) --outfile $(RAIN_RPY)

$(PSI_WT)	: src/process/make_subset.py data config/wt_region.mk $(PSI)
	$(PY_INTERP) $< --infile $(PSI) --X0 $(WTX0) --X1 $(WTX1) --Y0 $(WTY0) --Y1 $(WTY1) --outfile $(PSI_WT)

WT_CI: $(patsubst %,data/processed/wt_k_%.nc,$(WTK))
data/processed/wt_k_%.nc	:	src/process/make_weather_type.py data/processed/psi_wtype.nc config/wtype2.mk
	$(PY_INTERP) $< --infile data/processed/psi_wtype.nc --var_xpl $(VARXPL2) --n_cluster $* --n_sim $(NSIM2) --outfile $@

$(WT) tables/weather_type_centroid.tex : src/process/make_weather_type.py data/processed/psi_wtype.nc config/wtype.mk
	$(PY_INTERP) $< --infile data/processed/psi_wtype.nc --var_xpl $(VARXPL) --n_cluster $(NCLUS) --n_sim $(NSIM) --outfile data/processed/weather_type.nc --table tables/weather_type_centroid.tex

$(DIPOLE)	:	src/process/make_dipole.py config/dipole_region.mk $(SST)
	$(PY_INTERP) $< --infile $(SST) --outfile $(DIPOLE) --X0 $(SCADX0) --X1 $(SCADX1) --Y0 $(SCADY0) --Y1 $(SCADY1)

## Get all the processed data
process: PSI_RAW $(RAIN) $(PSI) $(UWND) $(VWND) $(RAIN_RPY) $(PSI_WT) WT_CI $(WT) tables/weather_type_centroid.tex $(DIPOLE)

################################################################################
# Self-Documenting Help Commands
#
# This section contains codes to build automatic help in the makefile
# Copied nearly verbatim from cookiecutter-data-science, in turn taken from
# <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
################################################################################

.DEFAULT_GOAL := help
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
