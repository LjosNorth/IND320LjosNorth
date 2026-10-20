'''page for displaying the entsoE data'''
from copy import copy
from xmlrpc import client

import pandas as pd
import streamlit as st
import plotly.express as px
from utils.dataLoaders import load_mongoDB_Data


class TransmissionPlot:
    def __init__(self):
        self.transmissions = load_mongoDB_Data()

    def pieChart(self, label: str, columnNames: list, connectionDF: pd.DataFrame):
        # Reshape data for pie chart
        data = pd.DataFrame({
            'category': ['In', 'Out'],
            'values': [connectionDF[columnNames[0]].sum(), connectionDF[columnNames[1]].sum()]
        })
        fig = px.pie(data, values="values", names="category", title=label)
        st.plotly_chart(fig)

    def lineChart(self, df):
        df = df.set_index("time").resample("D").mean(numeric_only=True).reset_index()

        y=[
            "de_lu_to_no_2", "no_2_to_de_lu",
            "dk_1_to_no_2", "no_2_to_dk_1",
            "fi_to_no_4", "no_4_to_fi",
            "gb_to_no_2", "no_2_to_gb",
            "nl_to_no_2", "no_2_to_nl",
            "se_3_to_no_1", "no_1_to_se_3"
        ]
        fig = px.line(df, x="time", y=y)
        # fig = px.line(df, x="time", y=["de_lu_to_no_2", "no_2_to_de_lu"])
        st.plotly_chart(fig)

    def renderCol1(self):
        connectionsList = {
            "DE/LU ↔ NO_2": ["de_lu_to_no_2", "no_2_to_de_lu"],
            "DK ↔ NO_2": ["dk_1_to_no_2", "no_2_to_dk_1"],
            "FI ↔ NO_4": ["fi_to_no_4", "no_4_to_fi"],
            "GB ↔ NO_2": ["gb_to_no_2", "no_2_to_gb"],
            "NL ↔ NO_2": ["nl_to_no_2", "no_2_to_nl"],
            "SE ↔ NO_1": ["se_3_to_no_1","no_1_to_se_3"],
        }
        optionConnection = st.radio("pick a connection", connectionsList, horizontal=True)
        optionConnectionvalue = connectionsList[optionConnection]
        # st.caption(optionConnection)
        # st.space()

        years = ["2024-2025", "2025-2026"]
        selectedTime = st.pills("pick a time span", years)

        minDate = self.transmissions["time"].min()
        cutoffDate = minDate + pd.DateOffset(years=1)
        if selectedTime == "2024-2025":
            selectedYearDF = self.transmissions[self.transmissions["time"]<cutoffDate]
        else:
            selectedYearDF = self.transmissions[self.transmissions["time"]>=cutoffDate]

        # selectedYearDF.sort_values(by="time", inplace=True)
        selectedYearDF.dropna(inplace=True)

        connection = selectedYearDF[[optionConnectionvalue[0], optionConnectionvalue[1]]]

        if selectedTime:
            try:
                self.pieChart(optionConnection, optionConnectionvalue, connection)
            except Exception as e:
                st.write(e)

    def renderCol2(self):
        st.write ("Choose months to display in the diagram")
        st.write("2024-2025")
        monthsListFirst = ['October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September'] # Hardcoded, could make a better solution probs, but lazy
        monthsChoosenFirst = st.pills("choice which months to display", monthsListFirst, selection_mode="multi", key="FirstYearPill", label_visibility="collapsed")

        st.write("2025-2026")
        monthsListLast = ['October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September']
        monthsChoosenLast = st.pills("", monthsListLast, selection_mode="multi", key="SecondYearPill", label_visibility="collapsed")

        col2DF = copy(self.transmissions)
        col2DF.dropna(inplace=True)
        col2DF.sort_values(by="time", inplace=True)
        col2DF["month"] = col2DF['time'].dt.strftime('%B')
        col2DF['year'] = col2DF['time'].dt.year

        # Determine which year range each row belongs to
        # (Oct-Dec is previous year, Jan-Sep is current year)
        def get_year_range(row):
            month = row['month']
            year = row['year']
            if month in ['October', 'November', 'December']:
                return year  # e.g., 2024 for Oct 2024 = 2024-2025 range
            else:
                return year - 1  # e.g., 2024 for Jan 2025 = 2024-2025 range

        col2DF['year_range'] = col2DF.apply(get_year_range, axis=1)

        # Filter based on selections
        filtered_df = col2DF[
            ((col2DF['year_range'] == 2024) & (col2DF['month'].isin(monthsChoosenFirst))) |
            ((col2DF['year_range'] == 2025) & (col2DF['month'].isin(monthsChoosenLast)))
            ]

        # st.dataframe(filtered_df)
        df = filtered_df.drop(columns=['month', 'year', 'year_range'])
        # st.dataframe(df)

        if monthsChoosenFirst or monthsChoosenLast:
            try:
                self.lineChart(df)
                st.caption("i think this looks chaotic, but the task does not ask me to include a connection choose option here")
            except Exception as e:
                st.write(e)

    def renderPage(self):
        '''render the page'''
        st.set_page_config(
            page_title="Transmission Plots",
            page_icon="📈",
            layout="centered",
        )

        col1, col2 = st.columns(2)

        with col1:
            self.renderCol1()

        with col2:
            self.renderCol2()

        #extra shits
        # st.dataframe(self.transmissions)
        with st.expander("Sources"):
            source = '''
            This data is sourced from the [ENTSO-E](https://transparency.entsoe.eu/) API
            '''
            st.markdown(source, unsafe_allow_html=True)
    def run(self):
        '''run the page'''
        self.renderPage()

if __name__ == "__main__":
    try:
        TransmissionPlot().run()
    except Exception as e:
        st.error(e)