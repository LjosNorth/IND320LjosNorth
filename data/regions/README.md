# Area shapefiles — source and field reference

Downloaded **2026-11-08** from NVE's public map services. All files are in
**EPSG:4326 (WGS 84)** and contain **5 polygons** each.

## Files

| File | Layer | Key fields | Features |
|---|---|---|---|
| `electricity_areas.shp` (+ `.geojson`) | Nettområder → **Budområde** | `budomr` = `NO 1` … `NO 5` | 5 |
| `precipitation_areas.shp` (+ `.geojson`) | **NVE regioner** (`NVE_Region`) | `REGION` = `RS`, `RØ`, `RV`, `RM`, `RN`; `REG_NAME` | 5 |

The `.geojson` versions are included because `geopandas.read_file()` reads them
without shapefile encoding issues. The `.shp` versions are the shapefiles the
assignment asks for.

> Shapefile field names are limited to 10 characters, so the shapefile stores
> `REGIONNAVN` as `REG_NAME`. The GeoJSON keeps the original `REGIONNAVN`.
> `budomr` contains a space (`"NO 1"`); strip it to get `NO1`.

## Where these layers are in NVE Atlas

- **Electricity areas:** NVE Atlas → **Nett** → **Nettområder** → **Budområde**
- **Precipitation areas:** NVE Atlas → **Administrasjon** → **NVE regioner**

The same layers are exposed by NVE's ArcGIS REST services, which is what was
used here (the download button in the atlas is easy to miss).

## Direct source URLs

### Electricity areas (`NO1`–`NO5`)

```
https://kart.nve.no/enterprise/rest/services/Nettomraader/FeatureServer/0/query
    ?where=1=1
    &outFields=budomr
    &returnGeometry=true
    &outSR=4326
    &f=geojson
```

### Precipitation areas (`RS`, `RØ`, `RV`, `RM`, `RN`)

```
https://kart.nve.no/enterprise/rest/services/Mapservices/Administrasjon2/MapServer/0/query
    ?where=1=1
    &outFields=REGION,REGIONNAVN
    &returnGeometry=true
    &outSR=4326
    &f=geojson
```

## How the files were created

```bash
cd Code/IND320/IND320LjosNorth
mkdir -p data/regions

# 1) Electricity areas -> GeoJSON
curl -sSL --get \
  "https://kart.nve.no/enterprise/rest/services/Nettomraader/FeatureServer/0/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "outFields=budomr" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "f=geojson" \
  -o data/regions/electricity_areas.geojson

# 2) Precipitation areas -> GeoJSON
curl -sSL --get \
  "https://kart.nve.no/enterprise/rest/services/Mapservices/Administrasjon2/MapServer/0/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "outFields=REGION,REGIONNAVN" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "f=geojson" \
  -o data/regions/precipitation_areas.geojson

# 3) GeoJSON -> Shapefile
ogr2ogr -f "ESRI Shapefile" data/regions/electricity_areas.shp \
  data/regions/electricity_areas.geojson -lco ENCODING=UTF-8

ogr2ogr -f "ESRI Shapefile" data/regions/precipitation_areas.shp \
  data/regions/precipitation_areas.geojson -lco ENCODING=UTF-8
```

## Mapping to the Magasinstatistikk data

| `omrType` | `omrnr` | Meaning | Polygon source |
|---|---|---|---|
| `EL` | 1–5 | Electricity price areas `NO1`–`NO5` | `electricity_areas` |
| `NO` | 0 | Whole country | union of all |
| `VASS` | 1 | South-East Norway | `RS` + `RØ` |
| `VASS` | 2 | Western Norway | `RV` |
| `VASS` | 3 | Central & Northern Norway | `RM` + `RN` |

This mapping is the one the assignment hints at:
*"East is split into RS+RØ, and North is split into RM+RN."*

## Quick verification

```python
import geopandas as gpd

el = gpd.read_file("data/regions/electricity_areas.shp")
precip = gpd.read_file("data/regions/precipitation_areas.shp")

print(el[["budomr"]])                 # NO 1 ... NO 5
print(precip[["REGION", "REG_NAME"]]) # RS/RØ/RV/RM/RN
print(el.crs, precip.crs)             # EPSG:4326
```
