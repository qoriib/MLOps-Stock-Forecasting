# Pipeline Report

## Data Profile


| Ticker   | Periode                 |    N |      Min |   Q1 (25%) |   Median (50%) |   Q3 (75%) |     Max |     Mean |   Std Dev |
|:---------|:------------------------|-----:|---------:|-----------:|---------------:|-----------:|--------:|---------:|----------:|
| BBCA.JK  | 2021-10-15 - 2026-10-13 | 1197 | 4815.88  |   6743.97  |        7753.25 |    8337.96 | 9989.8  | 7655.58  |  1021.13  |
| BBNI.JK  | 2021-10-15 - 2026-10-13 | 1197 | 2513.78  |   3477.96  |        3730    |    4058.99 | 5026.2  | 3744.53  |   512.992 |
| BBRI.JK  | 2021-10-15 - 2026-10-13 | 1197 | 2590     |   3251.13  |        3512.19 |    3958.12 | 5216.77 | 3619.39  |   502.151 |
| BBTN.JK  | 2021-10-11 - 2026-10-09 | 1199 |  724.671 |   1142.48  |        1195.06 |    1280    | 1505.81 | 1200.51  |   117.518 |
| BDMN.JK  | 2021-10-15 - 2026-10-13 | 1197 | 1841.03  |   2239.96  |        2349.28 |    2464.8  | 4980    | 2493.59  |   621.525 |
| BMRI.JK  | 2021-10-15 - 2026-10-13 | 1197 | 2392.66  |   3653.58  |        4160    |    4592.2  | 6002.09 | 4110.47  |   854.646 |
| BNGA.JK  | 2021-10-15 - 2026-10-13 | 1197 |  622.97  |    845.901 |        1409.3  |    1576.57 | 1765    | 1273.07  |   367.497 |
| BNLI.JK  | 2021-10-15 - 2026-10-13 | 1197 |  849.382 |    917.723 |        1142.2  |    2304.07 | 5913.31 | 1773.9   |  1229.03  |
| BRIS.JK  | 2021-10-15 - 2026-10-13 | 1197 | 1057.29  |   1518.65  |        1818.84 |    2474.82 | 3079.46 | 1980.23  |   531.612 |
| MEGA.JK  | 2021-10-15 - 2026-10-13 | 1197 | 1555.18  |   1936.94  |        2262.12 |    2368.16 | 3242.59 | 2145.49  |   328.726 |
| NISP.JK  | 2021-10-15 - 2026-10-13 | 1197 |  471.696 |    590.123 |        1115.65 |    1250    | 1527.91 |  984.727 |   321.304 |


## Evaluation


