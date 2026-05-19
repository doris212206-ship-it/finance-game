import yfinance as yf
import pandas as pd
import random
from datetime import datetime, timedelta

def load_stock_data():
    """
    下載 6505（台塑化）隨機歷史日線資料
    回傳 DataFrame（含 Close）
    """

    ticker = "6505.TW"

    # 從 2015 到 2023 年之間隨機挑選一天作為起點
    start_year = random.randint(2015, 2023)
    start_month = random.randint(1, 12)
    start_day = random.randint(1, 28) # 避免大小月報錯
    
    start_date = datetime(start_year, start_month, start_day)
    # 抓取 1 年的資料，確保有足夠的交易日供遊戲使用
    end_date = start_date + timedelta(days=365)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    print("⏳ 正在搭乘時光機，前往隨機的歷史市場區間...")

    df = yf.download(
        ticker,
        start=start_str,
        end=end_str,
        interval="1d",
        progress=False # 隱藏下載進度條，增加神秘感
    )

    # 將隨機區間記錄在 df.attrs 中，方便後續在結算畫面揭曉
    df.attrs['history_start'] = start_str
    df.attrs['history_end'] = end_str
    df.attrs['ticker'] = ticker

    # ===== 防呆處理 =====
    df = df.dropna()
    df = df.reset_index()

    # 只保留需要的欄位
    df = df[["Date", "Close"]]

    return df