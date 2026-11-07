'''page for displaying the entsoE data'''

import pandas as pd
import streamlit as st
import plotly.express as px

from utils.dataLoaders import load_mongoDB_Data

# [column towards Norway, column away from Norway]
CONNECTIONS = {
    "DE/LU ↔ NO_2": ["de_lu_to_no_2", "no_2_to_de_lu"],
    "DK ↔ NO_2": ["dk_1_to_no_2", "no_2_to_dk_1"],
    "FI ↔ NO_4": ["fi_to_no_4", "no_4_to_fi"],
    "GB ↔ NO_2": ["gb_to_no_2", "no_2_to_gb"],
    "NL ↔ NO_2": ["nl_to_no_2", "no_2_to_nl"],
    "SE ↔ NO_1": ["se_3_to_no_1", "no_1_to_se_3"],
}

# Hydrological years run October -> September
MONTHS = [
    "October",
    "November",
    "December",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
]


class TransmissionPlot:
    def __init__(self):
        self.transmissions = load_mongoDB_Data()

        # Filled in by renderCol1 and reused by renderCol2
        self.connection = None
        self.connectionColumns = None
        self.yearStart = None

        self.availableYears = self.yearStarts(self.transmissions)

    @staticmethod
    def yearStarts(dataFrame: pd.DataFrame) -> list[int]:
        '''Return the start year of every October -> September year in the data.'''
        if dataFrame.empty or "time" not in dataFrame.columns:
            return []

        startYears = dataFrame["time"].dt.year.where(
            dataFrame["time"].dt.month >= 10,
            dataFrame["time"].dt.year - 1,
        )
        return sorted(int(year) for year in startYears.unique())

    @staticmethod
    def yearLabel(startYear: int) -> str:
        '''e.g. 2024 -> "2024-2025"'''
        return f"{startYear}-{startYear + 1}"

    def yearData(self, startYear: int) -> pd.DataFrame:
        '''Rows belonging to one October -> September year.'''
        dataFrame = self.transmissions.copy()
        dataFrame["yearStart"] = dataFrame["time"].dt.year.where(
            dataFrame["time"].dt.month >= 10,
            dataFrame["time"].dt.year - 1,
        )
        return dataFrame[dataFrame["yearStart"] == startYear]

    def pieChart(self, label: str, totalIn: float, totalOut: float, rangeLabel: str):
        '''In/out totals for one connection and one year.'''
        data = pd.DataFrame({
            "category": ["In", "Out"],
            "values": [totalIn, totalOut],
        })
        fig = px.pie(
            data,
            values="values",
            names="category",
            title=f"{label} · {rangeLabel}",
        )
        st.plotly_chart(fig, use_container_width=True)

    def lineChart(self, dataFrame: pd.DataFrame, columns: list[str]):
        '''Daily averages keep the plot readable (same as the notebook).'''
        dataFrame = (
            dataFrame.set_index("time")
            .resample("D")
            .mean(numeric_only=True)
            .reset_index()
        )
        fig = px.line(dataFrame, x="time", y=columns)
        st.plotly_chart(fig, use_container_width=True)

    def renderCol1(self):
        '''Connection + year controls and the in/out pie chart.'''
        self.connection = st.radio(
            "pick a connection", list(CONNECTIONS), horizontal=True
        )
        self.connectionColumns = CONNECTIONS[self.connection]

        labels = [self.yearLabel(year) for year in self.availableYears]
        if not labels:
            st.info("No transmission data found in MongoDB.")
            return

        # "a different control to select the year"
        label = st.selectbox("pick a year", labels)
        self.yearStart = self.availableYears[labels.index(label)]

        yearDF = self.yearData(self.yearStart).dropna(subset=self.connectionColumns)
        if yearDF.empty:
            st.info("No data for this connection/year.")
            return

        # 15-minute MW samples -> MWh
        totalIn = yearDF[self.connectionColumns[0]].sum() * 0.25
        totalOut = yearDF[self.connectionColumns[1]].sum() * 0.25

        self.pieChart(self.connection, totalIn, totalOut, label)

    def renderCol2(self):
        '''Month pills and the line plot for the selected connection/year.'''
        if self.yearStart is None:
            return

        st.write("Choose months to display in the diagram")
        monthsChoosen = st.pills(
            "Choose which months to display",
            MONTHS,
            selection_mode="multi",
            key="transmissionMonths",
            label_visibility="collapsed",
        )
        if not monthsChoosen:
            st.info("Pick at least one month.")
            return

        yearDF = self.yearData(self.yearStart)
        yearDF["month"] = yearDF["time"].dt.strftime("%B")

        # Only the selected connection, not all twelve columns
        plotDF = (
            yearDF[yearDF["month"].isin(monthsChoosen)][
                ["time", *self.connectionColumns]
            ]
            .dropna()
        )

        if plotDF.empty:
            st.info("No data for the chosen months.")
            return

        self.lineChart(plotDF, self.connectionColumns)

    def renderPage(self):
        '''render the page'''
        st.set_page_config(
            page_title="Transmission plots",
            page_icon="📈",
            layout="wide",
        )

        col1, col2 = st.columns(2)

        with col1:
            self.renderCol1()

        with col2:
            self.renderCol2()

        with st.expander("Sources"):
            st.markdown(
                "This data is sourced from the "
                "[ENTSO-E Transparency Platform](https://transparency.entsoe.eu/) API. "
                "In/out totals are calculated from 15-minute cross-border flow samples "
                "(MW × 0.25 h = MWh)."
            )

    def run(self):
        '''run the page'''
        self.renderPage()


if __name__ == "__main__":
    try:
        TransmissionPlot().run()
    except Exception as e:
        st.error(e)
