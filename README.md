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

Please see our paper to read about our scientific ideas!
The below documentation will focus on how the _computation_ is structured, which is only a small piece of the thinking we did.
If you can't access our paper, please contact us!

## Code Layout

We use a `Makefile` (see [this resource](http://www.jonzelner.net/statistics/make/reproducibility/2016/06/01/makefiles/) to separate the key phases of our data analysis:

1. Define parameters. This is done in the `config/` directory, and different files specify parameters for different parts of the analysis.
2. **Access** data -- raw data is downloaded and put in `data/accessed`. Once there, it is read in but never modified. Consequently, we get a lot of data -- the entire globe is covered for the rainfall and reanalysis data -- and any subsetting is done later.
3. **Process** data -- starting from the raw data and the parameters defined above, we then create subsets of the data for working with (i.e. over a region of interest) and derive some variables from these (like the weather types)
4. **Analyze** data -- once all the processed data has been created, we're ready for analysis and visualization. This step is performed with jupyter notebooks.
5. **Write** our results -- using a `latex` file in `writeup/`

What `make` allows is for us to make changes to our configuration parameters (or to scripts themselves) and re-rurun _only the parts of the analysis that depend on the changed files_.

We're also liberal about downloading data -- it is better to download more data than is strictly necessary, and then sub-set it, than to repeatedly re-download data (as we learned from experience).
We download $u$ and $v$ wind globally for every year at our target levels, convert to streamfunction, and save each year and level to file.
Thus when we change the domains we want to plot, nothing has to change.

## Dependencies

You need access to `conda` for python and `make`.
It is possible to install python requirements but not recommended.
By default dependencies are installed when you run code (next section)

## Running

1. Download this repository using `git clone` or just download as a `.zip`
2. __Only the first time you are working with this program__ run `make setup`. This will create folders to store you data and will use `conda` to install all required python packages in a `conda` environment called `pyfloods`.
3. To make all results, run `make output` -- this will download data, run all analysis, and convert all `jupyter` notebooks to `.html` for your browsing convenience.
It will also put plots in `_figs`.
4. To create the writeup, run `make tex` -- this is not done by default when you run `make output`

Please note that when you run `make output`, you're likely to see a bunch of warnings that look like this:
```
[NbConvertApp] Executing notebook with kernel: python3
/usr/local/miniconda3/envs/pyfloods/lib/python3.6/site-packages/jupyter_client/connect.py:157: RuntimeWarning: Failed to set sticky bit on '/var/folders/fq/2rlq61px6h9dtl4qmtd7hmm00000gn/T': [Errno 1] Operation not permitted: '/var/folders/fq/2rlq61px6h9dtl4qmtd7hmm00000gn/T'
  RuntimeWarning,
```
You shouldn't worry as this is a harmless warning.

## Issues

If you have trouble running our code, please use the `Issues` tab to let us know.
We'll do our best to help you -- we're not software developers and don't promise to make these codes work seamlessly on every computing platform but we are scientists who are interested in ensuring (i) that our results are correct and (ii) supporting future research in the community.
