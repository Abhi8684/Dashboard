import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import os

from data_processor import (
    load_excel,
    compute_kpis,
    get_month_label,
    get_completed_by_panel,
    get_today_tasks_by_panel,
    get_status_distribution,
    get_daily_status_breakdown,
)

# ── Color palette matching the user's dark dashboard ──
BG_COLOR = "#1a1a2e"
CARD_COLOR = "#16213e"
ACCENT_BLUE = "#4a90d9"
GREEN = "#2ecc71"
ORANGE = "#e67e22"
RED = "#e74c3c"
TEXT_COLOR = "#ecf0f1"
GRID_COLOR = "#2c3e50"

STATUS_COLORS = {
    "Completed": GREEN,
    "completed": GREEN,
    "Ongoing": ORANGE,
    "ongoing": ORANGE,
    "Hold": RED,
    "hold": RED,
}

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")


def _get_latest_file():
    """Return the most recently uploaded Excel file path, or None."""
    if os.path.isdir(UPLOAD_DIR):
        files = [
            os.path.join(UPLOAD_DIR, f)
            for f in os.listdir(UPLOAD_DIR)
            if f.lower().endswith((".xlsx", ".xls"))
        ]
        if files:
            return max(files, key=os.path.getmtime)
    return None


def create_dash_app(flask_server):
    """Create and return the Dash application mounted on the Flask server."""

    app = dash.Dash(
        __name__,
        server=flask_server,
        url_base_pathname="/dashboard/",
        suppress_callback_exceptions=True,
    )

    app.layout = html.Div(
        id="dashboard-root",
        style={
            "backgroundColor": BG_COLOR,
            "minHeight": "100vh",
            "fontFamily": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        },
        children=[
            dcc.Location(id="url", refresh=False),

            # ── Header ──
            html.Div(
                style={
                    "background": "linear-gradient(135deg, #0f3460 0%, #16213e 100%)",
                    "padding": "16px 24px",
                    "borderBottom": "2px solid #4a90d9",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                },
                children=[
                    html.H1(
                        "📊 Task Management Dashboard",
                        style={
                            "color": TEXT_COLOR,
                            "margin": 0,
                            "fontSize": "22px",
                            "fontWeight": "700",
                        },
                    ),
                    html.A(
                        "⬆ Upload New File",
                        href="/",
                        style={
                            "color": ACCENT_BLUE,
                            "textDecoration": "none",
                            "fontSize": "14px",
                            "border": f"1px solid {ACCENT_BLUE}",
                            "padding": "6px 14px",
                            "borderRadius": "6px",
                        },
                    ),
                ],
            ),

            # ── Main dashboard content ──
            html.Div(id="dashboard-content", style={"padding": "20px"}),
        ],
    )

    @app.callback(
        Output("dashboard-content", "children"),
        Input("url", "pathname"),
    )
    def render_dashboard(_pathname):
        excel_path = _get_latest_file()

        if not excel_path or not os.path.exists(excel_path):
            return html.Div(
                [
                    html.H3(
                        "No data loaded.",
                        style={
                            "color": TEXT_COLOR,
                            "textAlign": "center",
                            "marginTop": "80px",
                        },
                    ),
                    html.P(
                        html.A(
                            "← Go back and upload an Excel file",
                            href="/",
                            style={"color": ACCENT_BLUE},
                        ),
                        style={"textAlign": "center"},
                    ),
                ]
            )

        try:
            # Detect if the workbook has multiple sheets and pick the right one
            from openpyxl import load_workbook as _lwb
            wb = _lwb(excel_path, read_only=True, data_only=True)
            sheet_names = wb.sheetnames
            wb.close()

            target_sheet = None
            if len(sheet_names) > 1 and "Daily_Activity_Tracker" in sheet_names:
                target_sheet = "Daily_Activity_Tracker"

            df = load_excel(excel_path, sheet_name=target_sheet)

            kpis = compute_kpis(df)
            month_label = get_month_label(df)

            return html.Div(
                [
                    _render_kpi_cards(kpis, month_label),
                    html.Div(style={"height": "20px"}),
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "1fr 1fr 1fr",
                            "gap": "16px",
                        },
                        children=[
                            _render_completed_by_panel(df, month_label),
                            _render_today_tasks(df),
                            _render_status_pie(df),
                        ],
                    ),
                    html.Div(style={"height": "20px"}),
                    _render_daily_stacked(df, month_label),
                ]
            )
        except Exception as exc:
            import traceback as _tb
            err_text = _tb.format_exc()
            print(err_text, flush=True)
            return html.Div(
                html.P(
                    f"Error: {exc}",
                    style={"color": RED, "textAlign": "center", "marginTop": "80px"},
                )
            )

    return app


