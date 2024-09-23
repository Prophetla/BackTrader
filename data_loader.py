import datetime
import pandas as pd
import backtrader as bt


def configure_data(cerebro, kline_file_path, start_date, end_date, timeframe=bt.TimeFrame.Minutes, compression=5):
    """
    优化后的数据加载和重新采样函数，支持CSV文件输入，并通过时间范围过滤数据。
    """
    # 使用分块读取，避免大文件内存问题
    chunk_list = []
    for chunk in pd.read_csv(kline_file_path, chunksize=10000,
                             usecols=['open_time', 'open', 'high', 'low', 'close', 'volume']):
        # 转换时间并过滤所需的时间段
        chunk['open_time'] = pd.to_datetime(chunk['open_time'])
        chunk_filtered = chunk[(chunk['open_time'] >= start_date) & (chunk['open_time'] <= end_date)]
        chunk_list.append(chunk_filtered)

    # 合并所有分块数据
    if chunk_list:
        kline_dataframe = pd.concat(chunk_list)
    else:
        raise ValueError("No data loaded. Please check the file path and date range.")

    # 重命名列以符合Backtrader要求
    kline_dataframe.rename(columns={
        'open_time': 'datetime',
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'volume': 'volume'
    }, inplace=True)

    # 设置索引为时间，并确保索引正确性
    kline_dataframe.set_index('datetime', inplace=True)
    kline_dataframe.sort_index(inplace=True)

    # 检查数据中是否有空值
    if kline_dataframe.isnull().values.any():
        raise ValueError("Data contains NaN values. Please clean your data.")

    # 将数据加载到Backtrader
    kline_data = bt.feeds.PandasData(
        dataname=kline_dataframe,
        timeframe=bt.TimeFrame.Minutes,
        compression=1,
    )
    # 添加1分钟数据到cerebro
    # cerebro.adddata(kline_data, name='1M')

    cerebro.resampledata(kline_data, timeframe=bt.TimeFrame.Minutes, compression=5, name='5M')

    # cerebro.resampledata(kline_data, timeframe=bt.TimeFrame.Minutes, compression=60, name='1H')





