"""Analysis helpers for the weather page.

The functions accept a daily pandas Series and return an ``AnalysisResult``
containing a Plotly figure, a summary DataFrame and statistics.

The module deliberately does not import Streamlit and does not call
``fig.show()``; the page decides how to render the returned figure.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.graph_objects import Figure
from scipy import signal
from scipy.fft import dct, idct
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.seasonal import STL
from plotly.subplots import make_subplots


@dataclass
class AnalysisResult:
    """Container for one analysis result."""

    fig: Figure
    summary: pd.DataFrame
    stats: dict


def _base_layout(fig: Figure, title: str, y_title: str) -> None:
    """Apply the shared Plotly layout used by the analysis figures."""
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=y_title,
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=45, r=20, t=55, b=45),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )


def dct_spc_outliers(
    series: pd.Series,
    cutoff_days: int = 30,
    n_sigma: float = 3.0,
) -> AnalysisResult:
    """Flag daily precipitation outliers with DCT + robust SPC.

    The seasonal cycle is removed with a DCT high-pass filter. The
    residual (SATV) is used to estimate robust SPC bounds; the SATV
    itself is not plotted.

    Parameters
    ----------
    series : pandas.Series
        Daily precipitation with a DatetimeIndex.
    cutoff_days : int, optional
        Periods longer than this are removed. Default is 30.
    n_sigma : float, optional
        Width of the SPC band in robust standard deviations. Default is 3.

    Returns
    -------
    AnalysisResult
        Plotly figure, outlier summary and statistics.
    """
    x = series.to_numpy(dtype=float)
    n = len(x)

    # DCT-II coefficient k has period 2N/k samples.
    coefficients = dct(x, norm="ortho")
    cutoff_index = max(1, int(2 * n / cutoff_days))
    coefficients[:cutoff_index] = 0.0
    satv = idct(coefficients, norm="ortho")

    centre = float(np.median(satv))
    sigma = float(1.4826 * np.median(np.abs(satv - centre)))
    if sigma == 0:
        sigma = float(np.finfo(float).eps)

    lower_satv = centre - n_sigma * sigma
    upper_satv = centre + n_sigma * sigma

    baseline = x - satv
    lower = baseline + lower_satv
    upper = baseline + upper_satv

    outliers = (x < lower) | (x > upper)

    summary = pd.DataFrame(
        {
            "date": series.index[outliers],
            "value": x[outliers],
            "lower": lower[outliers],
            "upper": upper[outliers],
        }
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=x,
            mode="lines",
            name="Daily precipitation",
            line=dict(color="#1f77b4", width=1.5),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=lower,
            mode="lines",
            name=f"SPC lower ({n_sigma}σ)",
            line=dict(color="black", dash="dash", width=1),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=upper,
            mode="lines",
            name=f"SPC upper ({n_sigma}σ)",
            line=dict(color="black", dash="dash", width=1),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=series.index[outliers],
            y=x[outliers],
            mode="markers",
            name="Outlier",
            marker=dict(color="crimson", size=7, line=dict(width=0)),
        )
    )
    _base_layout(
        fig,
        f"Precipitation outliers — DCT + SPC (cutoff={cutoff_days} days, {n_sigma}σ)",
        "Precipitation (mm)",
    )

    stats = {
        "count": int(len(summary)),
        "percent": float(100 * len(summary) / len(series)),
        "cutoff_days": int(cutoff_days),
        "n_sigma": float(n_sigma),
        "median_satv": centre,
        "robust_sigma": sigma,
        "lower_satv": float(lower_satv),
        "upper_satv": float(upper_satv),
    }

    if not summary.empty:
        strongest = summary.loc[summary["value"].idxmax()]
        stats["strongest_date"] = strongest["date"]
        stats["strongest_value"] = float(strongest["value"])
    else:
        stats["strongest_date"] = None
        stats["strongest_value"] = None

    return AnalysisResult(fig=fig, summary=summary, stats=stats)


def lof_anomalies(
    series: pd.Series,
    contamination: float = 0.01,
    n_neighbors: int = 20,
) -> AnalysisResult:
    """Flag daily temperature anomalies with Local Outlier Factor.

    Parameters
    ----------
    series : pandas.Series
        Daily temperature with a DatetimeIndex.
    contamination : float, optional
        Expected share of anomalies. Default is 0.01.
    n_neighbors : int, optional
        Number of neighbours used by LOF. Default is 20.

    Returns
    -------
    AnalysisResult
        Plotly figure, anomaly summary and statistics.
    """
    values = series.to_numpy(dtype=float).reshape(-1, 1)
    scaled = StandardScaler().fit_transform(values)

    # LOF needs fewer neighbours than samples.
    n_neighbors = min(int(n_neighbors), max(2, len(series) - 1))

    labels = LocalOutlierFactor(
        n_neighbors=n_neighbors,
        contamination=contamination,
    ).fit_predict(scaled)
    anomalies = labels == -1

    summary = pd.DataFrame(
        {
            "date": series.index[anomalies],
            "value": series[anomalies],
        }
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=series,
            mode="lines",
            name="Daily temperature",
            line=dict(color="#ff7f0e", width=1.5),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=series.index[anomalies],
            y=series[anomalies],
            mode="markers",
            name="Anomaly",
            marker=dict(color="crimson", size=8, line=dict(width=0)),
        )
    )
    _base_layout(
        fig,
        f"Temperature anomalies — LOF (contamination={contamination:.0%})",
        "Temperature (°C)",
    )

    stats = {
        "count": int(len(summary)),
        "percent": float(100 * len(summary) / len(series)),
        "contamination": float(contamination),
        "n_neighbors": int(n_neighbors),
    }

    if not summary.empty:
        highest = summary.loc[summary["value"].idxmax()]
        lowest = summary.loc[summary["value"].idxmin()]
        stats["highest_date"] = highest["date"]
        stats["highest_value"] = float(highest["value"])
        stats["lowest_date"] = lowest["date"]
        stats["lowest_value"] = float(lowest["value"])
    else:
        stats["highest_date"] = None
        stats["highest_value"] = None
        stats["lowest_date"] = None
        stats["lowest_value"] = None

    return AnalysisResult(fig=fig, summary=summary, stats=stats)


def stl_decomposition(
    series: pd.Series,
    period: int = 52,
    seasonal: int = 13,
    trend: int = 53,
    robust: bool = True,
) -> AnalysisResult:
    """Decompose a weekly series with STL.

    Parameters
    ----------
    series : pandas.Series
        Weekly values with a DatetimeIndex, e.g. ``filled degree``.
    period : int, optional
        Seasonal period in samples. Default is 52 (one year of weeks).
    seasonal : int, optional
        Seasonal smoother length; must be odd and at least 3.
        Default is 13.
    trend : int, optional
        Trend smoother length; must be odd and greater than ``period``.
        Default is 53.
    robust : bool, optional
        Down-weight outliers. Default is True.

    Returns
    -------
    AnalysisResult
        Plotly four-panel figure, component table and statistics.
    """
    if series.isna().any():
        raise ValueError("series must not contain NaNs")
    if period < 2:
        raise ValueError("period must be at least 2")
    if len(series) < 2 * period:
        raise ValueError(
            f"series needs at least {2 * period} observations for period={period}"
        )
    if seasonal < 3 or seasonal % 2 == 0:
        raise ValueError("seasonal must be an odd integer >= 3")
    if trend < 3 or trend % 2 == 0 or trend <= period:
        raise ValueError("trend must be an odd integer greater than period")

    result = STL(
        series,
        period=period,
        seasonal=seasonal,
        trend=trend,
        robust=robust,
    ).fit()

    observed = series.to_numpy(dtype=float)
    trend_values = result.trend.to_numpy(dtype=float)
    seasonal_values = result.seasonal.to_numpy(dtype=float)
    residual = result.resid.to_numpy(dtype=float)

    summary = pd.DataFrame(
        {
            "time": series.index,
            "observed": observed,
            "trend": trend_values,
            "seasonal": seasonal_values,
            "residual": residual,
        }
    )

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        subplot_titles=("Observed", "Trend", "Seasonal", "Residual"),
        vertical_spacing=0.06,
    )
    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=observed,
            mode="lines",
            name="Observed",
            line=dict(color="#1f77b4"),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=trend_values,
            mode="lines",
            name="Trend",
            line=dict(color="#ff7f0e"),
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=seasonal_values,
            mode="lines",
            name="Seasonal",
            line=dict(color="#2ca02c"),
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=residual,
            mode="lines",
            name="Residual",
            line=dict(color="#d62728"),
        ),
        row=4,
        col=1,
    )
    fig.update_layout(
        title=(
            f"STL decomposition (period={period}, seasonal={seasonal}, "
            f"trend={trend}, robust={robust})"
        ),
        template="plotly_white",
        height=900,
        showlegend=False,
        hovermode="x unified",
        margin=dict(l=45, r=20, t=70, b=45),
    )
    fig.update_xaxes(title_text="Date", row=4, col=1)
    fig.update_yaxes(title_text="Filled degree (%)", row=1, col=1)

    residual_variance = float(np.var(residual, ddof=1))
    trend_variance = float(np.var(trend_values + residual, ddof=1))
    seasonal_variance = float(np.var(seasonal_values + residual, ddof=1))

    trend_strength = (
        max(0.0, 1.0 - residual_variance / trend_variance)
        if trend_variance > 0
        else 0.0
    )
    seasonal_strength = (
        max(0.0, 1.0 - residual_variance / seasonal_variance)
        if seasonal_variance > 0
        else 0.0
    )

    reconstructed = trend_values + seasonal_values + residual
    stats = {
        "period": int(period),
        "seasonal": int(seasonal),
        "trend": int(trend),
        "robust": bool(robust),
        "n_observations": int(len(series)),
        "max_reconstruction_error": float(np.max(np.abs(reconstructed - observed))),
        "residual_std": float(np.std(residual, ddof=1)),
        "trend_strength": float(trend_strength),
        "seasonal_strength": float(seasonal_strength),
    }

    return AnalysisResult(fig=fig, summary=summary, stats=stats)


def spectrogram_plot(
    series: pd.Series,
    window: int = 52,
    overlap: float = 0.5,
) -> AnalysisResult:
    """Plot a spectrogram of a weekly series.

    Parameters
    ----------
    series : pandas.Series
        Weekly values with a DatetimeIndex.
    window : int, optional
        Window length in weeks. Default is 52.
    overlap : float, optional
        Fractional overlap between windows, in [0, 1). Default is 0.5.

    Returns
    -------
    AnalysisResult
        Plotly heatmap, per-window peak table and statistics.
    """
    if series.isna().any():
        raise ValueError("series must not contain NaNs")
    if window < 2:
        raise ValueError("window must be at least 2")
    if not 0 <= overlap < 1:
        raise ValueError("overlap must be in [0, 1)")

    values = series.to_numpy(dtype=float)
    nperseg = min(int(window), len(values))
    if nperseg < 2:
        raise ValueError("series is too short for a spectrogram")

    noverlap = int(nperseg * overlap)

    freqs, times, power = signal.spectrogram(
        values,
        fs=1.0,
        nperseg=nperseg,
        noverlap=noverlap,
        detrend="linear",
        scaling="density",
    )

    dates = series.index[0] + pd.to_timedelta(times * 7, unit="D")
    power_db = 10 * np.log10(power + 1e-12)

    # Ignore the zero-frequency bin when finding the dominant cycle,
    # otherwise a slow trend would always win.
    mean_power = power_db.mean(axis=1)
    if len(mean_power) > 1:
        peak_index = int(np.argmax(mean_power[1:]) + 1)
    else:
        peak_index = 0

    if len(freqs) > 1:
        window_peak_index = np.argmax(power_db[1:, :], axis=0) + 1
    else:
        window_peak_index = np.zeros(power_db.shape[1], dtype=int)

    summary = pd.DataFrame(
        {
            "time": dates,
            "peak_frequency": freqs[window_peak_index],
            "peak_power_db": power_db[window_peak_index, np.arange(len(dates))],
        }
    )

    fig = go.Figure(
        go.Heatmap(
            x=dates,
            y=freqs,
            z=power_db,
            colorscale="Viridis",
            colorbar=dict(title="Power (dB)"),
            hovertemplate=(
                "Date=%{x}<br>"
                "Frequency=%{y:.4f} cycles/week<br>"
                "Power=%{z:.2f} dB<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title=(f"Spectrogram (window={nperseg} weeks, overlap={overlap:.0%})"),
        xaxis_title="Date",
        yaxis_title="Frequency (cycles/week)",
        template="plotly_white",
        height=500,
        margin=dict(l=50, r=20, t=55, b=45),
    )

    peak_frequency = float(freqs[peak_index])
    stats = {
        "peak_frequency": peak_frequency,
        "peak_period_weeks": (
            float(1.0 / peak_frequency) if peak_frequency > 0 else None
        ),
        "frequency_resolution": (
            float(freqs[1] - freqs[0]) if len(freqs) > 1 else None
        ),
        "window": int(nperseg),
        "overlap": float(overlap),
        "n_windows": int(power.shape[1]),
        "n_frequencies": int(power.shape[0]),
    }

    return AnalysisResult(fig=fig, summary=summary, stats=stats)
