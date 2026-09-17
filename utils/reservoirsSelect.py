import pandas as pd
import streamlit as st

def reservoirsSelect(dataFrame:pd.DataFrame, columns:list[str]=[], months:int=0) -> pd.DataFrame:
        '''importing reservoirs data, then grabbing columns based on months and desired column output

        Parameters:
                 dataFrame: dataframe with reservoirs data
                 columns (list[str], optional): list of columns to grab, default to grab all columns
                 months (int, optional): number of months to grab, default to all months

        Returns:
                Dataframe with reservoirs data for selected months and columns
        '''

        #this can be removed depending on how st.select_slider() works
        if months < 0:
            raise ValueError("months must be zero or greater")

        # df = df.dropna()
        dataFrame["dato_Id"] = pd.to_datetime(dataFrame["dato_Id"]) # converting string to datetime <class 'pandas.Timestamp'>
        dataFrame = grab_logic(dataFrame, columns, months)
        return dataFrame

def grab_logic(dataFrame:pd.DataFrame, columns:list[str], months:int) -> pd.DataFrame:
        '''logic for grabbing reservoirs data'''

        # its ugly don't look
        # --||-- <- cool graphic don't look further

        # return entire dataframe
        if columns == [] and months == 0: return dataFrame
        # return all rows for chosen columns
        elif columns != [] and months == 0: return dataFrame[columns]
        # return chosen months for chosen/all columns
        else:
                years = months//12
                months = months%12
                if months%12 == 0:
                        months = 12
                        years = (months//12)-1

                #startDate for query
                startDate = dataFrame["dato_Id"].sort_values().iloc[0]
                firstYear = startDate.year
                firstMonth = startDate.month

                #endDate for query
                endYear = firstYear + years
                endMonth = months
                endDate = pd.Timestamp(year=endYear,month=endMonth,day=1)+pd.offsets.MonthBegin()

                #DataFrame for relevant timeframe
                dataFrame = dataFrame[(dataFrame["dato_Id"] >= startDate)& (dataFrame["dato_Id"] < endDate)]

                if not columns:
                        return dataFrame
                else: return dataFrame[columns]
