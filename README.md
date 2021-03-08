# Data Acquisition and Database Loading for US Representative Data
- **[App/Dashboard](https://rep-database.web.app/)**
- **Data Sources: [ProPublica Congress API](https://www.propublica.org/datastore/api/propublica-congress-api), [Google Knowledge Graph](https://developers.google.com/knowledge-graph/libraries), [Wikipedia](https://www.wikipedia.org/), [VoteSmart](https://justfacts.votesmart.org/), [Center for Responsive Politics (OpenSecrets API)](https://www.opensecrets.org/open-data/api), [US Census Bureau](https://www2.census.gov/geo/tiger/TIGER2020/CD/), [topojson/us-atlas](https://github.com/topojson/us-atlas).**
- Python Packages:
  - Data: [us](https://github.com/unitedstates/python-us), [bs4](https://www.crummy.com/software/BeautifulSoup/), [requests](https://requests.readthedocs.io/en/master/), [pymongo](https://pymongo.readthedocs.io/en/stable/index.html), [mediawiki](https://github.com/barrust/mediawiki)
  - Geographic Tools: [topojson](https://github.com/mattijn/topojson), [geopandas](https://geopandas.org/)
- JavaScript Packages:
  - Visualizations: [d3](https://d3js.org/)

## Where things are located
- [Database and Data Acquisition](https://github.com/wplam107/rep_db/tree/main/database-dev):
  - [Data Acquistion/Cleaning/Processing notebook](https://github.com/wplam107/rep_db/blob/main/database-dev/data_acquisition.ipynb)
- [App/Dashboard](https://github.com/wplam107/rep_db/tree/main/app-dev)
