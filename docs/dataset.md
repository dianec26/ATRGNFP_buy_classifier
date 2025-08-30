# UITF Trading Dataset Documentation

## Overview

This dataset contains historical Unit Investment Trust Fund (UITF) data with technical analysis indicators and algorithmic buy signals. The data is specifically for **ATRGFNP** (ATR Global Fund) from the Philippines, extracted from uitf.com.ph and enhanced with quantitative trading signals.

## Dataset Structure

The dataset contains **12 columns** with daily trading data spanning from 2019 to present:

### Core Data Fields

| Column | Type | Description |
|--------|------|-------------|
| `date` | Date | Trading date in YYYY-MM-DD format |
| `original_label` | String | Original date label from source (e.g., "Jan 15, 2024") |
| `navpu_value` | Float | Net Asset Value Per Unit - the fund's daily price |

### Technical Analysis Indicators

| Column | Type | Description |
|--------|------|-------------|
| `price_change` | Float | Daily price change percentage (decimal format) |
| `ma_7` | Float | 7-day Simple Moving Average |
| `ma_30` | Float | 30-day Simple Moving Average |
| `rsi` | Float | 14-day Relative Strength Index (0-100 scale) |

### Trading Signals

| Column | Type | Description |
|--------|------|-------------|
| `buy` | Integer | Binary buy signal (1 = Buy, 0 = Hold/No Action) |
| `buy_strength` | Integer | Signal strength score (0-6 based on multiple criteria) |
| `buy_reason` | String | Explanation of why buy signal was triggered |

### Forward-Looking Performance

| Column | Type | Description |
|--------|------|-------------|
| `future_return_7d` | Float | Actual return 7 days after this date (decimal format) |
| `future_return_30d` | Float | Actual return 30 days after this date (decimal format) |

## Buy Signal Strategy

The dataset implements a **multi-factor buy signal system** with 6 different strategies:

### 1. Golden Cross
- **Trigger**: 7-day MA crosses above 30-day MA
- **Logic**: Short-term momentum overtaking long-term trend

### 2. RSI Oversold Recovery
- **Trigger**: RSI was ≤30 (oversold), now >35 (recovery)
- **Logic**: Bounce back from oversold conditions

### 3. Dip Recovery
- **Trigger**: 7-day decline >5%, then daily gain >2%
- **Logic**: Buying the dip after significant decline

### 4. Near Support Level
- **Trigger**: Price within 2% of 30-day low + RSI <50
- **Logic**: Price approaching support with moderate momentum

### 5. Strong Uptrend
- **Trigger**: Price above all MAs + 7-day gain >2%
- **Logic**: Momentum trading in established uptrends

### 6. Dollar Cost Averaging (DCA)
- **Trigger**: First trading day of each month
- **Logic**: Systematic monthly investment strategy

## Data Quality Notes

- **Lookback Period**: Technical indicators require minimum periods (e.g., RSI needs 14 days)
- **Future Returns**: Last 30 rows will have NaN values for `future_return_30d`
- **Missing Values**: Early rows may have NaN for moving averages and RSI
- **Data Source**: Real-time extraction from uitf.com.ph API

## Use Cases



## Sample Data

```csv
date,original_label,navpu_value,buy,buy_strength,price_change,ma_7,ma_30,rsi,buy_reason,future_return_7d,future_return_30d
2024-01-15,Jan 15 2024,1.2543,1,2,-0.012,1.2534,1.2489,45.3,"RSI Recovery; DCA Signal",0.023,0.087
2024-01-16,Jan 16 2024,1.2587,0,0,0.035,1.2545,1.2491,48.7,"",−0.008,0.042
```

## Data Freshness

The dataset is generated through automated extraction and can be updated by running:
```python
data_ingestion(start="2019-01-01", end="")  # end="" uses current date
```

