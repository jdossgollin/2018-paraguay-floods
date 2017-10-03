'''
Get 1km elevation data
'''

import xarray as xr
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--outfile', nargs=1, help='The output file to save')

def main():
    # parse the arguments
    args = parser.parse_args()
    outfile = args.outfile[0]

    url = 'http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NGDC/.GLOBE/.topo/'
    url += 'X/-180/0.1/180/GRID/Y/-90/0.1/90/GRID/'
    url += 'dods'
    elev = xr.open_dataarray(url)

    # Save to file
    elev.to_netcdf(outfile, format='NETCDF4')

if __name__ == '__main__':
    main()
