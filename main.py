from market import load_stock_data
from education import FinancialAdvisor
from events import draw_event
import matplotlib.pyplot as plt

# =====================
# 遊戲設定與開場
# =====================
MAX_WEEKS = 156
TARGET = 800000
cash = 500000
stock = 0
avg_price = 0

print("="*50)
print("📈 歡迎來到【華爾街見習生：投資模擬遊戲】 📉")
print("="*50)
print("【遊戲背景】")
print("你是一位剛踏入股市的見習生。我們為你準備了一台時光機，")
print("將帶你回到過去的某一段真實歷史行情中。")
print("\n【你的任務】")
print(f"💰 初始資金：{cash:,}")
print(f"⏳ 遊戲時間：{MAX_WEEKS} 週")
print(f"🏆 目標總資產：{TARGET:,} (達標即可通關！)")
print("\n【操作說明】")
print("- 遊戲每週會推進一次，你必須在「每週五」根據走勢圖做出決策。")
print("- 你可以選擇：買(b)、賣(s)、或空手觀望(n)。")
print("- 每次交易都會扣除真實世界比例的手續費與交易稅。")
print("- 遊戲中有一位「財商導師」會根據你的行為給你評分與建議。")
print("="*50)
input("👉 準備好了嗎？請按下 [Enter] 鍵啟動時光機...")
print("")

# =====================
# 初始化市場資料
# =====================
df = load_stock_data()   # ⚠️ 現在建議是「日資料」

# 💥 終極攤平：直接拔掉 yfinance 產生的雙層 (MultiIndex) 欄位
if hasattr(df.columns, 'levels'):
    df.columns = df.columns.get_level_values(0)

# 🎯 預先推進 30 天，讓第一週就有完整的 30 天歷史走勢
START_OFFSET = 30
initial_close = df["Close"].iloc[START_OFFSET]
prev_price = float(initial_close.iloc[0] if hasattr(initial_close, "iloc") else initial_close)

# 📊 新增：用來記錄玩家交易點的歷史，方便畫在圖表上
trade_days_x = []
trade_prices_y = []
trade_actions_color = []  # 記錄顏色，買(綠) 賣(藍) 不動(紅)

# 🧠 新增：財商導師系統
advisor = FinancialAdvisor()

plt.ion()
plt.figure(figsize=(10, 5))  # 稍微拉寬，看趨勢更清楚

print("🎮 歡迎來到投資模擬遊戲（券商模式）")

