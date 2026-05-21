import random

# =========================
# 歷史新聞資料
# =========================
historical_news = [
    {"date": "2008-07-10", "text": "伊朗試射九枚飛彈，宣稱已準備進一步軍事行動"},
    {"date": "2008-09-09", "text": "市場憂心雷曼兄弟財務危機，道瓊暴跌近300點"},
    {"date": "2011-02-22", "text": "利比亞局勢動盪衝擊市場，國際油價大漲"},
    {"date": "2014-11-13", "text": "布蘭特原油跌破80美元，創四年新低，市場關注OPEC動向"},
    {"date": "2018-03-23", "text": "美中貿易戰開打！川普下令對中國課徵1.76兆關稅"},
    {"date": "2020-01-05", "text": "WHO:中國出現不明原因肺炎病例"},
    {"date": "2020-03-06", "text": "OPEC與俄羅斯減產談判破裂，國際油價重挫"},
    {"date": "2022-02-24", "text": "烏克蘭稱俄軍自俄羅斯、白俄與克里米亞全面進攻"},
    {"date": "2024-05-07", "text": "中國產能過剩衝擊全球化工產業"},
    {"date": "2025-08-20", "text": "中國將整頓石化產業，以化解產能過剩問題"}
]

# =========================
# 隨機事件資料
# =========================

events = [

    # ===== 好事件 =====
    {
        "name": "幸運的孩子！上次路過彩卷行買的樂透竟然中了大獎!!!",
        "amount": 1000000,
        "probability": 0.1
    },

    {
        "name": "老闆今天心情很好，公司發獎金",
        "amount": 10000,
        "probability": 5
    },

    {
        "name": "你上週加班爆肝，消耗了身體但加班費入帳了",
        "amount": 4000,
        "probability": 8
    },

    {
        "name": "生活中的小確幸，發票中了小獎~",
        "amount": 200,
        "probability": 10
    },

    {
        "name": "上次買手搖杯的發票竟然中了四獎",
        "amount": 4000,
        "probability": 2
    },

    {
        "name": "你撿到的錢交至警局後公告期滿，現在正式歸你了",
        "amount": 2000,
        "probability": 2
    },

    {
        "name": "政府補助通過，錢默默匯進帳戶",
        "amount": 5000,
        "probability": 4
    },

    {
        "name": "好久不見的親友突然塞紅包給你，今天人緣不錯",
        "amount": 2000,
        "probability": 5
    },

    {
        "name": "你整理房間，二手物品竟然賣出好價錢",
        "amount": 3000,
        "probability": 4
    },

    {
        "name": "臨時接到一個案子，辛苦但值得",
        "amount": 9000,
        "probability": 3
    },

    {
        "name": "保險理賠核准，終於等到這筆錢",
        "amount": 10000,
        "probability": 2
    },

    {
        "name": "報銷成功！之前墊的錢回來了",
        "amount": 3000,
        "probability": 4
    },

    # ===== 壞事件 =====
    {
        "name": "身體發出警訊，你去看醫生了",
        "amount": -3000,
        "probability": 6
    },

    {
        "name": "手機壽終正寢，你只好換一支新的",
        "amount": -18000,
        "probability": 2
    },

    {
        "name": "手一滑！手機螢幕直接裂成蜘蛛網，需要換新的了...",
        "amount": -2500,
        "probability": 3
    },

    {
        "name": "家電突然罷工，維修師傅來收錢了",
        "amount": -5000,
        "probability": 4
    },

    {
        "name": "天花板開始滴水，房屋漏水要處理",
        "amount": -15000,
        "probability": 1
    },

    {
        "name": "朋友結婚啦！當然要包個紅包",
        "amount": -3600,
        "probability": 5
    },

    {
        "name": "公司突然通知裁員，你的收入暫時中斷",
        "amount": -50000,
        "probability": 1
    },

    {
        "name": "忍不住訂了機票，出國放鬆一下",
        "amount": -25000,
        "probability": 2
    },

    {
        "name": "牙齒抗議了，自費治療跑不掉",
        "amount": -5000,
        "probability": 3
    },

    {
        "name": "一張罰單從天而降，你違規了",
        "amount": -1800,
        "probability": 4
    },

    {
        "name": "車子騎起來怪怪的，保養費來了",
        "amount": -4000,
        "probability": 4
    },

    {
        "name": "水電瓦斯加訂閱費，帳單默默變厚",
        "amount": -1500,
        "probability": 6
    },

    {
        "name": "家裡突然有急用，只好先掏錢處理",
        "amount": -4000,
        "probability": 2
    },

    {
        "name": "搬家雜費一項接一項，錢包大失血",
        "amount": -15000,
        "probability": 1
    },

    {
        "name": "家人臨時需要幫忙，你先借了一筆錢",
        "amount": -6000,
        "probability": 2
    },

    # ===== 沒事發生 =====
    {
        "name": "這週風平浪靜，什麼事都沒發生",
        "amount": 0,
        "probability": 30
    }
]


# =========================
# 抽事件
# =========================

def draw_event():

    weights = [event["probability"] for event in events]

    selected_event = random.choices(
        events,
        weights=weights,
        k=1
    )[0]

    return selected_event