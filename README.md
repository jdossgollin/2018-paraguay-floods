# Heavy rainfall in Paraguay during the 2015-2016 austral summer: causes and subseasonal-to-seasonal predictive skill

Welcome to the code repository for "Heavy rainfall in Paraguay during the 2015-2016 austral summer: causes and subseasonal-to-seasonal predictive skill", by James Doss-Gollin, Angel Munoz, Simon Mason, and Max Pasten.
All code was written by James Doss-Gollin (2016-2018).
This paper has been published in the Journal of Climate and may be accessed (via open access!) at https://journals.ametsoc.org/doi/abs/10.1175/JCLI-D-17-0805.1.
If you are unable to access this paper and would like to, please [contact me](http://jamesdossgollin.me/#contact).

This repository will enable you to repeat our analysis and reproduce it for your own benefit.
A permanent archive of the codes used to generate the submission to Journal of Climate is also available at: [![DOI](https://zenodo.org/badge/103452588.svg)](https://zenodo.org/badge/latestdoi/103452588)

## Goals

The key research questions that this analysis addresses are:

1. What sequences of rainfall led to intense flooding along the Paraguay and Paraná systems during NDJF 2015-16?
2. What sequences of daily circulation patterns led to the observed rainfall?
3. At sub-seasonal to seasonal timescales, what factors led to the observed rainfall and how did they enhance the probability of its occurrence?
4. What skill did models have in forecasting the rainfall?

Please see our paper to read about our scientific ideas!
The below documentation will focus on how the _computation_ is structured, which is only a small piece of the thinking we did.
If you can't access our paper, please contact us!

## Code Organization

Code is written in python, using well-documented and open-source packages:

- `numpy` and `scipy` for numerical computation
- `pandas` for tabular data
- `xarray` for organizing gridded data with metadata
- `numba` to speed a few computations
- `matplotlib`, `seaborn`, and `colorcet` for plotting
- `cartopy` for mapping
- `scikit-learn` for EOF analysis (PCA) and clustering
- `windspharm` to calculate the streamfunction from wind data

To track dependencies between parameters (stored in `/config`), data (stored in `/data`), and results (stored in `/figs`), a `Makefile` is used.
Some great posts such as these one by [Mike Bostock](https://bost.ocks.org/mike/make/), [Rob Hyndman](https://robjhyndman.com/hyndsight/makefiles/) or this [Software Carpentry Course](http://swcarpentry.github.io/make-novice/) go into more detail about why `make` is such a great tool for data anaylsis.

Using `make` helps us organize our code into several distinct steps:

- The first time you run the code, you need to install the package dependencies. We do this with `conda`, which we assume you have installed; if you want to install the packages manually with `pip` you may be able to do so, but it's more involved. To do this run `make environment`. Then run `source activate pyfloods` to activate the environment.
- Configure parameters of the analysis. These files are stored in `config/` and control what years are studied and the regions of the analysis
- Download raw data from source (climate indices, gridded rainfall data, gridded wind data, model forecasts, etc). To do this run `make get`. As a general rule for gridded data, we download year by year and subset by pressure level (for reanalysis) but not by space. This means that what we download reall is "raw" data
- Process the raw data into useful "chunks" that are easy to analyze. Calculate streamfunction from the wind vectors. Aggregate the stream function and rainfall over regions relevant for plotting and calculate anomalies. Sub-set the stream function over the weather typing region and the rainfall over the Lower Paraguay River Basin. Run the weather typing algorithm. All of this is done using `make process`.
- Create plots and tables with `make analyze`.

In fact, `make` knows that the analysis steps depend on the processed data and so on, so once you have your environment installed you can run `conda activate pyfloods` and then `make analyze` and everything will run.

## Using these Codes

Please use this code under the terms of the MIT License (see `LICENSE` file).
If you use it, please cite our paper.

If you find any errors with this code, please use the `Issues` tab.
However, the aim of this repository is _not_ to provide an active software library and we do not intend to modify it from this final version except to correct errors.
