import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np

from plotly.subplots import make_subplots
from scipy.stats import gaussian_kde

from utils.reservoirsSelect import reservoirsSelect
from utils.dataLoaders import load_Reservoirs

class PlotData:
    def __init__(self):

        # Data
        self.fullReservoirs = load_Reservoirs()
        self.fullReservoirs["dato_Id"] = pd.to_datetime(self.fullReservoirs["dato_Id"]).sort_values()

        # Columns
        self.fullColumns=["dato_Id", "fyllingsgrad", "kapasitet_TWh", "fylling_TWh", "fyllingsgrad_forrige_uke", "endring_fyllingsgrad"]
        self.fullColumns.append("All Columns")

        # Months
        self.minMonth = self.fullReservoirs["dato_Id"].min().month
        self.maxMonth = (self.fullReservoirs["dato_Id"].max().year - self.fullReservoirs["dato_Id"].min().year) * 12 + self.fullReservoirs["dato_Id"].max().month

    def plotData(self, column:str, months:int=1):
        if column == "":
            pass
        elif column == "All Columns":
            reservoirs = reservoirsSelect(self.fullReservoirs, [], months)
            reservoirsLog = np.log2(reservoirs) # Scaling
            reservoirsLog = pd.DataFrame(reservoirsLog)
            self.figureAllColumns(reservoirsLog)
        else:
            reservoirs = reservoirsSelect(self.fullReservoirs, [column], months)
            fig = go.Figure(
                data=[go.Histogram(x=reservoirs[column])]
            )
            fig.update_xaxes(title_text=column)
            fig.update_yaxes(title_text="count")
            fig.show()
            st.plotly_chart(fig)

    def subplotsAllColumns(self, reservoirs:pd.DataFrame):
        fig = make_subplots(rows=3, cols=2)
        fig.add_trace(
            go.Histogram(x=reservoirs["fyllingsgrad"], name="fyllingsgrad"),
            row=1, col=1
        )
        fig.add_trace(
            go.Histogram(x=reservoirs["fylling_TWh"], name="fylling_TWh"),
            row=1, col=2
        )
        fig.add_trace(
            go.Histogram(x=reservoirs["fyllingsgrad_forrige_uke"], name="fyllingsgrad_forrige_uke"),
            row=2, col=1
        )
        fig.add_trace(
            go.Histogram(x=reservoirs["endring_fyllingsgrad"], name="endring_fyllingsgrad"),
            row=2, col=2
        )
        fig.add_trace(
            go.Histogram(x=reservoirs["kapasitet_TWh"], name="kapasitet_TWh"),
            row=3, col=1
        )

        fig.update_layout(title_text="Reservoirs", showlegend=True)
        fig.update_layout(height=700)  # Increase as needed

        # figure1
        fig.update_xaxes(title="fyllingsgrad", row=1, col=1)
        fig.update_yaxes(title="count", row=1, col=1)

        # figure2
        fig.update_xaxes(title="fylling_TWh", row=1, col=2)
        fig.update_yaxes(title="count", row=1, col=2)

        # figure3
        fig.update_xaxes(title="fyllingsgrad_forrige_uke", row=2, col=1)
        fig.update_yaxes(title="count", row=2, col=1)

        # figure4
        fig.update_xaxes(title="endring_fyllingsgrad", row=2, col=2)
        fig.update_yaxes(title="count", row=2, col=2)

        # figure5
        fig.update_xaxes(title="kapasitet_TWh", row=3, col=1)
        fig.update_yaxes(title="count", row=3, col=1)

        st.plotly_chart(fig, use_container_width=True)

    def singlePlotAllColumns(self, reservoirs:pd.DataFrame):
        fig.show()
        # %%
        fig = go.Figure()

        # fig1
        dataFig1 = reservoirs["fyllingsgrad"]
        kde = gaussian_kde(dataFig1)
        x_range = np.linspace(dataFig1.min(), dataFig1.max(), 200)
        density = kde(x_range)
        fig.add_trace(
            go.Scatter(x=x_range, y=density, fill="tozeroy", name="fig1")
        )

        # fig2
        dataFig2 = reservoirs["fylling_TWh"]
        kde = gaussian_kde(dataFig2)
        x_range = np.linspace(dataFig2.min(), dataFig2.max(), 200)
        density = kde(x_range)
        fig.add_trace(
            go.Scatter(x=x_range, y=density, fill="tozeroy", name="fig2")
        )

        # fig3
        dataFig3 = reservoirs["fyllingsgrad_forrige_uke"]
        kde = gaussian_kde(dataFig3)
        x_range = np.linspace(dataFig3.min(), dataFig3.max(), 200)
        density = kde(x_range)
        fig.add_trace(
            go.Scatter(x=x_range, y=density, fill="tozeroy", name="fig3")
        )

        # fig4
        dataFig4 = reservoirs["endring_fyllingsgrad"]
        kde = gaussian_kde(dataFig4)
        x_range = np.linspace(dataFig4.min(), dataFig4.max(), 200)
        density = kde(x_range)
        fig.add_trace(
            go.Scatter(x=x_range, y=density, fill="tozeroy", name="fig4")
        )

        # fig5
        dataFig5 = reservoirs["kapasitet_TWh"]
        kde = gaussian_kde(dataFig5)
        x_range = np.linspace(dataFig5.min(), dataFig5.max(), 200)
        density = kde(x_range)
        fig.add_trace(
            go.Scatter(x=x_range, y=density, fill="tozeroy", name="fig5")
        )

    def renderPage(self):
        # FillerShit
        st.title("Nullam ac ornare tellus.")
        st.write("Duis eget sollicitudin justo. Pellentesque aliquam congue turpis sed aliquet. Etiam vitae nulla non sem elementum vulputate. ")

        # ActualStuff
        optionsColumns = st.selectbox("Select what columns to display", self.fullColumns)
        months = st.slider("Choose nr. of months to look at", self.minMonth, self.maxMonth)
        self.plotData(optionsColumns,months=months)

    def run(self):
        self.renderPage()


if __name__ == "__main__":
    try:
        PlotData().run()
    except Exception as e:
        st.error(e)