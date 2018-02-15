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
	mkdir -p figs data data/external data/processed

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
data/external/cpc_rain_%.nc : src/get/download_cpc_year.py
	$(PY_INTERP) $< --year $* --outfile $@

UWND_RAW: $(patsubst %,data/external/reanalysisv2_uwnd_850_%.nc,$(YEARS))
data/external/reanalysisv2_uwnd_850_%.nc : src/get/download_reanalysis_year.py
	$(PY_INTERP) $< --year $* --coord_system pressure --var uwnd --level 850 --outfile $@

VWND_RAW: $(patsubst %,data/external/reanalysisv2_vwnd_850_%.nc,$(YEARS))
data/external/reanalysisv2_vwnd_850_%.nc : src/get/download_reanalysis_year.py
	$(PY_INTERP) $< --year $* --coord_system pressure --var vwnd --level 850 --outfile $@

data/external/elevation.nc	: src/get/download_elevation.py
	$(PY_INTERP) $< --outfile $@

data/external/ssta_cmb.nc	:	src/get/download_ssta.py
	$(PY_INTERP) $< --outfile $@

data/external/mjo.nc	: src/get/download_mjo.py
	$(PY_INTERP) $< --syear $(SYEAR) --eyear $(EYEAR) --outfile $@

data/external/nino34.nc	: src/get/download_nino34.py
	$(PY_INTERP) $< --syear $(SYEAR) --eyear $(EYEAR) --outfile $@

data/external/s2s_area_avg.nc	: src/get/download_s2s_area_avg.py config/rpy_region.mk
	$(PY_INTERP) $< --outfile $@ --year 2015 --X0 $(LPRX0) --X1 $(LPRX1) --Y0 $(LPRY0) --Y1 $(LPRY1)

## Download all external data
get: CPC_RAW UWND_RAW VWND_RAW data/external/elevation.nc data/external/ssta_cmb.nc data/external/mjo.nc data/external/nino34.nc data/external/s2s_area_avg.nc

################################################################################
# PROCESSED DATA
#
# Get derived variables, calculate anomalies, and get time series for specific regions
################################################################################

PSI_RAW: $(patsubst %,data/processed/reanalysisv2_psi_850_%.nc,$(YEARS))
data/processed/reanalysisv2_psi_850_%.nc : src/process/calculate_streamfunction.py data/external/reanalysisv2_uwnd_850_%.nc data/external/reanalysisv2_vwnd_850_%.nc
	$(PY_INTERP) $< --uwnd data/external/reanalysisv2_uwnd_850_$*.nc --vwnd data/external/reanalysisv2_vwnd_850_$*.nc --outfile $@

data/processed/rain.nc	:	src/process/make_anomaly.py data/external/cpc_rain_*.nc config/time.mk config/rain_region.mk
	$(PY_INTERP) $< --syear $(SYEAR) --eyear $(EYEAR) --path "data/external/cpc_rain_*.nc" --X0 $(RAINX0) --X1 $(RAINX1) --Y0 $(RAINY0) --Y1 $(RAINY1) --outfile $@

data/processed/streamfunction.nc	:	src/process/make_anomaly.py data/processed/reanalysisv2_psi_850_*.nc config/time.mk config/reanalysis_region.mk
	$(PY_INTERP) $< --syear $(SYEAR) --eyear $(EYEAR) --path "data/processed/reanalysisv2_psi_850_*.nc" --X0 $(RNLSX0) --X1 $(RNLSX1) --Y0 $(RNLSY0) --Y1 $(RNLSY1) --to_daily 1 --outfile $@

data/processed/rain_rpy.nc: src/process/make_time_series.py data/processed/rain.nc
	$(PY_INTERP) $< --infile data/processed/rain.nc --X0 $(LPRX0) --X1 $(LPRX1) --Y0 $(LPRY0) --Y1 $(LPRY1) --outfile $@

data/processed/psi_wtype.nc: src/process/make_subset.py data/processed/streamfunction.nc
	$(PY_INTERP) $< --infile data/processed/streamfunction.nc --X0 $(WTX0) --X1 $(WTX1) --Y0 $(WTY0) --Y1 $(WTY1) --outfile $@

WT_CI: $(patsubst %,data/processed/wt_k_%.nc,$(WTK))
data/processed/wt_k_%.nc	:	src/process/make_weather_type.py data/processed/psi_wtype.nc config/wtype2.mk
	$(PY_INTERP) $< --infile data/processed/psi_wtype.nc --var_xpl $(VARXPL2) --n_cluster $* --n_sim $(NSIM2) --outfile $@

