# Data Dictionary - UITF Trading Dataset

## Dataset Schema

| Feature Name | Data Type | Description | Expected Values |
|--------------|-----------|-------------|-----------------|
| `date` | Date | Trading date in standardized format | YYYY-MM-DD (2019-01-01 to present) |
| `original_label` | String | Original date label from data source | "MMM DD, YYYY" format (e.g., "Jan 15, 2024") |
| `navpu_value` | Float | Net Asset Value Per Unit - daily fund price | 0.50 - 3.00 (typical UITF range) |
| `buy` | Integer | Binary buy signal indicator | 0 (No Buy), 1 (Buy) |
| `buy_strength` | Integer | Signal strength score based on multiple criteria | 0 - 6 (higher = stronger signal) |
| `price_change` | Float | Daily percentage price change (decimal format) | -0.10 to 0.10 (-10% to +10% typical daily range) |
| `ma_7` | Float | 7-day Simple Moving Average of navpu_value | Similar range to navpu_value |
| `ma_30` | Float | 30-day Simple Moving Average of navpu_value | Similar range to navpu_value |
| `rsi` | Float | 14-day Relative Strength Index | 0.0 - 100.0 (oversold <30, overbought >70) |
| `buy_reason` | String | Explanation of triggered buy signals | See categorical values below |
| `future_return_7d` | Float | Actual return 7 days forward (decimal format) | -0.20 to 0.20 (-20% to +20% typical 7-day range) |
| `future_return_30d` | Float | Actual return 30 days forward (decimal format) | -0.40 to 0.40 (-40% to +40% typical 30-day range) |
