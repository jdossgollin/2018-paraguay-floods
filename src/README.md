# Source Code

The code is all written in python.
The `pyfloods` directory provides a module in which most of the computation and definitions are carried out.
The rest of the analysis is implemented in individual scripts, which are named to give an idea of what they do.
Scripts are numbered in a "smart" format as follows:

- `0X-xx.py`: access the project's data
- `1X-xx.py`: make plots that don't require substantial analysis
- `2X-xx.py`: make plots associated with NDJF 2015-16 circulation and circulation anomalies
- `3X-xx.py`: make plots associated with weather types
- `4X-xx.py`: make plots associated with forecasts and forecast skill

To run a single script:

```
python 01-raw-data.py # for example
```

To run all scripts:
```
bash run.sh > log.txt
```
