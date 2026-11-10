# IND320LjosNorth Repo
- Version: 3.0
- Author: LjosNorth

:point_up: [This Git Repository](https://github.com/LjosNorth/IND320LjosNorth/tree/main)\
:spider_web: [Streamlit website](https://ind320ljosnorth.streamlit.app/)
### Folder structure:
```bash
.
├── .streamlit
│   └── config.toml
├── data
│   ├── regions
│   │   ├── electricity_areas.*
│   │   ├── precipitation_areas.*
│   │   ├── README.md
│   │   ├── samples
│   │   │   ├── samples_NO*.csv
│   │   │   ├── samples_VASS*.csv
│   │   │   └── weather
│   │   │       ├── NO
│   │   │       ├── NO1 ... NO5
│   │   │       └── VASS1 ... VASS3
│   │   └── state
│   └── reservoirs.csv
├── notebooks
│   ├── Oblig1.ipynb
│   ├── Oblig2.ipynb
│   └── Oblig3.ipynb
├── Oblig
│   ├── Oblig1
│   │   ├── Oblig1.html
│   │   └── Oblig1ScreenCast.mp4
│   ├── Oblig2
│   │   ├── 2026-10-20 ind320Oblig2.mp4
│   │   └── Oblig2.html
│   └── Oblig3
│       └── Oblig3.html
├── pages
│   ├── home.py
│   ├── plotData.py
│   ├── reservoirAnalysis.py
│   ├── settings.py
│   ├── tabularData.py
│   ├── transmissionsPlot.py
│   └── weatherAnalysis.py
├── utils
│   ├── Analysis.py
│   ├── areaSelect.py
│   ├── dataLoaders.py
│   ├── decorators.py
│   ├── fixit.py
│   ├── meteo.py
│   ├── reservoirsSelect.py
│   ├── sessionstatehandler.py
│   └── UserRoles.py
├── CHANGELOG.md
├── pyproject.toml
├── README.md
├── streamlit_app.py
└── uv.lock
```

### Run Locally:
```bash
git clone https://github.com/LjosNorth/IND320LjosNorth.git
cd IND320LjosNorth
uv sync
uv run streamlit run streamlit_app.py
```
^note parts will not function as secrets will not be provided

Starting Oblig 3 - (not yet) Read [Changelog](CHANGELOG.md)
