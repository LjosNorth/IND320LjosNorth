import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils.reservoirsSelect import reservoirsSelect
from utils.dataLoaders import load_Reservoirs

class PlotData:
    pd.options.plotting.backend = "plotly" #setting, cuz matplotlib be boring
    def __init__(self):
        self.fullReservoirs = load_Reservoirs()
        self.fullColumns=["fyllingsgrad", "kapasitet_TWh", "fylling_TWh", "fyllingsgrad_forrige_uke","endring_fyllingsgrad"] #for now reducing what can be displayed
        self.fullReservoirs["dato_Id"] = pd.to_datetime(self.fullReservoirs["dato_Id"]).sort_values()
        self.minMonth = self.fullReservoirs["dato_Id"].min().month
        self.maxMonth = (self.fullReservoirs["dato_Id"].max().year - self.fullReservoirs["dato_Id"].min().year) * 12 + self.fullReservoirs["dato_Id"].max().month
        self.months = self.minMonth

    def plotData(self, column:str, months:int=1):
        if column == "":
            pass
        elif column == "All columns":
            reservoirs = reservoirsSelect(self.fullReservoirs, [], months)
        else:
            reservoirs = reservoirsSelect(self.fullReservoirs, [column], months)
            fig = go.Figure(
                data=[go.Histogram(x=reservoirs[column])]
            )
            fig.update_xaxes(title_text=column)
            fig.update_yaxes(title_text="count")
            fig.show()
            st.plotly_chart(fig)

    def renderPage(self):
        # FillerShit
        st.title("Nullam ac ornare tellus.")
        st.write("Duis eget sollicitudin justo. Pellentesque aliquam congue turpis sed aliquet. Etiam vitae nulla non sem elementum vulputate. ")

        # ActualStuff
        optionsColumns = st.selectbox("Select what columns to display", self.fullColumns)
        self.plotData(optionsColumns,months=self.months)
        self.months = st.slider("Choose nr. of months to look at", self.minMonth, self.maxMonth)

    def run(self):
        self.renderPage()


if __name__ == "__main__":
    try:
        PlotData().run()
    except Exception as e:
        st.error(e)