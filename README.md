# Paraguay Floods

Code by James Doss-Gollin.
Work by James Doss-Gollin, Angel Munoz, Simon Mason, and Max Pasten.
See paper (link to be made available).

## Goals

To be added Later

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

One of the packages which will automatically be installed is the `paraguayfloodspy` package, available at [https://github.com/jdossgollin/paraguayfloodspy](https://github.com/jdossgollin/paraguayfloodspy).
This package contains some functions for plotting (in the `visualize` submodule), for working with `xarray` objects and calculating anomalies (in the `xrutil` submodule), for performing weather typing (`weather_type` submodule) and for defining some other paramaters (`pars` submodule).
Replication of our work or use of our codes requires the `paraguayfloodspy` package (though it is not particularly complicated -- no classes are defined.)

## Running

Add more later