# =====================
# 每週（週五交易）
# =====================
for week in range(1, MAX_WEEKS + 1):

    # ====== 防呆 ======
    if week >= len(df):
        print("📉 沒有更多資料，遊戲結束")
        break

    # =====================
    # 用「日資料模擬週五」
    # =====================
    day_index = START_OFFSET + week * 5  # 加上初始的 30 天偏移量

    if day_index >= len(df):
        print("📉 沒有更多交易日")
        break

    # 🎯 防禦機制 2：確保當週週五的價格絕對是純數字
    day_close = df["Close"].iloc[day_index]
    current_price = float(day_close.iloc[0] if hasattr(day_close, "iloc") else day_close)

    # =====================
    # 📊 顯示「市場走勢」（優化：專業看盤軟體風格）
    # =====================
    history_close = df["Close"].iloc[0:day_index + 1]
    history_ma10 = df["Close"].rolling(window=10).mean().iloc[0:day_index + 1]

    plt.clf()
    
    # 1. 股價曲線與漸層陰影
    plt.plot(history_close.index, history_close.values, label="Stock Price", color="#2c3e50", linewidth=2) 
    plt.fill_between(history_close.index, history_close.values, color="#3498db", alpha=0.1)
    
    # 2. 10 日均線 (MA10)
    plt.plot(history_ma10.index, history_ma10.values, label="10-Day MA", color="#e74c3c", linestyle="--", alpha=0.8)

    # 3. 玩家平均成本線
    if stock > 0:
        plt.axhline(y=avg_price, color="#27ae60", linestyle="-.", label="My Avg Cost", zorder=3)

    # 4. 過去交易軌跡
    if trade_days_x:
        for x, y, c in zip(trade_days_x, trade_prices_y, trade_actions_color):
            plt.scatter(x, y, color=c, s=70, zorder=5, edgecolors='white')

    # 5. 當下決策點
    current_day_label = history_close.index[-1]
    plt.scatter(current_day_label, current_price, color="#f1c40f", s=150, edgecolors='black', label="Decision Point", zorder=6)

    # 6. 隱藏式圖例 (用來解釋買/賣/不動的顏色)
    plt.scatter([], [], color="green", label="Buy", s=50)
    plt.scatter([], [], color="blue", label="Sell", s=50)
    plt.scatter([], [], color="red", label="Hold", s=50)

    # 7. 固定 X 與 Y 軸範圍 (改為滾動視窗：固定看前 30 天的走勢)
    view_window = 30
    start_x = max(0, day_index - view_window)
    end_x = max(view_window, day_index + 2) # 右側預留 2 天的空白空間，不要貼齊邊緣
    
    plt.xlim(start_x, end_x)
    
    # 根據當前畫面中的數據來動態調整 Y 軸，讓 K 線放大顯示
    visible_history = df["Close"].iloc[start_x:day_index + 1]
    y_min = visible_history.min() * 0.98  # 縮小 padding 讓走勢波動更明顯
    y_max = visible_history.max() * 1.02
    
    # 如果玩家有持股，確保 Y 軸也能顯示出「平均成本線」，不會跑到畫面外
    if stock > 0:
        y_min = min(y_min, avg_price * 0.98)
        y_max = max(y_max, avg_price * 1.02)
        
    plt.ylim(y_min, y_max)

    # 圖表美化
    plt.title(f"Market View (Week {week} / {MAX_WEEKS})", fontsize=14, fontweight="bold")
    plt.xlabel("Trading Days")
    plt.ylabel("Price")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(loc='upper left', fontsize='small')
    plt.tight_layout()
    plt.pause(0.1)

    # =====================
    # 資產計算
    # =====================
    total_asset = cash + stock * current_price
    unrealized = (current_price - avg_price) * stock if stock > 0 else 0

    # =====================
    # 儀表板
    # =====================
    print("\n📊 === 投資儀表板 ===")
    print(f"週數：{week}")
    print(f"股價：{current_price:.2f}")
    print(f"現金：{cash:.2f}")
    print(f"股票：{stock}")
    print(f"平均成本：{avg_price:.2f}")
    print(f"未實現損益：{unrealized:.2f}")
    print(f"總資產：{total_asset:.2f}")
    print("====================")

    # =====================
    # 玩家操作（只在週五）
    # =====================
    action = input("買(b) / 賣(s) / 不動(n): ")

    # 紀錄本次操作要畫在圖上的顏色
    current_color = "red" 

    # ===== 買 =====
    if action == "b":
        try:
            qty = int(input("買幾股: "))
            if qty <= 0:
                print("❌ 股數必須大於 0")
                continue
        except ValueError:
            print("❌ 請輸入數字")
            continue

        fee = current_price * qty * 0.001425
        total_cost = current_price * qty + fee

        if cash >= total_cost:
            stock_cost = avg_price * stock + current_price * qty
            stock += qty
            avg_price = stock_cost / stock
            cash -= total_cost

            print(f"✅ 買入 {qty} 股")
            print(f"手續費：{fee:.2f}")
            current_color = "green"  # 買入用綠點
        else:
            print("❌ 現金不足")

    # ===== 賣 =====
    elif action == "s":
        try:
            qty = int(input("賣幾股: "))
            if qty <= 0:
                print("❌ 股數必須大於 0")
                continue
        except ValueError:
            print("❌ 請輸入數字")
            continue

        if stock >= qty:
            fee = current_price * qty * 0.001425
            tax = current_price * qty * 0.003

            cash += current_price * qty - fee - tax
            stock -= qty

            if stock == 0:
                avg_price = 0

            print(f"✅ 賣出 {qty} 股")
            print(f"手續費：{fee:.2f}")
            print(f"交易稅：{tax:.2f}")
            current_color = "blue"  # 賣出用藍點
        else:
            print("❌ 股票不足")

    elif action == "n":
        print("本週沒有操作")
        current_color = "red"  # 不動用紅點

    else:
        print("❌ 無效操作")
        current_color = "red"

    # 儲存歷史紀錄，讓下一輪迴圈繪圖時可以畫出來
    trade_days_x.append(current_day_label)
    trade_prices_y.append(current_price)
    trade_actions_color.append(current_color)

    # =====================
    # 教學系統
    # =====================
    # 取出當下的 MA10 作為判斷依據（如果前 10 天資料不足則使用當前股價）
    current_ma10 = history_ma10.iloc[-1] if not history_ma10.isna().iloc[-1] else current_price
    advisor.evaluate(action, current_price, prev_price, avg_price, current_ma10, cash, total_asset, stock)

    # =====================
    # 隨機事件（每4週）
    # =====================
    if week % 4 == 0:
        event = draw_event()
        cash += event["amount"]

        print(f"📌 事件：{event['name']}")

        if event["amount"] > 0:
            print(f"🎉 +{event['amount']}")
        elif event["amount"] < 0:
            print(f"⚠️ {event['amount']}")
        else:
            print("😌 無變動")

    # =====================
    # 結束條件
    # =====================
    total_asset = cash + stock * current_price

    if total_asset < 0:
        print("💥 破產")
        break

    if total_asset >= TARGET:
        print("🏆 達標！")
        break

    prev_price = current_price


