"""This Page is to Display Weather information"""

# import
import pandas as pd
import streamlit as st

from utils.Analysis import dct_spc_outliers, lof_anomalies
from utils.dataLoaders import load_mongoDB_weather_data


class WeatherAnalysis:
    def __init__(self) -> None:
        self.weather = pd.DataFrame()

    def rendertab1(self) -> None:

        option1, option2 = st.columns(2)
        sigma = option1.slider("Pick nr σ", 1, 5, value=3)
        cuttoff = option2.slider("pick cutoff_days", 7, 120, value=30)
        option2.caption("season balancer, normally 30")

        outlierAnalysis = dct_spc_outliers(
            self.weather["precipitation"], cutoff_days=cuttoff, n_sigma=sigma
        )
        st.plotly_chart(outlierAnalysis.fig)
        metric1, metric2, metric3 = st.columns(3)

        metric1.metric("Outliers:", outlierAnalysis.stats["count"])
        metric2.metric("Share", f"{outlierAnalysis.stats['percent']:.2f} %")
        strongest = outlierAnalysis.stats["strongest_value"]
        metric3.metric(
            "Strongest",
            "—" if strongest is None else f"{strongest:.1f} mm",
        )
        st.caption(
            f"Cutoff {outlierAnalysis.stats['cutoff_days']} days · "
            f"robust σ {outlierAnalysis.stats['robust_sigma']:.2f} mm · "
            f"{outlierAnalysis.stats['n_sigma']}σ band"
        )

        with st.expander("Full DataFrame"):
            st.dataframe(outlierAnalysis.summary)

    def rendertab2(self) -> None:

        option1, option2 = st.columns(2)
        contamination = option1.slider(
            "pick contamination", 0.001, 0.5, value=0.01, step=0.001
        )
        option1.caption("how many anomalies")
        neighbors = option2.slider("pick n neighbors", 5, 50, value=20)

        anomalyAnalysis = lof_anomalies(
            self.weather["temperature_2m"],
            contamination=contamination,
            n_neighbors=neighbors,
        )
        st.plotly_chart(anomalyAnalysis.fig)

        metric1, metric2, metric3, metric4 = st.columns(4)
        metric1.metric("Anomalies", anomalyAnalysis.stats["count"])
        metric2.metric("Share", f"{anomalyAnalysis.stats['percent']:.1f} %")
        highest = anomalyAnalysis.stats["highest_value"]
        lowest = anomalyAnalysis.stats["lowest_value"]

        metric3.metric(
            "Highest",
            "—" if highest is None else f"{highest:.1f} °C",
        )
        metric4.metric(
            "Lowest",
            "—" if lowest is None else f"{lowest:.1f} °C",
        )
        expected = anomalyAnalysis.stats["contamination"] * len(self.weather)
        st.caption(
            f"contamination {anomalyAnalysis.stats['contamination']:.1%} · "
            f"n_neighbors {anomalyAnalysis.stats['n_neighbors']} · "
            f"{len(self.weather)} days · expected ≈ {expected:.1f} anomalies"
        )

        with st.expander("Full DataFrame"):
            st.dataframe(anomalyAnalysis.summary)

    def renderPage(self) -> None:
        """render page"""

        regionType = st.pills(
            "",
            ["NO", "EL", "VASS"],
            label_visibility="collapsed",
            selection_mode="single",
        )
        if regionType == "EL":
            region = st.pills(
                "",
                ["NO1", "NO2", "NO3", "NO4", "NO5"],
                label_visibility="collapsed",
                selection_mode="single",
            )
        elif regionType == "VASS":
            region = st.pills(
                "",
                ["VASS1", "VASS2", "VASS3"],
                label_visibility="collapsed",
                selection_mode="single",
            )
        elif regionType == "NO":
            region = "NO"
        else:
            region = None

        if region is None:
            st.stop()

        self.weather = (
            load_mongoDB_weather_data(region=region).set_index("time").sort_index()
        )

        if self.weather.empty:
            st.info(f"No weather data for {region}.")
            st.stop()

        tab1, tab2 = st.tabs(["Outlier Analysis", "Anomaly Analysis"])
        with tab1:
            self.rendertab1()

        with tab2:
            self.rendertab2()

    def run(self) -> None:
        """renders the page"""
        st.set_page_config(
            page_title="Weather Analysis",
            page_icon="🌦️",
            layout="centered",
        )

        self.renderPage()


# ---
if __name__ == "__main__":
    try:
        WeatherAnalysis().run()
    except Exception as e:
        st.error(e)
