"""
Turns raw survey rows into a connectivity score and effectiveness score,
then fits a simple linear regression between them:

    effectiveness = b0 + b1 * connectivity
"""

import numpy as np
import pandas as pd


def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Add connectivity_score and effectiveness_score columns to df."""
    df = df.copy()

    # Connectivity score (0-10): higher speed rating and affordability,
    # fewer disconnections, all pulled onto the same 0-10 scale.
    speed = pd.to_numeric(df["speed_rating"], errors="coerce")          # 1-5
    afford = pd.to_numeric(df["affordability_rating"], errors="coerce")  # 1-5
    disconnects = pd.to_numeric(df["weekly_disconnections"], errors="coerce")  # count

    # Normalize disconnections (more disconnections -> lower score).
    # Cap at 20/week so one outlier doesn't dominate the scale.
    disconnect_penalty = (disconnects.clip(upper=20) / 20) * 10

    df["connectivity_score"] = (
        (speed / 5) * 5 + (afford / 5) * 5 - disconnect_penalty * 0.5
    ).clip(lower=0, upper=10)

    # Effectiveness score (0-10): directly from self-rating, but nudged
    # down if the student reports low task completion.
    self_rating = pd.to_numeric(df["effectiveness_rating"], errors="coerce")  # 1-10
    completion = pd.to_numeric(df["task_completion_pct"], errors="coerce")    # 0-100

    df["effectiveness_score"] = (
        self_rating * 0.7 + (completion / 100 * 10) * 0.3
    ).clip(lower=0, upper=10)

    return df


def fit_simple_regression(x: pd.Series, y: pd.Series):
    """
    Fit y = b0 + b1*x using least squares (the same idea as MSE-minimizing
    gradient descent, solved directly here via the normal equation).

    Returns (b0, b1, r_squared, n).
    """
    mask = x.notna() & y.notna()
    x, y = x[mask].to_numpy(), y[mask].to_numpy()
    n = len(x)

    if n < 2:
        return None, None, None, n

    b1, b0 = np.polyfit(x, y, 1)

    y_pred = b0 + b1 * x
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0

    return round(b0, 3), round(b1, 3), round(r_squared, 3), n


def regression_line_points(x: pd.Series, b0: float, b1: float) -> pd.DataFrame:
    """Generate points for drawing the fitted line across the range of x."""
    x_min, x_max = x.min(), x.max()
    xs = np.linspace(x_min, x_max, 50)
    ys = b0 + b1 * xs
    return pd.DataFrame({"connectivity_score": xs, "fitted": ys})
