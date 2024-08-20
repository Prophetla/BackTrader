import datetime
import pandas as pd
import backtrader as bt


def load_data():
    # 读取数据
    file_path = '/Users/prophetl/PycharmProjects/BackTrader/F-BTCUSDT-1m-202001-202407.csv'
    dataframe = pd.read_csv(file_path, index_col=False)

    dataframe['open_time'] = pd.to_datetime(dataframe['open_time'])
    dataframe.sort_values(by='open_time', inplace=True)
    dataframe.set_index('open_time', inplace=True)

    # 加载数据到Backtrader中
    start_date = datetime.datetime(2020, 1, 1, 1, 0, 0)
    end_date = datetime.datetime(2020, 1, 1, 2, 0, 0)

    data = bt.feeds.PandasData(dataname=dataframe, fromdate=start_date, todate=end_date)
    return data
