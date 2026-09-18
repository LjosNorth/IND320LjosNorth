from pathlib import Path
import streamlit as st
import pandas as pd
from PyQt6.QtCore.QUrl import userInfo
from PyQt6.lupdate import user

from utils.UserRoles import UserRoles
from utils.reservoirsSelect import reservoirsSelect
from utils.dataLoaders import load_Reservoirs
from utils.decorators import require_role

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

    def showTable(self):
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

    @require_role(UserRoles.USER)
    def userInfo(self):
        st.write("Only the goodest boy or girl can see this message :)")

    # Render Page
    def renderPage(self):
        #dummy text
        st.title("Mauris lorem")
        st.write("elis, consectetur id mollis sit amet, vulputate non libero. Interdum et malesuada fames ac ante ipsum primis in faucibus. Mauris eros purus, sagittis in finibus eu, ultricies sit amet nisi. Cras at sagittis eros.")

        #actual stuff
        self.showTable()

        #UserShit
        userInfo()

    def run(self):
        self.renderPage()

if __name__ == "__main__":
    try:
        TabularData().run()
    except Exception as e:
        st.error(e)