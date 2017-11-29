import os

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))

data_external = os.path.join(project_dir, 'data', 'external')
data_raw = os.path.join(project_dir, 'data', 'raw')
data_processed = os.path.join(project_dir, 'data', 'processed')
figures = os.path.join(project_dir, 'figures')

for dir in [data_external, data_raw, data_processed, figures]:
    if not os.path.isdir(dir):
        os.makedirs(dir)

streamfunction = os.path.abspath(os.path.join(data_processed, 'streamfunction.nc'))
rainfall = os.path.abspath(os.path.join(data_processed, 'precip.nc'))
monthly_indices = os.path.abspath(os.path.join(data_external, 'monthly_indices.csv'))
daily_indices = os.path.abspath(os.path.join(data_external, 'daily_indices.csv'))
elevation_data = os.path.abspath(os.path.join(data_external, 'elevation_data.nc'))
s2s_area_avg = os.path.abspath(os.path.join(data_external, 's2s_area_avg.nc'))
