# Paraguay Floods

Code by James Doss-Gollin (2017).
Work by James Doss-Gollin, Angel Munoz, Simon Mason, and Max Pasten.
See paper (link to be made available).

## Goals

The key research questions that this analysis addresses are:

1. What sequences of rainfall led to intense flooding along the Paraguay and Paraná systems during NDJF 2015-16?
2. What sequences of daily circulation patterns led to the observed rainfall?
3. At sub-seasonal to seasonal timescales, what factors led to the observed rainfall and how did they enhance the probability of its occurrence?
4. What skill did models have in forecasting the rainfall?

Please see our paper for more infomration.

## Installing Dependencies

All codes are written in python.
In addition to several standard packages used, we provide a custom package just for this paper, available [on github](github.com/jdossgollin/paraguayfloodspy).
This helps us separate the computation from the analysis.

To get started use `git clone` or download the package as a `.zip` and unzip it.
Installing all required packages is easiest using `miniconda`:

```
conda env create --file environment.yml
source activate pyfloods
```

One of the packages (which will automatically be installed!) is the `paraguayfloodspy` package, available at [https://github.com/jdossgollin/paraguayfloodspy](https://github.com/jdossgollin/paraguayfloodspy).
This package contains some functions for plotting (in the `visualize` submodule), for working with `xarray` objects and calculating anomalies (in the `xrutil` submodule), for performing weather typing (`weather_type` submodule) and for defining some other paramaters (`pars` submodule).
Replication of our work or use of our codes requires the `paraguayfloodspy` package (though it is not particularly complicated -- no classes are defined.)

## Running

Once you have installed the dependencies, running is as simple as
```
bash run.sh
```

Please note that you will not be able to reproduce the figure showing streamflow (the raw figure is included in `04Writeup/`) because we are not authorized to disseminate the underlying data.
Please contact us directly if you are interested in obtaining this data and we will help you seek permission to use it.
