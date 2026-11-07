# Suggested Streamlit fixes

This folder contains drop-in replacements for the Streamlit files affected by the
Oblig 2 checklist. The notebook, Cassandra/Spark work, MongoDB loading and the
general hand-in items are intentionally **not** touched here.

Each file is a copy of the current version with only the Streamlit fixes applied.
`utils/areaSelect.py` is new.

## Files

| File in `Suggestions/` | Replaces | Status |
|---|---|---|
| `streamlit_app.py` | `streamlit_app.py` | changed |
| `utils/dataLoaders.py` | `utils/dataLoaders.py` | changed |
| `utils/reservoirsSelect.py` | `utils/reservoirsSelect.py` | changed |
| `utils/areaSelect.py` | — | **new** |
| `pages/plotData.py` | `pages/plotData.py` | changed |
| `pages/tabularData.py` | `pages/tabularData.py` | changed |
| `pages/transmissionsPlot.py` | `pages/transmissionsPlot.py` | changed |

## How to apply

From the repository root:

```bash
cp Suggestions/streamlit_app.py            streamlit_app.py
cp Suggestions/utils/dataLoaders.py        utils/dataLoaders.py
cp Suggestions/utils/reservoirsSelect.py   utils/reservoirsSelect.py
cp Suggestions/utils/areaSelect.py         utils/areaSelect.py
cp Suggestions/pages/plotData.py           pages/plotData.py
cp Suggestions/pages/tabularData.py        pages/tabularData.py
cp Suggestions/pages/transmissionsPlot.py  pages/transmissionsPlot.py
```

Then run:

```bash
uv run streamlit run streamlit_app.py
```

All copies were syntax-checked with `python -m py_compile`; `reservoirsSelect()`
and the October–September year logic were also smoke-tested against
`data/reservoirs.csv`.

---

## 1. `utils/dataLoaders.py`

**Problem:** the slider could not control the download interval, and the Mongo
loader returned the raw Mongo document shape (`_id` column, `time` as object).

**Changes:**

- Split the API call into a cached `_fetch_magazine_data()` and a
  `load_magazine_data_api(start=None, end=None)` that trims the frame.
  The NVE endpoint ignores `startDate`/`endDate` parameters (verified: it always
  returns 14 940 rows), so filtering is done after the cached download. This
  keeps the 4 MB download to once per session while still letting the slider
  decide which data reach the pages.
- `load_mongoDB_Data()` now drops `_id` and parses/sorts `time` to datetime, so
  the transmission page no longer depends on Mongo/pandas dtype luck.

```python
def load_magazine_data_api(start=None, end=None):
    magasinDF = _fetch_magazine_data().copy()
    if start is not None:
        magasinDF = magasinDF[magasinDF["date (y-m-d)"] >= pd.Timestamp(start)]
    if end is not None:
        magasinDF = magasinDF[magasinDF["date (y-m-d)"] <= pd.Timestamp(end)]
    return magasinDF.sort_values("date (y-m-d)").reset_index(drop=True)
```

## 2. `utils/reservoirsSelect.py`

**Problem:** the old `grab_logic()` treated the slider value as a *number of
months* and always started at the first row in the data (1995). Selecting
2020-01 → 2020-12 therefore showed 1995 data.

**Changes:**

- New signature: `reservoirsSelect(dataFrame, columns=None, start=None, end=None)`.
- Explicit inclusive date filtering, sorted ascending.
- `dropna()` is applied only after the requested columns are selected.
- The old `grab_logic()` helper is removed; both pages now pass real dates.

## 3. `utils/areaSelect.py` (new)

**Problem:** the area radio only existed on the Plots page, used
`NO / VASS / EL_1 … EL_5` as separate options, and the Tables page had no area
control at all, so `LineChartColumn` could not react to area type.

**Changes:**

- `areaSelector(dataFrame, key)` renders:
  - `st.radio("Area type", ["EL", "NO", "VASS"])`
  - `st.radio("Area number", ...)` for EL and VASS, with the numbers **derived
    from the data** (EL has 1–5, VASS currently 1–3, NO is `omrnr = 0`).
- `filterArea(dataFrame, areaType, areaNr)` returns the matching rows.
- Widget keys include the area type, so switching EL → VASS cannot leave an
  invalid area number selected.

Both pages call the same helper, which is what keeps the plots and the table in
sync.

## 4. `pages/plotData.py`

**Changes:**