# =====================
# 結束
# =====================
final_asset = cash + stock * current_price

print("\n===== 遊戲結束 =====")
print(f"最終資產：{final_asset:.2f}")

if final_asset >= TARGET:
    print("🎉 成功達標")
else:
    print("📉 未達標")
    
# 讓最後的圖表留著，不會瞬間消失
plt.ioff()
plt.show()

# =====================
# 遊戲結束結算畫面 
# =====================
final_asset = cash + stock * current_price
final_fiq = advisor.fiq_score  # 讀取累積的理財積分

print("\n" + "★"*20)
print("🏆 ===== 投資模擬遊戲 最終結算 ===== 🏆")
print(f"💰 最終總資產：{final_asset:.2f} (目標: {TARGET})")
print(f"🧠 你的最終理財積分 (Financial IQ): {final_fiq} 分")

print("\n🎖️ 獲得財商尊號：", end="")
if final_fiq >= 120:
    print("【👑 傲視華爾街的少年股神】")
    print("👉 評語：太厲害了！你擁有極高的克制力，懂得越跌越買、分批停利，完全沒有被市場情緒牽著走，是萬中選一的理性投資人！")
elif final_fiq >= 100:
    print("【⚖️ 穩健前行的理性投資人】")
    print("👉 評語：表現標準！你懂得基本的操作紀律，也能避開極端的風險。只要保持這個節奏，在現實市場中你也能穩健資產翻倍。")
elif final_fiq >= 85:
    print("【🌱 隨波逐流的市場小散戶】")
    print("👉 評語：稍微有點危險喔！你常常看到大漲就忍不住想追，看到大跌就想亂賣，這會讓你在不知不覺中交了好多手續費給券商。")
else:
    print("【🚨 散財童子 / 終極韭菜】")
    print("👉 評語：完全是憑著感覺和情緒在盲目操作！頻繁追高殺低、把子彈一次打光、不給自己留退路。請重新多玩幾次，好好看導師的白話文建議！")

if advisor.achievements:
    print("\n🏅 [ 你的榮耀勳章 (解鎖成就) ]")
    for ach in advisor.achievements:
        print(f"  - {ach}")
        
print("★"*20)
