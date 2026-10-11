'''
plot page, show plots for data about water magazines throughout Norway
'''

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.reservoirsSelect import reservoirsSelect
from utils.dataLoaders import load_magazine_data_api

class PlotData:
    '''class for the plotdata page'''
    def __init__(self):

        # Data
        self.fullReservoirs = load_magazine_data_api()
        self.fullReservoirs["date (y-m-d)"] = pd.to_datetime(self.fullReservoirs["date (y-m-d)"]).sort_values()

        # Columns
        self.fullColumns=["filled degree", "capacity_Twh", "fill_Twh", "filled degree last week", "change in filled degree", "All Columns"]

        # Months
        self.minMonth = self.fullReservoirs["date (y-m-d)"].min().month
        self.maxMonth = (self.fullReservoirs["date (y-m-d)"].max().year - self.fullReservoirs["date (y-m-d)"].min().year) * 12 + self.fullReservoirs["date (y-m-d)"].max().month

    def processData(self, dataframe:pd.DataFrame) -> dict:
        # changing columns and subdividing columns

        # scaling columns
        colsToScale = ["filled degree", "capacity_Twh", "fill_Twh", "filled degree last week",
                       "change in filled degree"]

        # datetime shiz
        dataframe["date (y-m-d)"] = pd.to_datetime(dataframe["date (y-m-d)"])  # date str -> datetime
        dataframe = dataframe.sort_values("date (y-m-d)", ascending=False)  # sort by date

        # Scale columns to 0-1 range (min-max scaling)
        for col in colsToScale:
            min_val = dataframe[col].min()
            max_val = dataframe[col].max()
            dataframe[col] = (dataframe[col] - min_val) / (max_val - min_val)

        # NO region
        NO = dataframe[dataframe["omrType"] == "NO"]

        # VASS
        VASS = dataframe[dataframe["omrType"] == "VASS"]

        # EL regions
        EL_1 = dataframe[(dataframe['omrType'] == "EL") & (dataframe["omrnr"] == 1)]
        EL_2 = dataframe[(dataframe['omrType'] == "EL") & (dataframe["omrnr"] == 2)]
        EL_3 = dataframe[(dataframe['omrType'] == "EL") & (dataframe["omrnr"] == 3)]
        EL_4 = dataframe[(dataframe['omrType'] == "EL") & (dataframe["omrnr"] == 4)]
        EL_5 = dataframe[(dataframe['omrType'] == "EL") & (dataframe["omrnr"] == 5)]

        return {"NO":NO, "VASS":VASS, "EL_1":EL_1, "EL_2":EL_2, "EL_3":EL_3, "EL_4":EL_4, "EL_5":EL_5}

    def plotData(self, region:pd.DataFrame, column:str, months:int=1):
        '''plotting based on selectbox | columns'''
        if column == "":
            pass
        elif column == "All Columns":
            self.plotAllColumns(region, months)
        else:
            reservoirs = reservoirsSelect(region, ["date (y-m-d)", column], months)
            fig = px.line(
                reservoirs,
                x="date (y-m-d)",
                y=column,
                title="Reservoir Filled Degree Over Time",
                labels={
                    "date (y-m-d)": "Date",
                    "filled degree": "Filled Degree (%)",
                },
            )
            st.plotly_chart(fig, use_container_width=True)

    def plotAllColumns(self, dataframe, months:int):
        '''plotting all the columns'''

        reservoirs = reservoirsSelect(dataframe, ["date (y-m-d)", "filled degree", "capacity_Twh", "fill_Twh", "filled degree last week", "change in filled degree"], months)

        # Columns to process
        columns = [
            "filled degree",
            "fill_Twh",
            "filled degree last week",
            "change in filled degree",
            "capacity_Twh",
        ]

        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

        # Create an empty figure or start with the first column
        fig = go.Figure()
        for column, color in zip(columns, colors):
            tempFig = px.line(
                reservoirs,
                x="date (y-m-d)",
                y=column,
                color_discrete_sequence=[color]
            )
            for trace in tempFig.data:
                fig.add_trace(trace)

        st.plotly_chart(fig, use_container_width=True)

    def renderPage(self):
        '''render the page'''

        #getting region
        regionsDict = self.processData(self.fullReservoirs)
        regionNames = list(regionsDict.keys())
        optionsRegions = st.selectbox("Select what Region to display", regionNames)
        region = regionsDict[optionsRegions]

        if optionsRegions == "VASS":
            st.caption("I should split VASS into 5 regions probably")

        #getting colums
        st.space()
        optionsColumns = st.selectbox("Select what columns to display", self.fullColumns)

        # plotting
        self.plotData(region= region, column=optionsColumns, months=st.session_state.plotMonths)

        # getting months
        st.session_state.plotMonths = st.slider("Choose range of time", self.minMonth, self.maxMonth)

        # Consider later if i want to make the following work or no

        # # 1. Generate the year-month options
        # month_range = pd.period_range(start=self.minMonth, end=self.maxMonth, freq="M")
        # month_options = [p.strftime("%Y-%m") for p in month_range]
        #
        # # 2. Render the select slider for range selection
        # selected_range = st.select_slider(
        #     "Choose range of time",
        #     options=month_options,
        #     value=(month_options[0], month_options[-1])
        # )
        #
        # # 3. Calculate the integer number of months (inclusive)
        # start_period = pd.Period(selected_range[0], freq="M")
        # end_period = pd.Period(selected_range[1], freq="M")
        #
        # # Store the total count as an integer in session state
        # st.session_state.plotMonths = (end_period - start_period).n + 1

    def run(self):
        '''run the page'''
        self.renderPage()


if __name__ == "__main__":
    try:
        PlotData().run()
    except Exception as e:
        st.error(e)