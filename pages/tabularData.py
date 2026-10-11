'''
tabular data page, shows a table for the first month of data from water magazines throughout Norway
'''

import streamlit as st
import pandas as pd

from utils.UserRoles import UserRoles
from utils.reservoirsSelect import reservoirsSelect
from utils.dataLoaders import load_magazine_data_api
from utils.decorators import require_role

class TabularData:
    '''class to render the tabular data page'''
    def __init__(self):
        self.columns=["filled degree", "capacity_Twh", "fill_Twh", "filled degree last week", "change in filled degree"]
        self.months = 1
        self.reservoirsDF = reservoirsSelect(load_magazine_data_api(), self.columns, self.months)

    def tabularData(self):
        '''function to rotate the DF'''
        return pd.DataFrame({
            "column": self.columns,
            "first month": [self.reservoirsDF[columns].tolist() for columns in self.reservoirsDF.columns]
        })

    def showTable(self):
        '''function to show the table'''
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

    @require_role(UserRoles.SECRET)
    def userInfo(self):
        '''silly use of roles for funnsies'''
        st.write("Only the goodest boy or girl can see this message :)")

    # Render Page
    def renderPage(self):
        '''function to render the page'''

        #actual stuff
        self.showTable()

        #UserShit
        self.userInfo()

    def run(self):
        '''function to run the page'''
        self.renderPage()

if __name__ == "__main__":
    try:
        TabularData().run()
    except Exception as e:
        st.error(e)