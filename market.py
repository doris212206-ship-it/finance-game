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

    # 從 2008 到 2023 年之間隨機挑選一天作為起點
    start_year = random.randint(2008, 2023)
    start_month = random.randint(1, 12)
    start_day = random.randint(1, 28) # 避免大小月報錯
    
    start_date = datetime(start_year, start_month, start_day)
    # 抓取 4 年的資料，確保 156 週（3 年）有足夠的交易日
    end_date = start_date + timedelta(days=1460)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    print("⏳ 正在搭乘時光機，前往隨機的歷史市場區間...")

    try:
        df = yf.download(
            ticker,
            start=start_str,
            end=end_str,
            interval="1d",
            auto_adjust=False,
            progress=False, # 隱藏下載進度條，增加神秘感
            threads=False
        )
    except Exception as exc:
        raise RuntimeError("無法下載股票資料，請確認網路連線後再重新整理頁面。") from exc

    if df.empty:
        raise RuntimeError("這次沒有抓到股票資料，請重新整理頁面再試一次。")

    # 將隨機區間記錄在 df.attrs 中，方便後續在結算畫面揭曉
    df.attrs['history_start'] = start_str
    df.attrs['history_end'] = end_str
    df.attrs['ticker'] = ticker
    
    # 抓取公司基本資訊（名稱、產業）
    try:
        info = yf.Ticker(ticker).info
        df.attrs['company_name'] = info.get('longName', ticker)
        df.attrs['sector'] = info.get('sector', '未知產業')
        df.attrs['industry'] = info.get('industry', '未知細分產業')
    except Exception:
        df.attrs['company_name'] = ticker
        df.attrs['sector'] = '未知'
        df.attrs['industry'] = '未知'

    # ===== 防呆處理 =====
    df = df.dropna()
    df = df.reset_index()

    # 只保留需要的欄位
    if 'Date' not in df.columns:
        df = df.reset_index()
    df = df[["Date", "Close"]]

    return df
