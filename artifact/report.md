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
| BRIS.JK  | 2021-10-15 - 2026-10-13 | 1197 | 1057.28  |   1518.65  |        1818.84 |    2474.82 | 3079.46 | 1980.23  |   531.612 |
| MEGA.JK  | 2021-10-15 - 2026-10-13 | 1197 | 1555.18  |   1936.94  |        2262.12 |    2368.16 | 3242.59 | 2145.49  |   328.726 |
| NISP.JK  | 2021-10-15 - 2026-10-13 | 1197 |  471.697 |    590.123 |        1115.65 |    1250    | 1527.91 |  984.727 |   321.304 |


## Evaluation


| Ticker   | Model   |   Time Steps |   Batch Size |   Learning Rate |       MSE |     RMSE |    MAPE |
|:---------|:--------|-------------:|-------------:|----------------:|----------:|---------:|--------:|
| BBCA.JK  | GRU     |           20 |           32 |          0.001  |  25695.8  | 160.299  | 1.76829 |
| BBCA.JK  | LSTM    |           20 |           32 |          0.001  |  36696.4  | 191.563  | 2.0034  |
| BBNI.JK  | GRU     |           20 |           16 |          0.001  |   5644.32 |  75.1287 | 1.46644 |
| BBNI.JK  | LSTM    |           30 |           16 |          0.001  |   5499.02 |  74.1554 | 1.43863 |
| BBRI.JK  | GRU     |           30 |           16 |          0.001  |   4093.4  |  63.9797 | 1.49921 |
| BBRI.JK  | LSTM    |           30 |           32 |          0.001  |   5097.71 |  71.3983 | 1.73537 |
| BBTN.JK  | GRU     |           30 |           16 |          0.001  |   1225.62 |  35.0089 | 2.0791  |
| BBTN.JK  | LSTM    |           20 |           16 |          0.001  |   1325.05 |  36.4013 | 2.03746 |
| BDMN.JK  | GRU     |           30 |           16 |          0.001  |  81509.4  | 285.498  | 4.69049 |
| BDMN.JK  | LSTM    |           30 |           16 |          0.001  | 119332    | 345.445  | 5.50738 |
| BMRI.JK  | GRU     |           30 |           16 |          0.001  |   7284.37 |  85.3485 | 1.54698 |
| BMRI.JK  | LSTM    |           30 |           32 |          0.001  |  13346.1  | 115.525  | 2.12001 |
| BNGA.JK  | GRU     |           30 |           32 |          0.0001 |   1186.21 |  34.4414 | 1.7005  |
| BNGA.JK  | LSTM    |           30 |           32 |          0.001  |   9724.71 |  98.614  | 5.74501 |
| BNLI.JK  | GRU     |           30 |           32 |          0.001  |  24671.1  | 157.07   | 3.24346 |
| BNLI.JK  | LSTM    |           30 |           16 |          0.001  |  36014    | 189.774  | 3.98028 |
| BRIS.JK  | GRU     |           30 |           32 |          0.001  |   3079.26 |  55.4911 | 1.97647 |
| BRIS.JK  | LSTM    |           30 |           16 |          0.001  |   3678.61 |  60.6516 | 2.1627  |
| MEGA.JK  | GRU     |           30 |           32 |          0.001  |   7728.24 |  87.9104 | 1.88998 |
| MEGA.JK  | LSTM    |           20 |           16 |          0.001  |  11826.8  | 108.751  | 2.59696 |
| NISP.JK  | GRU     |           30 |           32 |          0.0001 |   1896.66 |  43.5507 | 2.75316 |
| NISP.JK  | LSTM    |           20 |           32 |          0.0001 |   2869.49 |  53.5676 | 3.43359 |


## Visualisasi Hasil Inferensi


![BBCA.JK (GRU)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/BBCA.JK_GRU_inference.png)




![BBCA.JK (LSTM)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/BBCA.JK_LSTM_inference.png)




![BBNI.JK (GRU)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/BBNI.JK_GRU_inference.png)




![BBNI.JK (LSTM)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/BBNI.JK_LSTM_inference.png)




![BBRI.JK (GRU)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/BBRI.JK_GRU_inference.png)




![BBRI.JK (LSTM)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/BBRI.JK_LSTM_inference.png)




![BDMN.JK (GRU)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/BDMN.JK_GRU_inference.png)




![BDMN.JK (LSTM)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/BDMN.JK_LSTM_inference.png)




![BMRI.JK (GRU)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/BMRI.JK_GRU_inference.png)




![BMRI.JK (LSTM)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/BMRI.JK_LSTM_inference.png)




![BNGA.JK (GRU)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/BNGA.JK_GRU_inference.png)




![BNGA.JK (LSTM)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/BNGA.JK_LSTM_inference.png)




![BNLI.JK (GRU)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/BNLI.JK_GRU_inference.png)




![BNLI.JK (LSTM)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/BNLI.JK_LSTM_inference.png)




![BRIS.JK (GRU)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/BRIS.JK_GRU_inference.png)




![BRIS.JK (LSTM)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/BRIS.JK_LSTM_inference.png)




![MEGA.JK (GRU)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/MEGA.JK_GRU_inference.png)




![MEGA.JK (LSTM)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/MEGA.JK_LSTM_inference.png)




![NISP.JK (GRU)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/NISP.JK_GRU_inference.png)




![NISP.JK (LSTM)](https://storagestockforecast.blob.core.windows.net/plots/20261014_test/NISP.JK_LSTM_inference.png)


