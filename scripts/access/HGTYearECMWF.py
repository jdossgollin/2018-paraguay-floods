'''
Download the streamfunction for a specified year and level and save to file
Data from ERA-Interim
Download a single year
'''

from ecmwfapi import ECMWFDataServer
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--level', type=int, nargs=1, help = 'Pressure level (hPa) for data')
parser.add_argument('--year', nargs=1, type=int, help='The year of data to download')
parser.add_argument('--outfile', nargs=1, help='The output file to save!')

def main():
    # parse the arguments
    args = parser.parse_args()
    year = args.year[0]
    level = args.level[0]
    outfile = args.outfile[0]

    server = ECMWFDataServer()
    server.retrieve({
        "class": "ei",
        "dataset": "interim",
        "date": "{}-01-01/to/{}-12-31".format(year,year), #  Download the whole year
        "expver": "1",
        "grid": "1/1", # ONE DEGREE
        "levelist": "{}".format(level), # One level
        "levtype": "pl", # Pressure level
        "param": "129.128", # for GPH
        "step": "0",
        "stream": "oper",
        "time": "00:00:00/06:00:00/12:00:00/18:00:00",
        "type": "an",
        "format": "netcdf",
        "target": "{}".format(outfile),
    })

if __name__ == '__main__':
    main()