- The `NO / VASS / EL_1 … EL_5` dict radio is replaced by
  `areaSelector()` + `filterArea()`.
- The interval `st.select_slider` is now read **before** the plot is drawn
  (previously the plot was rendered with the old interval and only updated on
  the next rerun).
- The selected `YYYY-MM` endpoints are converted to timestamps and passed
  through `plotData()` → `reservoirsSelect()`, so the slider really controls
  the interval shown.
- `processData()` now scales the full frame and returns one DataFrame instead of
  a dict of per-area frames; the area split happens afterwards.
- Page title is "Reservoir plots".

## 5. `pages/tabularData.py`

**Changes:**

- Adds the same `areaSelector()` + interval slider as the Plots page.
- The table is built from the filtered area/interval, not from the first month
  of 1995 with all regions mixed.
- `filled degree`, `filled degree last week` and `change in filled degree` are
  multiplied by 100 so the 0–100 `LineChartColumn` scale is meaningful.
- Added an empty-result guard and a caption showing the selected area/interval.
- Page title is "Reservoir tables".

## 6. `pages/transmissionsPlot.py`

**Changes:**

- Year ranges are derived from the Mongo data (October → September
  "hydrological" years) instead of the hard-coded `2024-2025 / 2025-2026` pills.
- Left column: `st.radio` for the connection and `st.selectbox` for the year
  (the "different control to select the year" in the task).
- Pie chart filters to the selected connection/year and converts 15-minute MW
  samples to MWh (`× 0.25`) before summing, so the slices are energy rather
  than a sum of instantaneous power readings.
- Right column: one `st.pills` group for the months of the selected year, and
  the line plot now uses **only the selected connection's two directions**
  instead of all twelve columns.
- `dropna(inplace=True)` on filtered slices is replaced with
  `dropna(subset=...)`, removing the `SettingWithCopyWarning`.
- Source expander documents ENTSO-E and the MW → MWh conversion.
- Page title is "Transmission plots" and layout is `wide`.

## 7. `streamlit_app.py`

- Removed the unused `from zmq.backend import select` (and the implicit
  `pyzmq` dependency it created).
- Renamed page titles to "Reservoir tables", "Reservoir plots" and
  "Transmission plots" to match the new page content.

---

## Behaviour after the changes

| Control | Before | After |
|---|---|---|
| Plots interval slider | selected a month count applied from 1995 | selects the actual start/end dates |
| Plots area radio | `NO / VASS / EL_1…EL_5` | `EL / NO / VASS` + area number |
| Tables area control | none | `EL / NO / VASS` + area number |
| `LineChartColumn` | first month of 1995, all regions, wrong scale | selected area/interval, percent scale |
| Transmission year | two hard-coded ranges | any October–September year in the data |
| Transmission line plot | all 12 connection/direction columns | selected connection's two directions |
| Pie totals | sum of MW samples | sum of MWh (`× 0.25 h`) |

## Test checklist

1. Plots page: select `2020-01` → `2020-12`. Only 2020 data is shown (the old
   code showed 1995).
2. Plots page: switch `EL` → `NO` → `VASS` and change the area number; the line
   and the "All Columns" plot change immediately.
3. Tables page: the same area/interval controls change the sparklines, and the
   `filled degree` lines now use the full 0–100 range.
4. Transmission page: changing the connection changes the pie and the line
   plot; changing the year changes both; selecting months updates the line
   plot; the line plot shows exactly two lines (in/out).
5. No `SettingWithCopyWarning` in the terminal when moving the transmission
   controls.

## Notes / limitations

- The NVE endpoint does not support server-side date filtering. The fix makes
  the slider control *which data are loaded into the pages* while keeping the
  expensive download cached. If the grader insists on an actual per-range HTTP
  request, `_fetch_magazine_data()` can be called with the range appended to
  the cache key, at the cost of re-downloading 4 MB per slider move.
- `utils/sessionstatehandler.py` still initialises `st.session_state.plotMonths`.
  It is no longer used, but leaving it is harmless; remove those lines if you
  want a fully clean state object.
- `.streamlit/config.toml` references `app/static/*.ttf` files that are not in
  the repository. That is a theme issue, not a task requirement. Either commit
  the four font files to a `static/` folder (Streamlit serves `./static` at
  `/app/static/...`) or remove the `[[theme.fontFaces]]` blocks. No config copy
  is included here because it changes the visual theme.
- `pages/home.py`, `pages/settings.py`, the role decorators and the notebook
  are unchanged.
