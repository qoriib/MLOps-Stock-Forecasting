## Dataset Overview

| Ticker   |   Jumlah Data | Date Range               |   Latest Close |
|:---------|--------------:|:-------------------------|---------------:|
| BBCA.JK  |          1203 | 2021-09-27 to 2026-09-25 |           6250 |
| BBRI.JK  |          1204 | 2021-09-27 to 2026-09-25 |           3150 |


## Champion Models

| Ticker   | Model   |   Time Steps | Optimizer   |   Batch Size |   Learning Rate |   RMSE |   MAPE |
|:---------|:--------|-------------:|:------------|-------------:|----------------:|-------:|-------:|
| BBCA.JK  | GRU     |           10 | Adam        |            8 |            0.01 | 145.82 |   1.73 |
| BBRI.JK  | GRU     |           30 | RMSprop     |           16 |            0.01 |  65.35 |   1.66 |

