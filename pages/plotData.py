import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np

from scipy.stats import gaussian_kde
from utils.fixit import signlog
from utils.reservoirsSelect import reservoirsSelect
from utils.dataLoaders import load_Reservoirs

class PlotData:
    '''class for the plotdata page'''
    def __init__(self):

        # Data
        self.fullReservoirs = load_Reservoirs()
        self.fullReservoirs["dato_Id"] = pd.to_datetime(self.fullReservoirs["dato_Id"]).sort_values()

        # Columns
        self.fullColumns=["fyllingsgrad", "kapasitet_TWh", "fylling_TWh", "fyllingsgrad_forrige_uke", "endring_fyllingsgrad"]
        self.fullColumns.append("All Columns")

        # Months
        self.minMonth = self.fullReservoirs["dato_Id"].min().month
        self.maxMonth = (self.fullReservoirs["dato_Id"].max().year - self.fullReservoirs["dato_Id"].min().year) * 12 + self.fullReservoirs["dato_Id"].max().month


    def plotData(self, column:str, months:int=1):
        '''plotting based on selectbox | columns'''
        if column == "":
            pass
        elif column == "All Columns":
            reservoirs = reservoirsSelect(self.fullReservoirs, ["fyllingsgrad", "kapasitet_TWh", "fylling_TWh", "fyllingsgrad_forrige_uke", "endring_fyllingsgrad"], months)
            reservoirs = reservoirs.apply(signlog)
            self.singlePlotAllColumns(reservoirs)
        else:
            reservoirs = reservoirsSelect(self.fullReservoirs, [column], months)
            fig = go.Figure(
                data=[go.Histogram(x=reservoirs[column])]
            )
            fig.update_xaxes(title_text=column)
            fig.update_yaxes(title_text="count")
            st.plotly_chart(fig)

    def singlePlotAllColumns(self, reservoirs:pd.DataFrame):
        '''plotting all the columns'''
        fig = go.Figure()

        # fig1
        dataFig1 = reservoirs["fyllingsgrad"]
        kde = gaussian_kde(dataFig1)
        x_range = np.linspace(dataFig1.min(), dataFig1.max(), 200)
        density = kde(x_range)
        density = density / density.max()
        fig.add_trace(
            go.Scatter(x=x_range, y=density, fill="tozeroy", name="fyllingsgrad")
        )

        # fig2
        dataFig2 = reservoirs["fylling_TWh"]
        kde = gaussian_kde(dataFig2)
        x_range = np.linspace(dataFig2.min(), dataFig2.max(), 200)
        density = kde(x_range)
        density = density / density.max()
        fig.add_trace(
            go.Scatter(x=x_range, y=density, fill="tozeroy", name="fylling_TWh")
        )

        # fig3
        dataFig3 = reservoirs["fyllingsgrad_forrige_uke"]
        kde = gaussian_kde(dataFig3)
        x_range = np.linspace(dataFig3.min(), dataFig3.max(), 200)
        density = kde(x_range)
        density = density / density.max()
        fig.add_trace(
            go.Scatter(x=x_range, y=density, fill="tozeroy", name="fyllingsgrad_forrige_uke")
        )

        # fig4
        dataFig4 = reservoirs["endring_fyllingsgrad"]
        kde = gaussian_kde(dataFig4)
        x_range = np.linspace(dataFig4.min(), dataFig4.max(), 50)
        density = kde(x_range)
        density = density / density.max()
        fig.add_trace(
            go.Scatter(x=x_range, y=density, fill="tozeroy", name="endring_fyllingsgrad")
        )

        # fig5
        dataFig5 = reservoirs["kapasitet_TWh"]
        kde = gaussian_kde(dataFig5)
        x_range = np.linspace(dataFig5.min(), dataFig5.max(), 200)
        density = kde(x_range)
        density = density / density.max()
        fig.add_trace(
            go.Scatter(x=x_range, y=density, fill="tozeroy", name="kapasitet_TWh")
        )

        st.plotly_chart(fig, use_container_width=True)

    def renderPage(self):
        '''render the page'''
        # FillerShit
        st.title("Nullam ac ornare tellus.")
        st.write("Duis eget sollicitudin justo. Pellentesque aliquam congue turpis sed aliquet. Etiam vitae nulla non sem elementum vulputate. ")

        # ActualStuff
        optionsColumns = st.selectbox("Select what columns to display", self.fullColumns)
        self.plotData(optionsColumns,months=st.session_state.plotMonths)
        st.session_state.plotMonths = st.slider("Choose nr. of months to look at", self.minMonth, self.maxMonth)

    def run(self):
        '''run the page'''
        self.renderPage()


if __name__ == "__main__":
    try:
        PlotData().run()
    except Exception as e:
        st.error(e)