'''
logic for extracting y columns and x months from the reservoirs data
'''

import pandas as pd


def reservoirsSelect(dataFrame: pd.DataFrame, columns: list[str] | None = None,
                     start=None, end=None) -> pd.DataFrame:
    '''Grab the requested columns for the requested date interval.

    Replaces the old "N months from the first row" logic, which always
    started at 1995 no matter which range the slider showed.

    Parameters:
        dataFrame: dataframe with reservoirs data
        columns (list[str], optional): columns to keep, defaults to all
        start (optional): first date to keep (inclusive)
        end (optional): last date to keep (inclusive)

    Returns:
        Dataframe with reservoirs data for the selected interval and columns
    '''
    columns = columns or []

    dataFrame = dataFrame.copy()
    dataFrame["date (y-m-d)"] = pd.to_datetime(dataFrame["date (y-m-d)"])

    if start is not None:
        dataFrame = dataFrame[dataFrame["date (y-m-d)"] >= pd.Timestamp(start)]
    if end is not None:
        dataFrame = dataFrame[dataFrame["date (y-m-d)"] <= pd.Timestamp(end)]

    dataFrame = dataFrame.sort_values("date (y-m-d)").reset_index(drop=True)

    if columns:
        dataFrame = dataFrame[columns]

    return dataFrame.dropna()
