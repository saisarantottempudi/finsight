from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class RiskMetrics:
    portfolio_value: float
    daily_volatility: float
    annualized_volatility: float
    sharpe_ratio: float
    var_95: float
    var_99: float
    max_drawdown: float


class RiskEngine:
    RISK_FREE_RATE = 0.05  # 5% annualized

    def compute(self, prices: pd.DataFrame, weights: dict[str, float]) -> RiskMetrics:
        returns = prices.pct_change().dropna()
        symbols = [s for s in weights if s in returns.columns]
        if not symbols:
            raise ValueError("No matching symbols in price data")

        w = np.array([weights[s] for s in symbols], dtype=float)
        w = w / w.sum()

        portfolio_returns = returns[symbols].dot(w)
        daily_vol = float(portfolio_returns.std())
        annual_vol = daily_vol * np.sqrt(252)

        mean_daily = float(portfolio_returns.mean())
        excess = mean_daily - (self.RISK_FREE_RATE / 252)
        sharpe = (excess / daily_vol) * np.sqrt(252) if daily_vol > 0 else 0.0

        var_95 = float(np.percentile(portfolio_returns, 5))
        var_99 = float(np.percentile(portfolio_returns, 1))

        cumulative = (1 + portfolio_returns).cumprod()
        rolling_max = cumulative.cummax()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_dd = float(drawdown.min())

        portfolio_value = sum(weights[s] for s in symbols)

        return RiskMetrics(
            portfolio_value=round(portfolio_value, 2),
            daily_volatility=round(daily_vol, 6),
            annualized_volatility=round(annual_vol, 6),
            sharpe_ratio=round(sharpe, 4),
            var_95=round(var_95, 6),
            var_99=round(var_99, 6),
            max_drawdown=round(max_dd, 6),
        )
