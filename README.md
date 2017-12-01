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

## To Run

We assume you have `conda` installed -- otherwise you can likely use `pip` to install your dependencies but this can be complicated.
If there's an issue replicating our `conda` environment please let us know!
We note that successful installation of `cartopy` has been messy on our and many computers.

```
source activate -f environment.yml
cd src
bash run.sh > log.txt
```

The `log.txt` argument will then contain any warnings, or errors from running the code,
as well as any outputs from the scripts such as the classifiability index.
