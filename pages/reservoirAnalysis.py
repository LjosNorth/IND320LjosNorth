"""This Page is to display reservoir filling analysis"""

# import
import streamlit as st

from utils.Analysis import spectrogram_plot, stl_decomposition
from utils.areaSelect import areaSelector
from utils.dataLoaders import load_magazine_data_api


class ReservoirAnalysis:
    def __init__(self) -> None:
        self.filled_degree = None

    def rendertab1(self) -> None:
        option1, option2, option3 = st.columns(3)
        seasonal = option1.slider("Pick seasonal", 3, 51, value=13, step=2)
        trend = option2.slider("Pick trend", 53, 201, value=53, step=2)
        robust = option3.checkbox("Robust", value=True)

        stlAnalysis = stl_decomposition(
            self.filled_degree,
            period=52,
            seasonal=seasonal,
            trend=trend,
            robust=robust,
        )
        st.plotly_chart(stlAnalysis.fig)

        metric1, metric2, metric3, metric4 = st.columns(4)
        metric1.metric(
            "Trend strength",
            f"{stlAnalysis.stats['trend_strength']:.2f}",
        )
        metric2.metric(
            "Seasonal strength",
            f"{stlAnalysis.stats['seasonal_strength']:.2f}",
        )
        metric3.metric(
            "Residual std",
            f"{stlAnalysis.stats['residual_std']:.2f} pp",
        )
        metric4.metric(
            "Max reconstruction error",
            f"{stlAnalysis.stats['max_reconstruction_error']:.1e}",
        )

        st.caption(
            f"period 52 weeks · seasonal {stlAnalysis.stats['seasonal']} · "
            f"trend {stlAnalysis.stats['trend']} · "
            f"robust {stlAnalysis.stats['robust']}"
        )

        with st.expander("Full DataFrame"):
            st.dataframe(stlAnalysis.summary)

    def rendertab2(self) -> None:
        option1, option2 = st.columns(2)
        window = option1.slider("Pick window length", 8, 104, value=52)
        overlap = option2.slider(
            "Pick overlap", 0.0, 0.9, value=0.5, step=0.1
        )

        spectrogramAnalysis = spectrogram_plot(
            self.filled_degree,
            window=window,
            overlap=overlap,
        )
        st.plotly_chart(spectrogramAnalysis.fig)

        metric1, metric2, metric3 = st.columns(3)
        metric1.metric(
            "Peak frequency",
            f"{spectrogramAnalysis.stats['peak_frequency']:.4f} /week",
        )
        metric2.metric(
            "Peak period",
            f"{spectrogramAnalysis.stats['peak_period_weeks']:.1f} weeks",
        )
        metric3.metric(
            "Frequency resolution",
            f"{spectrogramAnalysis.stats['frequency_resolution']:.4f} /week",
        )

        st.caption(
            f"window {spectrogramAnalysis.stats['window']} weeks · "
            f"overlap {spectrogramAnalysis.stats['overlap']:.0%} · "
            f"{spectrogramAnalysis.stats['n_windows']} windows"
        )

        with st.expander("Full DataFrame"):
            st.dataframe(spectrogramAnalysis.summary)

    def renderPage(self) -> None:
        """render page"""

        magasin = load_magazine_data_api("1995-01-01", "2024-12-31")
        areaType, areaNr = areaSelector(magasin, "reservoirAnalysis")

        series = magasin[
            (magasin["omrType"] == areaType) & (magasin["omrnr"] == areaNr)
        ]

        self.filled_degree = (
            series.set_index("date (y-m-d)")["filled degree"]
            .sort_index()
            .dropna()
            * 100
        )

        if self.filled_degree.empty:
            st.info(f"No filling degree data for {areaType} {areaNr}.")
            st.stop()

        tab1, tab2 = st.tabs(["STL", "Spectrogram"])
        with tab1:
            self.rendertab1()

        with tab2:
            self.rendertab2()

    def run(self) -> None:
        """renders the page"""
        st.set_page_config(
            page_title="Reservoir Analysis",
            page_icon="🔬",
            layout="centered",
        )

        self.renderPage()


# ---
if __name__ == "__main__":
    try:
        ReservoirAnalysis().run()
    except Exception as e:
        st.error(e)
