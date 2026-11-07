'''
plot page, show plots for data about water magazines throughout Norway
'''

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.areaSelect import areaSelector, filterArea
from utils.dataLoaders import load_magazine_data_api
from utils.reservoirsSelect import reservoirsSelect

# columns that are scaled to 0-1 so they can share one axis
COLUMNS_TO_SCALE = [
    "filled degree",
    "capacity_Twh",
    "fill_Twh",
    "filled degree last week",
    "change in filled degree",
]


class PlotData:
    '''class for the plotdata page'''

    def __init__(self):
        # Full dataset is downloaded once and cached in dataLoaders
        self.fullReservoirs = load_magazine_data_api()
        self.fullReservoirs["date (y-m-d)"] = pd.to_datetime(
            self.fullReservoirs["date (y-m-d)"]
        )

        # Columns
        self.fullColumns = [
            "filled degree",
            "capacity_Twh",
            "fill_Twh",
            "filled degree last week",
            "change in filled degree",
            "All Columns",
        ]

        # Date range for the date/month slider options
        min_date = self.fullReservoirs["date (y-m-d)"].min()
        max_date = self.fullReservoirs["date (y-m-d)"].max()
        self.month_options = [
            period.strftime("%Y-%m")
            for period in pd.period_range(start=min_date, end=max_date, freq="M")
        ]

        # Scaled copy used for plotting (same behaviour as part 1)
        self.scaledReservoirs = self.processData(self.fullReservoirs)

        # Filled in by renderCol1
        self.regionToPlot = None

    def processData(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        '''Scale the numeric columns to 0-1 so they can share an axis.'''
        dataframe = dataframe.copy()
        dataframe["date (y-m-d)"] = pd.to_datetime(dataframe["date (y-m-d)"])
        dataframe = dataframe.sort_values("date (y-m-d)", ascending=False)

        for column in COLUMNS_TO_SCALE:
            min_val = dataframe[column].min()
            max_val = dataframe[column].max()
            if max_val != min_val:
                dataframe[column] = (dataframe[column] - min_val) / (max_val - min_val)

        return dataframe

    def plotData(self, region: pd.DataFrame, column: str, start, end):
        '''plotting based on selectbox | columns'''
        if column == "":
            return

        if column == "All Columns":
            self.plotAllColumns(region, start, end)
            return

        reservoirs = reservoirsSelect(
            region, ["date (y-m-d)", column], start=start, end=end
        )
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

    def plotAllColumns(self, dataframe: pd.DataFrame, start, end):
        '''plotting all the columns'''
        columns = [
            "filled degree",
            "fill_Twh",
            "filled degree last week",
            "change in filled degree",
            "capacity_Twh",
        ]
        reservoirs = reservoirsSelect(
            dataframe, ["date (y-m-d)", *columns], start=start, end=end
        )

        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

        fig = go.Figure()
        for column, color in zip(columns, colors):
            tempFig = px.line(
                reservoirs,
                x="date (y-m-d)",
                y=column,
                color_discrete_sequence=[color],
            )
            for trace in tempFig.data:
                fig.add_trace(trace)

        st.plotly_chart(fig, use_container_width=True)

    def renderCol1(self):
        '''Area type/number radio, shared with the table page.'''
        empty1, empty2, content = st.columns([1, 1, 1])

        with content:
            areaType, areaNr = areaSelector(self.fullReservoirs, "plots")
            self.regionToPlot = filterArea(self.scaledReservoirs, areaType, areaNr)

            if areaType == "NO":
                st.caption("Showing Norway total")
            else:
                st.caption(f"Showing {areaType} area {areaNr}")

    def renderCol2(self):
        '''Interval slider + column selectbox + plot.'''
        st.space()

        # The slider is read BEFORE plotting so the new interval is used
        # immediately instead of on the next rerun.
        selected_range = st.select_slider(
            "Choose range of time",
            options=self.month_options,
            value=(self.month_options[0], self.month_options[-1]),
        )
        start = pd.Period(selected_range[0], freq="M").start_time
        end = pd.Period(selected_range[1], freq="M").end_time

        optionsColumns = st.selectbox("Select what columns to display", self.fullColumns)
        self.plotData(self.regionToPlot, optionsColumns, start, end)

    def renderCol3(self):
        pass

    def renderPage(self):
        '''reder the structure of the page'''
        st.set_page_config(
            page_title="Reservoir plots",
            page_icon="📊",
            layout="wide",
        )

        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            self.renderCol1()

        with col2:
            self.renderCol2()

        with col3:
            self.renderCol3()

    def run(self):
        '''run the page'''
        self.renderPage()


if __name__ == "__main__":
    try:
        PlotData().run()
    except Exception as e:
        st.error(e)
