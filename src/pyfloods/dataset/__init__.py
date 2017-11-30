"""
This submodule defines the abstraction of a dataset and can work generically
for any dataset whether it has one or more files, regardless of the
type of file that it describes.
In general, the dataset has the following elements:
* a set of parameters that determine what the dataset contains
* a filename or set of filenames that describe where the data is stored
* a way to access the data from some remote source and save it to file
* a way to read the data, including its parameters, in from files
* a way to check whether the data that was read from file has the desired parameters
"""

from typing import Tuple,Dict,Any
import os

class SingleFileDataSet():
    def __init__(self, fname: str, verbose: bool = False,
                params: Dict[str, Any] = {}) -> None:
        self.params = params
        self.fname = fname
        self.verbose = verbose

    def download_data(self):
        raise NotImplementedError

    def read_data(self) -> Tuple[Any, Dict]:
        raise NotImplementedError

    def get_data(self):
        """Try to read in the data, and if it has changed or if it cannot be
        read in, then download the data.
        """
        need_download: bool = False
        try:
            data,data_params = self.read_data()
            if self.params != data_params:
                os.remove(self.fname)
                need_download = 1
                if self.verbose:
                    print('Data was read from file but had different parameters')
            if self.verbose:
                print('Successfully read data from file')
        except:
            if self.verbose:
                print('Unable to read data from file')
            need_download = True
        if need_download:
            if self.verbose:
                print('Downloading data from source')
            data = self.download_data()
        return(data)

# Make it so we don't have to remember the file names when we do imports later
from .cpc_rain import CPC
from .elevation import NOAANGDC
from .mjo_bom import MJOBOMD
from .nino_34 import KaplanNINO34
from .reanalysisv2 import ReanalysisV2
from .s2s_area_avg import S2SAreaAvg
