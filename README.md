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

## Dependencies

You need access to `conda` and `make`.
It is possible to install python requirements but not recommended.

## Running

We created a `Makefile` to simplify setup and running.
First, download this repository as a `.zip` and unzip it or use `git clone`.
Next, and __only the first time you are working with this program__ run `make setup`.
This will use `conda` to install all required python packages in a `conda` environment called `pyfloods`.
_If you leave and come back later, just run `source activate pyfloods` to activate these packages_.
Finally, to make all results, run `make output` -- this will download data, run all analysis, and convert all `jupyter` notebooks to `.html` for your browsing convenience.
It will also put plots in `_figs`.

Note that when you run `make output`, you're likely to see a bunch of errors that look like this:
```
[NbConvertApp] Executing notebook with kernel: python3
/usr/local/miniconda3/envs/pyfloods/lib/python3.6/site-packages/jupyter_client/connect.py:157: RuntimeWarning: Failed to set sticky bit on '/var/folders/fq/2rlq61px6h9dtl4qmtd7hmm00000gn/T': [Errno 1] Operation not permitted: '/var/folders/fq/2rlq61px6h9dtl4qmtd7hmm00000gn/T'
  RuntimeWarning,
```
You shouldn't worry as this is a harmless warning.

At this point you may want to see the figures!
Run `make viewfigs` to open them all (if you're not on OSX or if you don't like Preview, go to `Makefile`, and edit the line that says `PDF_VIEWER = Preview` to set your favorite PDF viewer.)

If you want to reproduce our paper, you need to run `make tex` which will convert the `latex` document into a `.pdf`.
Please note that you will not be able to reproduce the figure showing streamflow (the raw figure is included in `04-Writeup/`) because we are not authorized to disseminate the underlying data.
Please contact us directly if you are interested in obtaining this data and we will help you seek permission to use it.

## Issues

If you have trouble running our code, please use the `Issues` tab to let us know.
We'll do our best to help you -- we're not software developers and don't promise to make these codes work seamlessly on every computing platform but we are scientists who are interested in ensuring (i) that our results are correct and (ii) supporting future research in the community.