data/processed/weather_type.nc: src/process/make_weather_type.py data/processed/psi_wtype.nc config/wtype.mk
	$(PY_INTERP) $< --infile data/processed/psi_wtype.nc --var_xpl $(VARXPL) --n_cluster $(NCLUS) --n_sim $(NSIM) --outfile $@

## Get all the processed data
process: PSI_RAW data/processed/rain.nc data/processed/streamfunction.nc data/processed/rain_rpy.nc data/processed/psi_wtype.nc WT_CI data/processed/weather_type.nc

################################################################################
# MAKE PLOTS AND TABLES (ANALYSIS)
#
# Each plot or table is created from a separate file with corresponding name
################################################################################

figs/study_area.jpg	:	src/analyze/plot_study_area.py config/wt_region.mk config/rpy_region.mk data/external/elevation.nc
	$(PY_INTERP) $< --outfile $@ --LPRX0 $(LPRX0) --LPRX1 $(LPRX1) --LPRY0 $(LPRY0) --LPRY1 $(LPRY1) --WTX0 $(WTX0) --WTX1 $(WTX1) --WTY0 $(WTY0) --WTY1 $(WTY1)

figs/lagged_rain.pdf	:	src/analyze/plot_lagged_rain.py data/processed/rain.nc data/processed/rain_rpy.nc data/processed/streamfunction.nc
	$(PY_INTERP) $< --outfile $@ --prcp_rpy data/processed/rain_rpy.nc --psi data/processed/streamfunction.nc --rain data/processed/rain.nc

figs/anomalies_ndjf1516.pdf	:	src/analyze/plot_anom_1516.py data/processed/rain.nc data/processed/rain_rpy.nc data/processed/streamfunction.nc
	$(PY_INTERP) $< --outfile $@ --psi data/processed/streamfunction.nc --rain data/processed/rain.nc

figs/eof_loadings.pdf	:	src/analyze/plot_leading_eofs.py data/processed/psi_wtype.nc
	$(PY_INTERP) $< --outfile $@ --psi_wtype data/processed/psi_wtype.nc --n_eof 4

figs/rain_wt_201516.pdf	:	src/analyze/plot_wt_rain.py data/processed/weather_type.nc data/processed/rain_rpy.nc
	$(PY_INTERP) $< --outfile $@ --prcp_rpy data/processed/rain_rpy.nc --wt data/processed/weather_type.nc

figs/wt_composite.pdf	:	src/analyze/plot_wt_composite.py data/processed/weather_type.nc data/processed/rain.nc data/processed/streamfunction.nc
	$(PY_INTERP) $< --outfile $@ --wt data/processed/weather_type.nc --rain data/processed/rain.nc --psi data/processed/streamfunction.nc

figs/klee.pdf	:	src/analyze/plot_klee.py data/processed/weather_type.nc
	$(PY_INTERP) $< --outfile $@ --wt data/processed/weather_type.nc

figs/weather_type_prop_year.tex	:	src/analyze/print_wt_prop_table.py data/processed/weather_type.nc
	$(PY_INTERP) $< --outfile $@ --wt data/processed/weather_type.nc

figs/seasonal_forecast.pdf	:	src/analyze/plot_seasonal_forecast.py data/processed/rain.nc data/raw/SeasonalForecast.tsv
	$(PY_INTERP) $< --outfile $@ --rain data/processed/rain.nc --seasonal data/raw/SeasonalForecast.tsv

figs/chiclet.pdf	:	src/analyze/plot_chiclet.py data/processed/rain.nc data/external/s2s_area_avg.nc
	$(PY_INTERP) $< --outfile $@ --rain data/processed/rain.nc --s2s data/external/s2s_area_avg.nc

figs/mos_forecasts.pdf	:	src/analyze/plot_mos_forecasts.py
	$(PY_INTERP) $< --outfile $@

## Make all analysis tables and figures
analyze:	figs/study_area.jpg figs/lagged_rain.pdf figs/anomalies_ndjf1516.pdf figs/eof_loadings.pdf figs/rain_wt_201516.pdf figs/wt_composite.pdf figs/klee.pdf figs/weather_type_prop_year.tex figs/seasonal_forecast.pdf figs/chiclet.pdf figs/mos_forecasts.pdf

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
