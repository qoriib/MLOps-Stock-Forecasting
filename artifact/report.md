# Pipeline Report

## Dataset Overview

| Ticker   | Period                   |   Rows |   Gaps | Price (Mean ± Std)   | Price Range        |
|:---------|:-------------------------|-------:|-------:|:---------------------|:-------------------|
| BBCA.JK  | 2021-10-04 to 2026-10-02 |   1203 |    622 | 7671.62 ± 1028.69    | 4831.27 - 10021.74 |

## Model Evaluation

| Ticker   | Model   |   Time Steps |   Batch Size | Optimizer   |   Learning Rate |   RMSE | MAPE   | Status    |
|:---------|:--------|-------------:|-------------:|:------------|----------------:|-------:|:-------|:----------|
| BBCA.JK  | GRU     |           10 |            8 | Adam        |            0.01 | 148.77 | 1.85%  | Champion  |
| BBCA.JK  | LSTM    |           10 |            8 | Adam        |            0.01 | 156.92 | 1.93%  | Candidate |
