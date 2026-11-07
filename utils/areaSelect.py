'''
Shared area selection for the reservoir pages.

The 12.10 update asks for st.radio over the area types (EL, NO, VASS) so
that both the plots and LineChartColumn() show the matching area numbers.
Keeping this in one helper makes the Plots and Tables pages behave the same.
'''

import pandas as pd
import streamlit as st

AREA_TYPES = ["EL", "NO", "VASS"]


def areaSelector(dataFrame: pd.DataFrame, key: str) -> tuple[str, int]:
    '''Render the area type radio and (if relevant) the area number radio.

    Parameters:
        dataFrame: full reservoirs dataframe, used to find the available numbers
        key: prefix for the widget keys, so pages do not share widget state

    Returns:
        (area type, area number) - NO always uses number 0.
    '''
    areaType = st.radio(
        "Area type",
        AREA_TYPES,
        horizontal=True,
        key=f"{key}_areaType",
        help="EL = Elspot areas, NO = Norway total, VASS = catchment areas",
    )

    if areaType == "NO":
        return areaType, 0

    numbers = sorted(
        int(n) for n in dataFrame.loc[dataFrame["omrType"] == areaType, "omrnr"].unique()
    )
    if not numbers:
        st.warning(f"No {areaType} areas found in the data.")
        return areaType, -1

    areaNr = st.radio(
        "Area number",
        numbers,
        horizontal=True,
        # include the type in the key so switching type does not reuse a
        # number that may not exist for the new type
        key=f"{key}_{areaType}_areaNr",
    )
    return areaType, areaNr


def filterArea(dataFrame: pd.DataFrame, areaType: str, areaNr: int) -> pd.DataFrame:
    '''Return only the rows for the chosen area type and number.'''
    return dataFrame[
        (dataFrame["omrType"] == areaType) & (dataFrame["omrnr"] == areaNr)
    ].copy()
