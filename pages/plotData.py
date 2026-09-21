import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from plotly.subplots import make_subplots
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
        elif column == "All columns":
            reservoirs = reservoirsSelect(self.fullReservoirs, [], months)
            self.figureAllColumns(reservoirs)
        else:
            reservoirs = reservoirsSelect(self.fullReservoirs, [column], months)
            fig = go.Figure(
                data=[go.Histogram(x=reservoirs[column])]
            )
            fig.update_xaxes(title_text=column)
            fig.update_yaxes(title_text="count")
            fig.show()
            st.plotly_chart(fig)

    def figureAllColumns(self, reservoirs:pd.DataFrame):
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