# Changelog

All notable changes are noted here\
if im a good boy that does what I say I'm going to & remember the changes lol

## [3.0] - 10-11-2026

### Added
- **notebook/Oblig3.ipynb**: weather data, DCT/SPC outliers, LOF anomalies, STL and spectrogram
- **utils/meteo.py**: ERA5 download, grid aggregation and MongoDB upload
- **utils/Analysis.py**: Plotly analysis functions for the weather and reservoir pages
- **reservoir analysis page**: STL and spectrogram tabs
- **weather analysis page**: SPC and LOF tabs
- weather data for all regions in MongoDB

### Changed
- updated Oblig 3 data loading and page structure
- added icons to the analysis pages
- added geopandas for the area shapefiles

### Removed
- placeholder weather page content

## [2.0] - 20-10-2026

### Added
- **notebook/Oblig2.ipynb**: finished
- **uv.lock & pyproject.toml**: now instead of requirements.txt
- **transmission plots page**: with right and left column showing a piechart and line plot
- function to load and cache magasinstatistikk data


### Changed
- dockstrings to start of all py files
- updated plotting to datetime as x axis and split regions to a seperate select
- now pulling data from magasinstatistikk API for tables and plotting, reservoirs.cvs is now no longer in use
- changed the themeing of the streamlit site

### Removed
- **Requirements.txt**: uv.lock has tanken its place
- totally "*removed*" a silly little message from the tables page ;)