# ─── KPI Cards ──────────────────────────────────────────────────────────────

def _render_kpi_cards(kpis: dict, month_label: str):
    cards = [
        (f"Total Task\n{month_label}", kpis["total_tasks"]),
        ("Total Task\nCompleted", kpis["total_completed"]),
        ("Delay\nCompletion", kpis["delay_completion"]),
        ("Task\nToday", kpis["tasks_today"]),
        ("Task Completed\nToday", kpis["completed_today"]),
    ]

    card_divs = [
        html.Div(
            style={
                "background": "linear-gradient(135deg, #1565c0 0%, #4a90d9 100%)",
                "borderRadius": "10px",
                "padding": "16px 20px",
                "textAlign": "center",
                "boxShadow": "0 4px 15px rgba(74,144,217,0.3)",
                "border": "1px solid #4a90d9",
            },
            children=[
                html.P(
                    label,
                    style={
                        "color": "#b3d4f0",
                        "margin": "0 0 6px",
                        "fontSize": "11px",
                        "fontWeight": "600",
                        "textTransform": "uppercase",
                        "letterSpacing": "0.5px",
                        "whiteSpace": "pre-line",
                    },
                ),
                html.H2(
                    str(value),
                    style={
                        "color": "white",
                        "margin": 0,
                        "fontSize": "32px",
                        "fontWeight": "800",
                    },
                ),
            ],
        )
        for label, value in cards
    ]

    return html.Div(
        style={
            "display": "grid",
            "gridTemplateColumns": "repeat(5, 1fr)",
            "gap": "14px",
        },
        children=card_divs,
    )


# ─── Chart container ─────────────────────────────────────────────────────────

def _chart_container(title: str, graph_id: str, figure, height="280px"):
    return html.Div(
        style={
            "backgroundColor": CARD_COLOR,
            "borderRadius": "10px",
            "padding": "16px",
            "boxShadow": "0 4px 15px rgba(0,0,0,0.4)",
            "border": f"1px solid {GRID_COLOR}",
        },
        children=[
            html.H4(
                title,
                style={
                    "color": TEXT_COLOR,
                    "margin": "0 0 12px",
                    "fontSize": "13px",
                    "fontWeight": "700",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.5px",
                },
            ),
            dcc.Graph(
                id=graph_id,
                figure=figure,
                config={"displayModeBar": False},
                style={"height": height},
            ),
        ],
    )


def _base_layout():
    return dict(
        plot_bgcolor=CARD_COLOR,
        paper_bgcolor=CARD_COLOR,
        font=dict(color=TEXT_COLOR, family="Segoe UI"),
        margin=dict(l=10, r=10, t=10, b=40),
        legend=dict(font=dict(color=TEXT_COLOR), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(color=TEXT_COLOR)),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(color=TEXT_COLOR)),
    )


# ─── Individual charts ───────────────────────────────────────────────────────

def _render_completed_by_panel(df, month_label: str):
    data = get_completed_by_panel(df)

    if data.empty:
        fig = go.Figure(layout=_base_layout())
        fig.update_layout(
            annotations=[dict(text="No completed data", showarrow=False, font=dict(color=TEXT_COLOR))]
        )
    else:
        fig = go.Figure(
            go.Bar(
                x=data["panel"],
                y=data["count"],
                text=data["count"],
                textposition="outside",
                textfont=dict(color=TEXT_COLOR),
                marker_color=GREEN,
            )
        )
        layout = _base_layout()
        layout["xaxis"] = dict(
            tickangle=-30,
            gridcolor=GRID_COLOR,
            tickfont=dict(color=TEXT_COLOR, size=10),
        )
        layout["yaxis"] = dict(gridcolor=GRID_COLOR, tickfont=dict(color=TEXT_COLOR))
        layout["bargap"] = 0.3
        fig.update_layout(**layout)

    return _chart_container(f"{month_label} Completed", "chart-completed-panel", fig)


