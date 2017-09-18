conda env create --file environment.yml
source activate pyfloods
conda install -c conda-forge cartopy eofs netcdf4 windspharm
pip install git+git://github.com/jdossgollin/paraguayfloodspy@master
