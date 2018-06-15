# Raw Data Included

## `station_description.csv`:

This `.csv` file contains information on four streamflow gauges whose data was shared with us from the Paraguayan Directorate of Meteorology and Hydrology.
The fields are:

- `stn_id`: an internal station identifier
- `long_name`: the full name of the station
- `short_name`: a shortened name of the station
- `lon`: station's longitude
- `lat`: station's latitude
- `elev_m`: station's elevation, in meters above sea level
- `alert`: the river stage [in meters] at which an alert for flooding is declared
- `critical`: the stage at which a critical alert for flooding is declared
- `disaster`: the stage at which a flooding disaster is declared

## `SeasonalForecast.tsv`:

This `tsv` file contains the seasonal forecast produced by the IRI data library.
It has two header rows and three columns.
The three columns are, in order,

- the grid box's longitude
- the grid box's latitude
- the probability of heavy (>90th percentile) rainfall