def _render_today_tasks(df):
    data = get_today_tasks_by_panel(df)

    if data.empty:
        fig = go.Figure(layout=_base_layout())
        fig.update_layout(
            annotations=[dict(text="No ongoing tasks today", showarrow=False, font=dict(color=TEXT_COLOR))]
        )
    else:
        fig = go.Figure(
            go.Bar(
                x=data["count"],
                y=data["panel"],
                orientation="h",
                text=data["count"],
                textposition="outside",
                textfont=dict(color=TEXT_COLOR),
                marker_color=ORANGE,
            )
        )
        layout = _base_layout()
        layout["margin"] = dict(l=180, r=50, t=10, b=30)
        layout["yaxis"] = dict(
            gridcolor=GRID_COLOR,
            autorange="reversed",
            tickfont=dict(color=TEXT_COLOR, size=10),
        )
        layout["xaxis"] = dict(gridcolor=GRID_COLOR, tickfont=dict(color=TEXT_COLOR))
        fig.update_layout(**layout)

    return _chart_container("Today Task Planned For Asset", "chart-today-panel", fig)


def _render_status_pie(df):
    data = get_status_distribution(df)

    if data.empty:
        fig = go.Figure(layout=_base_layout())
    else:
        colors = [STATUS_COLORS.get(s, ACCENT_BLUE) for s in data["status"]]
        fig = go.Figure(
            go.Pie(
                labels=data["status"],
                values=data["count"],
                hole=0.25,
                marker=dict(colors=colors, line=dict(color=BG_COLOR, width=2)),
                textinfo="label+value",
                textfont=dict(color=TEXT_COLOR, size=11),
            )
        )
        fig.update_layout(
            plot_bgcolor=CARD_COLOR,
            paper_bgcolor=CARD_COLOR,
            font=dict(color=TEXT_COLOR),
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
            legend=dict(
                orientation="v",
                font=dict(color=TEXT_COLOR),
                bgcolor="rgba(0,0,0,0)",
            ),
        )

    return _chart_container("Current Status Distribution", "chart-status-pie", fig)


def _render_daily_stacked(df, month_label: str):
    data = get_daily_status_breakdown(df)

    if data.empty:
        fig = go.Figure(layout=_base_layout())
        fig.update_layout(
            annotations=[dict(text="No date data found", showarrow=False, font=dict(color=TEXT_COLOR))]
        )
    else:
        all_dates = data["date_label"].unique().tolist()
        statuses = ["Completed", "Ongoing", "Hold"]
        traces = []

        for status in statuses:
            sub = data[data["status"].str.strip() == status]
            date_count = dict(zip(sub["date_label"], sub["count"]))
            counts = [date_count.get(d, 0) for d in all_dates]

            traces.append(
                go.Bar(
                    name=status,
                    x=all_dates,
                    y=counts,
                    text=[str(c) if c > 0 else "" for c in counts],
                    textposition="inside",
                    textfont=dict(color="white", size=11),
                    marker_color=STATUS_COLORS.get(status, ACCENT_BLUE),
                    marker_line_width=0,
                )
            )

        fig = go.Figure(data=traces)
        layout = _base_layout()
        layout["barmode"] = "stack"
        layout["bargap"] = 0.2
        layout["xaxis"] = dict(
            title=dict(text=month_label, font=dict(color=TEXT_COLOR, size=12)),
            gridcolor=GRID_COLOR,
            tickfont=dict(color=TEXT_COLOR),
        )
        layout["yaxis"] = dict(gridcolor=GRID_COLOR, tickfont=dict(color=TEXT_COLOR))
        layout["margin"] = dict(l=40, r=20, t=20, b=60)
        layout["legend"] = dict(
            orientation="v",
            font=dict(color=TEXT_COLOR),
            bgcolor="rgba(0,0,0,0)",
        )
        fig.update_layout(**layout)

    return html.Div(
        style={
            "backgroundColor": CARD_COLOR,
            "borderRadius": "10px",
            "padding": "16px",
            "boxShadow": "0 4px 15px rgba(0,0,0,0.4)",
            "border": f"1px solid {GRID_COLOR}",
        },
        children=[
            html.H4(
                "Daily Task Breakdown",
                style={
                    "color": TEXT_COLOR,
                    "margin": "0 0 12px",
                    "fontSize": "13px",
                    "fontWeight": "700",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.5px",
                },
            ),
            dcc.Graph(
                id="chart-daily-stacked",
                figure=fig,
                config={"displayModeBar": False},
                style={"height": "340px"},
            ),
        ],
    )
