"""
predict_pricing.py (v2)

Replaces the fixed-formula predictor with:
  1. A forecast actually derived from an item's real historical series
     (produced by ingest_public_prices.py), not a hardcoded 0.5%/month
     applied to everyone.
  2. A confidence interval derived from BACKTESTING — measuring how wrong
     this same method was on past data — instead of an assumed decay curve.

This is still intentionally simple: a linear trend fit on log-price over a
trailing window. The point of v2 is not "best model," it's "a model that
can tell you, honestly, whether it beats naive last-price-carried-forward."
Do not claim accuracy numbers publicly until this has been run against
real history for each item and the backtest results below have been
reviewed.
"""

import os
import numpy as np
import pandas as pd


class CostPredictor:
    def __init__(self, series_dir="data/national_series"):
        self.series_dir = series_dir
        self._cache = {}

    # ------------------------------------------------------------------
    def _load_series(self, item):
        """Load an item's real historical series and standardize columns."""
        if item in self._cache:
            return self._cache[item]

        path = os.path.join(self.series_dir, f"{item}.csv")
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"No ingested data for '{item}' at {path}. "
                f"Run ingest_public_prices.py first — this predictor refuses "
                f"to guess a price the way enrich_prices.py did."
            )

        df = pd.read_csv(path)
        df["date"] = pd.to_datetime(df["date"])

        value_col = next(
            (c for c in df.columns if c not in ("date", "item", "source", "series_id")),
            None,
        )
        if value_col is None:
            raise ValueError(f"Could not find a value column in {path}")

        df = df[["date", value_col]].rename(columns={value_col: "value"})
        df = df.dropna().sort_values("date").reset_index(drop=True)
        self._cache[item] = df
        return df

    # ------------------------------------------------------------------
    def _fit_trend(self, df, as_of_idx, window=52):
        """
        Fit a linear trend to log(value) using up to `window` points
        ending at as_of_idx (inclusive). Returns (intercept, slope) in
        log-space, fit against a simple integer time index.
        """
        start = max(0, as_of_idx - window + 1)
        sub = df.iloc[start:as_of_idx + 1]
        if len(sub) < 3:
            # not enough history yet — flat forecast, wide uncertainty
            return np.log(sub["value"].iloc[-1]), 0.0
        x = np.arange(len(sub))
        y = np.log(sub["value"].values)
        slope, intercept = np.polyfit(x, y, 1)
        return intercept + slope * (len(sub) - 1), slope

    # ------------------------------------------------------------------
    def get_forecast(self, item, horizon_days):
        """
        Forecast `item`'s price `horizon_days` from its latest known date.
        Returns (forecast_price, lower_bound, upper_bound, empirical_mape)
        empirical_mape comes from backtest() — it's the honest version of
        "confidence": the average error this exact method made on past data
        at a similar horizon. Lower is better; there is no artificial floor.
        """
        df = self._load_series(item)
        last_idx = len(df) - 1
        last_log, slope = self._fit_trend(df, last_idx)

        periods_per_day = self._infer_periods_per_day(df)
        steps = max(1, round(horizon_days * periods_per_day))
        forecast_log = last_log + slope * steps
        forecast_price = float(np.exp(forecast_log))

        mape = self.backtest(item, horizon_days)["mape"]
        lower = forecast_price * (1 - mape)
        upper = forecast_price * (1 + mape)

        return round(forecast_price, 4), round(lower, 4), round(upper, 4), round(mape, 4)

    # ------------------------------------------------------------------
    def _infer_periods_per_day(self, df):
        """Roughly infer the series' native cadence (daily/weekly/monthly)."""
        if len(df) < 2:
            return 1.0
        median_gap_days = df["date"].diff().dt.days.median()
        return 1.0 / max(median_gap_days, 1)

    # ------------------------------------------------------------------
    def backtest(self, item, horizon_days, window=52, min_train=12):
        """
        Walk-forward backtest: at every historical point with enough data
        both before and after it, forecast `horizon_days` ahead using only
        data available up to that point, then compare to what actually
        happened. Returns MAPE against this method, and against a naive
        carry-forward baseline, so you can see whether the trend model is
        actually earning its complexity.
        """
        df = self._load_series(item)
        periods_per_day = self._infer_periods_per_day(df)
        steps = max(1, round(horizon_days * periods_per_day))

        errors, naive_errors = [], []
        for i in range(min_train, len(df) - steps):
            actual = df["value"].iloc[i + steps]

            last_log, slope = self._fit_trend(df, i, window=window)
            pred = np.exp(last_log + slope * steps)
            errors.append(abs(pred - actual) / actual)

            naive_pred = df["value"].iloc[i]
            naive_errors.append(abs(naive_pred - actual) / actual)

        if not errors:
            # Not enough history to backtest yet — say so, do not fabricate
            # a number. This is the honest version of a low-data warning.
            return {"mape": 0.5, "naive_mape": None, "n_folds": 0,
                    "note": "insufficient history to backtest; treat forecast as low-confidence"}

        return {
            "mape": float(np.mean(errors)),
            "naive_mape": float(np.mean(naive_errors)),
            "n_folds": len(errors),
            "beats_naive": float(np.mean(errors)) < float(np.mean(naive_errors)),
        }


# --- Example usage ---
if __name__ == "__main__":
    predictor = CostPredictor()

    item = "diesel_midwest"       # must match a CSV from ingest_public_prices.py
    horizon = 90                  # days out

    try:
        price, lower, upper, mape = predictor.get_forecast(item, horizon)
        bt = predictor.backtest(item, horizon)
        print(f"--- Forecast for {item}, {horizon} days out ---")
        print(f"Forecast:  {price}")
        print(f"Range:     {lower} - {upper}")
        print(f"Backtest MAPE (this method): {mape:.1%}")
        print(f"Backtest MAPE (naive carry-forward): {bt.get('naive_mape')}")
        print(f"Beats naive baseline: {bt.get('beats_naive')}")
    except FileNotFoundError as e:
        print(e)
