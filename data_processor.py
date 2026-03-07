import pandas as pd
from datetime import datetime, date


def load_excel(filepath: str, sheet_name: str | None = None) -> pd.DataFrame:
    """Load and clean the Excel file into a DataFrame."""
    df = pd.read_excel(filepath, sheet_name=sheet_name or 0, engine="openpyxl")

    # Normalize column names: strip whitespace, lowercase for internal use
    df.columns = df.columns.str.strip()

    # Try to find the date column
    date_col = _find_column(df, ["Date", "date"])
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")

    # Normalize Current Status: fill blank with "Ongoing"
    status_col = _find_column(df, ["Current Status", "Status", "current status"])
    if status_col:
        df[status_col] = df[status_col].fillna("Ongoing").str.strip()
        df[status_col] = df[status_col].replace("", "Ongoing")

    return df


def _find_column(df: pd.DataFrame, candidates: list) -> str | None:
    """Return the first matching column name from candidates."""
    for c in candidates:
        if c in df.columns:
            return c
    # case-insensitive fallback
    lower_cols = {col.lower(): col for col in df.columns}
    for c in candidates:
        if c.lower() in lower_cols:
            return lower_cols[c.lower()]
    return None


def compute_kpis(df: pd.DataFrame) -> dict:
    """Compute all KPI values for the top cards."""
    status_col = _find_column(df, ["Current Status", "Status"])
    date_col = _find_column(df, ["Date", "date"])

    total_tasks = len(df)

    completed = 0
    if status_col:
        completed = int((df[status_col].str.lower() == "completed").sum())

    today = date.today()
    tasks_today = 0
    completed_today = 0
    if date_col:
        today_mask = df[date_col].dt.date == today
        tasks_today = int(today_mask.sum())
        if status_col:
            completed_today = int(
                (today_mask & (df[status_col].str.lower() == "completed")).sum()
            )

    # Delay Completion: tasks where status is Ongoing/Hold (not completed)
    delay = 0
    if status_col:
        delay = int((df[status_col].str.lower().isin(["ongoing", "hold"])).sum())

    return {
        "total_tasks": total_tasks,
        "total_completed": completed,
        "delay_completion": delay,
        "tasks_today": tasks_today,
        "completed_today": completed_today,
    }


def get_month_label(df: pd.DataFrame) -> str:
    """Return month label like 'FEB 2026'."""
    date_col = _find_column(df, ["Date", "date"])
    if date_col and not df[date_col].dropna().empty:
        first_date = df[date_col].dropna().iloc[0]
        return first_date.strftime("%b %Y").upper()
    return "MONTH"


def get_completed_by_panel(df: pd.DataFrame) -> pd.DataFrame:
    """Completed tasks grouped by Panel (asset type)."""
    status_col = _find_column(df, ["Current Status", "Status"])
    panel_col = _find_column(df, ["Panel", "panel", "Asset", "asset"])

    if status_col and panel_col:
        mask = df[status_col].str.lower() == "completed"
        result = (
            df[mask]
            .groupby(panel_col)
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        result.columns = ["panel", "count"]
        return result

    return pd.DataFrame(columns=["panel", "count"])


def get_today_tasks_by_panel(df: pd.DataFrame) -> pd.DataFrame:
    """Today's Ongoing tasks grouped by Panel."""
    status_col = _find_column(df, ["Current Status", "Status"])
    panel_col = _find_column(df, ["Panel", "panel", "Asset", "asset"])
    date_col = _find_column(df, ["Date", "date"])

    if status_col and panel_col and date_col:
        today = date.today()
        today_mask = df[date_col].dt.date == today

        # If no today data, use the most recent date
        if today_mask.sum() == 0:
            latest = df[date_col].dropna().max()
            if pd.notna(latest):
                today_mask = df[date_col].dt.date == latest.date()

        ongoing_mask = df[status_col].str.lower() == "ongoing"
        result = (
            df[today_mask & ongoing_mask]
            .groupby(panel_col)
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        result.columns = ["panel", "count"]
        return result

    return pd.DataFrame(columns=["panel", "count"])


def get_status_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Overall status distribution (Completed, Ongoing, Hold)."""
    status_col = _find_column(df, ["Current Status", "Status"])

    if status_col:
        result = (
            df[status_col]
            .str.strip()
            .value_counts()
            .reset_index()
        )
        result.columns = ["status", "count"]
        return result

    return pd.DataFrame(columns=["status", "count"])


def get_daily_status_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Daily stacked bar data: date × status counts."""
    status_col = _find_column(df, ["Current Status", "Status"])
    date_col = _find_column(df, ["Date", "date"])

    if status_col and date_col:
        df2 = df[[date_col, status_col]].copy()
        df2[date_col] = df2[date_col].dt.date
        result = (
            df2.groupby([date_col, status_col])
            .size()
            .reset_index(name="count")
        )
        result.columns = ["date", "status", "count"]
        result["date"] = pd.to_datetime(result["date"])
        result = result.sort_values("date")
        result["date_label"] = result["date"].dt.strftime("%d-%b")
        return result

    return pd.DataFrame(columns=["date", "status", "count", "date_label"])
