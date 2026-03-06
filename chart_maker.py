import io
import warnings
import plotly.graph_objects as go
import plotly.express as px
from utils import extract_json_from_response

CHART_COLORS = [
    "#4C9BE8", "#E85C4C", "#4CE87A", "#E8C44C", "#9B4CE8",
    "#E84CA0", "#4CE8D8", "#E88C4C", "#7AE84C", "#4C7AE8",
]

DARK_LAYOUT = dict(
    paper_bgcolor="#1E1E2E",
    plot_bgcolor="#1E1E2E",
    font=dict(color="#CDD6F4", size=13),
    title_font=dict(size=16, color="#CDD6F4"),
    legend=dict(bgcolor="#313244", bordercolor="#45475A", borderwidth=1),
    margin=dict(l=60, r=30, t=60, b=60),
)


def try_make_chart(ai_response: str) -> go.Figure | None:
    """
    Parse AI response and attempt to build a Plotly chart.
    Returns None if the response is not a valid chart spec.
    """
    spec = extract_json_from_response(ai_response)
    if spec is None:
        return None

    chart_type = spec.get("chart_type", "").lower()
    if chart_type not in ("bar", "line", "pie", "scatter", "heatmap"):
        return None

    try:
        if chart_type == "bar":
            return _make_bar(spec)
        elif chart_type == "line":
            return _make_line(spec)
        elif chart_type == "pie":
            return _make_pie(spec)
        elif chart_type == "scatter":
            return _make_scatter(spec)
        elif chart_type == "heatmap":
            return _make_heatmap(spec)
    except Exception as e:
        warnings.warn(f"Chart render failed: {e}")
        return None


def _apply_layout(fig: go.Figure, spec: dict) -> go.Figure:
    fig.update_layout(
        title=spec.get("title", ""),
        xaxis_title=spec.get("x_label", ""),
        yaxis_title=spec.get("y_label", ""),
        **DARK_LAYOUT,
    )
    return fig


def _make_bar(spec: dict) -> go.Figure:
    labels = spec.get("labels", [])
    values = spec.get("values", [])
    secondary = spec.get("secondary_values", [])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=values,
        name=spec.get("y_label", "Value"),
        marker_color=CHART_COLORS[:len(labels)],
    ))
    if secondary:
        fig.add_trace(go.Bar(
            x=labels, y=secondary,
            name="Secondary",
            marker_color=CHART_COLORS[5:5 + len(labels)],
        ))
        fig.update_layout(barmode="group")

    return _apply_layout(fig, spec)


def _make_line(spec: dict) -> go.Figure:
    labels = spec.get("labels", [])
    values = spec.get("values", [])
    secondary = spec.get("secondary_values", [])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=values,
        mode="lines+markers",
        name=spec.get("y_label", "Value"),
        line=dict(color=CHART_COLORS[0], width=2),
        marker=dict(size=8),
    ))
    if secondary:
        fig.add_trace(go.Scatter(
            x=labels, y=secondary,
            mode="lines+markers",
            name="Secondary",
            line=dict(color=CHART_COLORS[1], width=2),
            marker=dict(size=8),
        ))

    return _apply_layout(fig, spec)


def _make_pie(spec: dict) -> go.Figure:
    labels = spec.get("labels", [])
    values = spec.get("values", [])

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.4,  # donut style
        marker=dict(colors=CHART_COLORS),
        textinfo="label+percent",
        textfont_size=12,
    ))
    fig.update_layout(
        title=spec.get("title", ""),
        **DARK_LAYOUT,
    )
    return fig


def _make_scatter(spec: dict) -> go.Figure:
    labels = spec.get("labels", [])
    values = spec.get("values", [])

    fig = go.Figure(go.Scatter(
        x=labels, y=values,
        mode="markers",
        marker=dict(color=CHART_COLORS[0], size=10, opacity=0.8),
        name=spec.get("y_label", "Value"),
    ))
    return _apply_layout(fig, spec)


def _make_heatmap(spec: dict) -> go.Figure:
    labels = spec.get("labels", [])
    values = spec.get("values", [])
    secondary = spec.get("secondary_values", [])

    # Build z-matrix: if secondary exists, use it as second dimension
    if secondary:
        z = [values, secondary]
        y = [spec.get("y_label", "Series 1"), "Series 2"]
    else:
        z = [values]
        y = [spec.get("y_label", "Value")]

    fig = go.Figure(go.Heatmap(
        x=labels, y=y, z=z,
        colorscale="Blues",
    ))
    return _apply_layout(fig, spec)


def chart_to_png(fig: go.Figure) -> bytes | None:
    """Export Plotly figure to PNG bytes using kaleido."""
    try:
        return fig.to_image(format="png", width=900, height=500, scale=2)
    except Exception as e:
        warnings.warn(f"PNG export failed (is kaleido installed?): {e}")
        return None
