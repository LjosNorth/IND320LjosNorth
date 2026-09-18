from pathlib import Path
import streamlit as st
import pandas as pd
from utils.reservoirsSelect import reservoirsSelect
from utils.dataLoaders import load_Reservoirs

class TabularData:
    '''class to render the tabular data page'''
    def __init__(self):
        self.columns=["fyllingsgrad", "kapasitet_TWh", "fylling_TWh", "fyllingsgrad_forrige_uke","endring_fyllingsgrad"]
        self.months = 1
        self.reservoirsDF = reservoirsSelect(load_Reservoirs(), self.columns, self.months)

    def tabularData(self):
        return pd.DataFrame({
            "column": self.columns,
            "first month": [self.reservoirsDF[columns].tolist() for columns in self.reservoirsDF.columns]
        })

    def showData(self):
        tabularData = self.tabularData()
        st.dataframe(
            tabularData,
            column_config={
                "name": st.column_config.TextColumn("Reservoirs"),
                "first month": st.column_config.LineChartColumn(
                    "first month",
                    width="medium",
                    y_min=0,
                    y_max=100,
                    help="Data for each column in the first month"
                )
            }
        )

    def renderPage(self):
        #dummy text
        st.title("Mauris lorem")
        st.write("elis, consectetur id mollis sit amet, vulputate non libero. Interdum et malesuada fames ac ante ipsum primis in faucibus. Mauris eros purus, sagittis in finibus eu, ultricies sit amet nisi. Cras at sagittis eros.")

        #actual stuff
        self.showData()

    def run(self):
        self.renderPage()

if __name__ == "__main__":
    try:
        TabularData().run()
    except Exception as e:
        st.error(e)