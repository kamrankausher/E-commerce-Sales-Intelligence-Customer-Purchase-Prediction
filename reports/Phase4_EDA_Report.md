# Phase 4: Exploratory Data Analysis & Business Insights

## 1. Automated Business Insights from SQL Analytics

### Top Categories Revenue
**Observation:** The 'health_beauty' category generates the highest revenue at R$ 298,933.11.
**Business Impact:** Revenue is heavily concentrated in this category, representing a strong market fit but also a vulnerability if demand shifts.
**Recommendation:** Capitalize on 'health_beauty' with premium cross-selling, while simultaneously diversifying marketing efforts to underperforming categories.

### Monthly Revenue
**Observation:** Revenue peaked during 2025-12.
**Business Impact:** Seasonality plays a significant role in customer purchasing behavior, likely tied to promotional events like Black Friday or holidays.
**Recommendation:** Allocate higher marketing budgets 30 days prior to the peak month to maximize customer acquisition during high-intent periods.

### Average Order Value
**Observation:** The Average Order Value (AOV) across all delivered orders is R$ 154.07.
**Business Impact:** AOV indicates the baseline profitability per transaction before operational costs.
**Recommendation:** Introduce free-shipping thresholds at R$ 185 to incentivize customers to add more items to their cart.

## 2. SQL Query Results

### average_order_value.sql
| total_orders | total_revenue | average_order_value |
|---|---|---|
| 24820.0 | 3824001.3799999906 | 154.06935455277963 |


### monthly_revenue.sql
| month | total_revenue | total_orders |
|---|---|---|
| 2024-01 | 102480.04999999999 | 663 |
| 2024-02 | 129291.51999999995 | 824 |
| 2024-03 | 134122.6399999999 | 847 |
| 2024-04 | 120331.52000000009 | 791 |
| 2024-05 | 155085.59999999998 | 1002 |
| 2024-06 | 140268.57999999987 | 956 |
| 2024-07 | 132162.83000000002 | 831 |
| 2024-08 | 141006.06000000008 | 872 |
| 2024-09 | 133783.67999999988 | 886 |
| 2024-10 | 127646.70000000007 | 816 |


### revenue_by_state.sql
| state | unique_customers | total_revenue |
|---|---|---|
| SP | 3111 | 1298794.7500000012 |
| RJ | 1318 | 544199.5299999998 |
| MG | 1077 | 451426.88000000024 |
| BA | 499 | 217482.99999999997 |
| RS | 460 | 177351.18999999974 |
| PR | 386 | 169757.8100000002 |
| CE | 287 | 124134.90000000002 |
| PE | 280 | 112300.13999999997 |
| SC | 231 | 100027.12000000001 |
| PA | 218 | 93793.52000000005 |


### top_categories_revenue.sql
| category | items_sold | total_revenue |
|---|---|---|
| health_beauty | 3695 | 298933.1100000004 |
| sports_leisure | 3496 | 280898.41999999975 |
| computers_accessories | 2759 | 219761.14999999962 |
| bed_bath_table | 2335 | 192136.48999999967 |
| furniture_decor | 2266 | 189173.57999999964 |
| housewares | 2125 | 180231.7600000001 |
| telephony | 1922 | 163111.43999999986 |
| auto | 1648 | 139075.03999999978 |
| watches_gifts | 1596 | 134260.05999999988 |
| garden_tools | 1396 | 116151.17999999992 |


### top_customers.sql
| customer_unique_id | total_orders | total_spend |
|---|---|---|
| cust_001195 | 4 | 3123.64 |
| cust_007802 | 10 | 3077.8499999999995 |
| cust_004479 | 8 | 2935.22 |
| cust_000796 | 3 | 2625.36 |
| cust_007482 | 8 | 2499.74 |
| cust_007129 | 6 | 2475.6 |
| cust_004315 | 10 | 2474.6000000000004 |
| cust_007759 | 7 | 2401.77 |
| cust_000137 | 8 | 2386.73 |
| cust_000988 | 5 | 2369.65 |


## 3. Visualization Artifacts

Static visualizations have been saved to `reports/images/`.
