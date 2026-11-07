'''
tabular data page, shows a table for the selected area and interval
from water magazines throughout Norway
'''

import pandas as pd
import streamlit as st

from utils.UserRoles import UserRoles
from utils.areaSelect import areaSelector, filterArea
from utils.dataLoaders import load_magazine_data_api
from utils.decorators import require_role
from utils.reservoirsSelect import reservoirsSelect

# Columns that are stored as 0-1 but are easier to read as percent
PERCENT_COLUMNS = [
    "filled degree",
    "filled degree last week",
    "change in filled degree",
]


class TabularData:
    '''class to render the tabular data page'''

    def __init__(self):
        self.columns = [
            "filled degree",
            "capacity_Twh",
            "fill_Twh",
            "filled degree last week",
            "change in filled degree",
        ]

        self.fullReservoirs = load_magazine_data_api()
        self.fullReservoirs["date (y-m-d)"] = pd.to_datetime(
            self.fullReservoirs["date (y-m-d)"]
        )

        min_date = self.fullReservoirs["date (y-m-d)"].min()
        max_date = self.fullReservoirs["date (y-m-d)"].max()
        self.month_options = [
            period.strftime("%Y-%m")
            for period in pd.period_range(start=min_date, end=max_date, freq="M")
        ]

    def tabularData(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        '''function to rotate the DF'''
        return pd.DataFrame({
            "column": list(dataframe.columns),
            "values": [dataframe[column].tolist() for column in dataframe.columns],
        })

    def showTable(self):
        '''Area + interval controls, then the LineChartColumn table.'''
        areaType, areaNr = areaSelector(self.fullReservoirs, "tables")

        selected_range = st.select_slider(
            "Choose range of time",
            options=self.month_options,
            value=(self.month_options[0], self.month_options[-1]),
        )
        start = pd.Period(selected_range[0], freq="M").start_time
        end = pd.Period(selected_range[1], freq="M").end_time

        areaDF = filterArea(self.fullReservoirs, areaType, areaNr)
        reservoirsDF = reservoirsSelect(areaDF, self.columns, start=start, end=end)

        if reservoirsDF.empty:
            st.info("No data for this area and interval.")
            return

        # 0-1 -> 0-100 so the sparklines use the same scale as part 1
        for column in PERCENT_COLUMNS:
            if column in reservoirsDF.columns:
                reservoirsDF[column] = reservoirsDF[column] * 100

        tabularData = self.tabularData(reservoirsDF)
        st.dataframe(
            tabularData,
            column_config={
                "column": st.column_config.TextColumn("Reservoirs"),
                "values": st.column_config.LineChartColumn(
                    "values",
                    width="medium",
                    y_min=0,
                    y_max=100,
                    help="Data for each column in the selected interval",
                ),
            },
        )

        areaLabel = "Norway total" if areaType == "NO" else f"{areaType} area {areaNr}"
        st.caption(f"{areaLabel} · {selected_range[0]} → {selected_range[1]}")

    @require_role(UserRoles.SECRET)
    def userInfo(self):
        '''silly use of roles for funnsies'''
        st.write("Only the goodest boy or girl can see this message :)")

    # Render Page
    def renderPage(self):
        '''function to render the page'''

        st.set_page_config(
            page_title="Reservoir tables",
            page_icon="🗒️",
            layout="centered",
        )

        # actual stuff
        self.showTable()

        # UserShit
        self.userInfo()

    def run(self):
        '''function to run the page'''
        self.renderPage()


if __name__ == "__main__":
    try:
        TabularData().run()
    except Exception as e:
        st.error(e)