| Ticker   | Model   |   Time Steps |   Batch Size |   Learning Rate |       MSE |     RMSE |     MAPE |
|:---------|:--------|-------------:|-------------:|----------------:|----------:|---------:|---------:|
| BBCA.JK  | GRU     |           20 |           16 |          0.0001 |  40742    | 201.846  |  2.12701 |
| BBCA.JK  | LSTM    |           20 |           16 |          0.0001 |  65566.7  | 256.06   |  2.79068 |
| BBNI.JK  | GRU     |           20 |           16 |          0.0001 |  11955.5  | 109.341  |  2.17033 |
| BBNI.JK  | LSTM    |           20 |           16 |          0.0001 |  17883    | 133.727  |  2.68046 |
| BBRI.JK  | GRU     |           20 |           32 |          0.0001 |   6571.14 |  81.0626 |  1.96159 |
| BBRI.JK  | LSTM    |           20 |           16 |          0.0001 |   9219.8  |  96.0198 |  2.36536 |
| BBTN.JK  | GRU     |           30 |           16 |          0.001  |   1225.62 |  35.0089 |  2.0791  |
| BBTN.JK  | LSTM    |           20 |           16 |          0.001  |   1325.05 |  36.4013 |  2.03746 |
| BDMN.JK  | GRU     |           20 |           32 |          0.0001 | 115722    | 340.179  |  5.87566 |
| BDMN.JK  | LSTM    |           20 |           16 |          0.0001 | 438160    | 661.936  | 11.6418  |
| BMRI.JK  | GRU     |           20 |           16 |          0.0001 |  17798.5  | 133.411  |  2.55242 |
| BMRI.JK  | LSTM    |           20 |           16 |          0.0001 |  22451.8  | 149.839  |  2.8121  |
| BNGA.JK  | GRU     |           20 |           32 |          0.0001 |   3934.23 |  62.7235 |  3.48486 |
| BNGA.JK  | LSTM    |           20 |           32 |          0.0001 |   9729.24 |  98.6369 |  5.60536 |
| BNLI.JK  | GRU     |           20 |           32 |          0.0001 |  36064.7  | 189.907  |  3.97326 |
| BNLI.JK  | LSTM    |           20 |           16 |          0.0001 | 196317    | 443.077  | 10.512   |
| BRIS.JK  | GRU     |           20 |           16 |          0.0001 |   3817.87 |  61.7889 |  2.32259 |
| BRIS.JK  | LSTM    |           20 |           16 |          0.0001 |   6379.72 |  79.8732 |  3.09678 |
| MEGA.JK  | GRU     |           20 |           16 |          0.0001 |  10680.2  | 103.345  |  2.14338 |
| MEGA.JK  | LSTM    |           20 |           16 |          0.0001 |  17976.3  | 134.076  |  2.93078 |
| NISP.JK  | GRU     |           20 |           32 |          0.0001 |   4755.93 |  68.9632 |  4.76513 |
| NISP.JK  | LSTM    |           20 |           32 |          0.0001 |   4643.85 |  68.1458 |  4.37381 |


## Visualisasi Hasil Inferensi


### BBCA.JK (GRU)

![BBCA.JK (GRU)](plots/BBCA.JK_GRU_inference.png)




### BBCA.JK (LSTM)

![BBCA.JK (LSTM)](plots/BBCA.JK_LSTM_inference.png)




### BBNI.JK (GRU)

![BBNI.JK (GRU)](plots/BBNI.JK_GRU_inference.png)




### BBNI.JK (LSTM)

![BBNI.JK (LSTM)](plots/BBNI.JK_LSTM_inference.png)




### BBRI.JK (GRU)

![BBRI.JK (GRU)](plots/BBRI.JK_GRU_inference.png)




### BBRI.JK (LSTM)

![BBRI.JK (LSTM)](plots/BBRI.JK_LSTM_inference.png)




### BDMN.JK (GRU)

![BDMN.JK (GRU)](plots/BDMN.JK_GRU_inference.png)




### BDMN.JK (LSTM)

![BDMN.JK (LSTM)](plots/BDMN.JK_LSTM_inference.png)




### BMRI.JK (GRU)

![BMRI.JK (GRU)](plots/BMRI.JK_GRU_inference.png)




### BMRI.JK (LSTM)

![BMRI.JK (LSTM)](plots/BMRI.JK_LSTM_inference.png)




### BNGA.JK (GRU)

![BNGA.JK (GRU)](plots/BNGA.JK_GRU_inference.png)




### BNGA.JK (LSTM)

![BNGA.JK (LSTM)](plots/BNGA.JK_LSTM_inference.png)




### BNLI.JK (GRU)

![BNLI.JK (GRU)](plots/BNLI.JK_GRU_inference.png)




### BNLI.JK (LSTM)

![BNLI.JK (LSTM)](plots/BNLI.JK_LSTM_inference.png)




### BRIS.JK (GRU)

![BRIS.JK (GRU)](plots/BRIS.JK_GRU_inference.png)




### BRIS.JK (LSTM)

![BRIS.JK (LSTM)](plots/BRIS.JK_LSTM_inference.png)




### MEGA.JK (GRU)

![MEGA.JK (GRU)](plots/MEGA.JK_GRU_inference.png)




### MEGA.JK (LSTM)

![MEGA.JK (LSTM)](plots/MEGA.JK_LSTM_inference.png)




### NISP.JK (GRU)

![NISP.JK (GRU)](plots/NISP.JK_GRU_inference.png)




### NISP.JK (LSTM)

![NISP.JK (LSTM)](plots/NISP.JK_LSTM_inference.png)


