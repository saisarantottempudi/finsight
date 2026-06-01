from pydantic import BaseModel


class RiskMetricsResponse(BaseModel):
    portfolio_value: float
    daily_volatility: float
    annualized_volatility: float
    sharpe_ratio: float
    var_95: float
    var_99: float
    max_drawdown: float
