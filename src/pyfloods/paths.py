import os

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))

data_external = os.path.join(project_dir, 'data', 'external')
data_raw = os.path.join(project_dir, 'data', 'raw')
data_processed = os.path.join(project_dir, 'data', 'processed')
figures = os.path.join(project_dir, 'figures')

for dir in [data_external, data_raw, data_processed, figures]:
    if not os.path.isdir(dir):
        os.makedirs(dir)

file_station_description = os.path.join(data_raw, 'station_description.csv')
