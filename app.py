import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from market import load_stock_data
from education import FinancialAdvisor
from events import draw_event

# 頁面設定
st.set_page_config(page_title="華爾街見習生", page_icon="📈", layout="wide")

# 初始化 Session State
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    
    with st.spinner('正在搭乘時光機，下載歷史行情...'):
        st.session_state.df = load_stock_data()
        
    if hasattr(st.session_state.df.columns, 'levels'):
        st.session_state.df.columns = st.session_state.df.columns.get_level_values(0)
        
    st.session_state.MAX_WEEKS = 20
    st.session_state.TARGET = 150000
    st.session_state.START_OFFSET = 30
    st.session_state.week = 1
    
    st.session_state.cash = 100000
    st.session_state.stock = 0
    st.session_state.avg_price = 0
    
    initial_close = st.session_state.df["Close"].iloc[st.session_state.START_OFFSET]
    st.session_state.prev_price = float(initial_close.iloc[0] if hasattr(initial_close, "iloc") else initial_close)
    
    st.session_state.trade_days_x = []
    st.session_state.trade_prices_y = []
    st.session_state.trade_actions_color = []
    
    st.session_state.advisor = FinancialAdvisor()
    st.session_state.logs = ["🎮 歡迎來到【華爾街見習生】網頁版！", "準備好開始你的投資之旅了嗎？請在左方進行操作！"]
    st.session_state.game_over = False

# =====================
# 側邊欄：投資儀表板
# =====================
with st.sidebar:
    st.header("📊 投資儀表板")
    
    # 準備資料
    df = st.session_state.df
    week = st.session_state.week
    
    # 確保結算時圖表停留在最後一天
    display_week = min(week, st.session_state.MAX_WEEKS)
    day_index = st.session_state.START_OFFSET + display_week * 5
    day_index = min(day_index, len(df) - 1)
    
    if (st.session_state.START_OFFSET + week * 5) >= len(df) or week > st.session_state.MAX_WEEKS:
        st.session_state.game_over = True
        
    day_close = df["Close"].iloc[day_index]
    current_price = float(day_close.iloc[0] if hasattr(day_close, "iloc") else day_close)
        
    total_asset = st.session_state.cash + st.session_state.stock * current_price
    unrealized = (current_price - st.session_state.avg_price) * st.session_state.stock if st.session_state.stock > 0 else 0
    
    st.metric("週數", f"{display_week} / {st.session_state.MAX_WEEKS}")
    st.metric("當前股價", f"${current_price:.2f}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    col1.metric("現金 (Cash)", f"${st.session_state.cash:,.0f}")
    col2.metric("持股 (Stock)", f"{st.session_state.stock} 股")
    
    st.metric("平均成本", f"${st.session_state.avg_price:.2f}")
    st.metric("未實現損益", f"${unrealized:,.0f}", delta=float(unrealized))
    
    st.divider()
    
    st.metric("總資產 (Total Asset)", f"${total_asset:,.0f}", delta=float(total_asset - 100000))
    st.metric("通關目標", f"${st.session_state.TARGET:,.0f}")
    st.metric("新手理財積分 (FIQ)", f"{st.session_state.advisor.fiq_score} 分")

# =====================
# 遊戲主畫面
# =====================
st.title("📈 華爾街見習生：投資模擬遊戲")

with st.expander("📖 遊戲規則與背景 (點擊展開/收起)", expanded=(st.session_state.week == 1)):
    ticker_name = df.attrs.get('ticker', '神秘股票')
    st.markdown(f"""
    **【遊戲背景】**
    你是一位剛踏入股市的見習生。我們為你準備了一台時光機，將帶你回到過去的某一段真實歷史行情中。
    🎯 **本局操盤標的：{ticker_name}**

    **【你的任務】**
    - 💰 **初始資金**：$100,000
    - ⏳ **遊戲時間**：20 週
    - 🏆 **目標總資產**：$150,000 (達標即可通關！)

    **【操作說明】**
    - 遊戲每週會推進一次，你必須在「每週五」根據走勢圖做出決策。
    - 你可以選擇：買入、賣出、或空手觀望。每次交易都會扣除真實世界比例的手續費與交易稅。
    - 遊戲中有一位「財商導師」會根據你的行為給你評分與建議。

    **【📊 圖表怎麼看？新手必讀】**
    - 🔵 **深藍實線 (Stock Price)**：公司每一天的「真實股價走勢」。
    - 🔴 **紅色虛線 (10-Day MA)**：這是「10日移動平均線」，代表市場過去 10 天的平均買進成本。股價在紅線上方代表近期趨勢向上；在下方代表趨勢向下。
    - 🟢 **綠色點虛線 (My Avg Cost)**：這是「你自己的平均買進成本」。只要深藍實線高於這條線，你帳面上就是賺錢的！
    - 🟡 **黃色大圓點 (Decision Point)**：這是「現在」的時間點，你只能看到過去的歷史，未來是未知的。
    """)

# =====================
# 雙欄式排版設計
# =====================
main_col_left, main_col_right = st.columns([2, 1], gap="large")

with main_col_left:
    # =====================
    # 畫圖 (永遠顯示)
    # =====================
    history_close = df["Close"].iloc[0:day_index + 1]
    history_ma10 = df["Close"].rolling(window=10).mean().iloc[0:day_index + 1]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(history_close.index, history_close.values, label="Stock Price", color="#2c3e50", linewidth=2) 
    ax.fill_between(history_close.index, history_close.values, color="#3498db", alpha=0.1)
    ax.plot(history_ma10.index, history_ma10.values, label="10-Day MA", color="#e74c3c", linestyle="--", alpha=0.8)
    
    if st.session_state.stock > 0:
        ax.axhline(y=st.session_state.avg_price, color="#27ae60", linestyle="-.", label="My Avg Cost", zorder=3)
        
    if st.session_state.trade_days_x:
        ax.scatter(st.session_state.trade_days_x, st.session_state.trade_prices_y, c=st.session_state.trade_actions_color, s=70, zorder=5, edgecolors='white')
        
    current_day_label = history_close.index[-1]
    ax.scatter(current_day_label, current_price, color="#f1c40f", s=150, edgecolors='black', label="Decision Point", zorder=6)
    
    ax.scatter([], [], color="green", label="Buy", s=50)
    ax.scatter([], [], color="blue", label="Sell", s=50)
    ax.scatter([], [], color="red", label="Hold", s=50)
    
    view_window = 30
    start_x = max(0, day_index - view_window)
    end_x = max(view_window, day_index + 2)
    ax.set_xlim(start_x, end_x)
    
    visible_history = df["Close"].iloc[start_x:day_index + 1]
    y_min = visible_history.min() * 0.98
    y_max = visible_history.max() * 1.02
    
    if st.session_state.stock > 0:
        y_min = min(y_min, st.session_state.avg_price * 0.98)
        y_max = max(y_max, st.session_state.avg_price * 1.02)
        
    ax.set_ylim(y_min, y_max)
    ax.set_title(f"Market View (Week {display_week} / {st.session_state.MAX_WEEKS})", fontsize=14, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc='upper left', fontsize='small')
    
    st.pyplot(fig)
    
    # =====================
    # 操作區與結算區
    # =====================
    if st.session_state.game_over:
        st.success("🎉 遊戲結束！")
        st.subheader(f"💰 最終總資產：${total_asset:,.2f} (目標: ${st.session_state.TARGET:,.0f})")
        st.subheader(f"🧠 你的最終理財積分 (FIQ)：{st.session_state.advisor.fiq_score} 分")
        
        final_fiq = st.session_state.advisor.fiq_score
        if final_fiq >= 120:
            st.info("🎖️ **獲得財商尊號：【👑 傲視華爾街的少年股神】**  \n👉 評語：太厲害了！你擁有極高的克制力，懂得越跌越買、分批停利，完全沒有被市場情緒牽著走，是萬中選一的理性投資人！")
        elif final_fiq >= 100:
            st.info("🎖️ **獲得財商尊號：【⚖️ 穩健前行的理性投資人】**  \n👉 評語：表現標準！你懂得基本的操作紀律，也能避開極端的風險。只要保持這個節奏，在現實市場中你也能穩健資產翻倍。")
        elif final_fiq >= 85:
            st.warning("🎖️ **獲得財商尊號：【🌱 隨波逐流的市場小散戶】**  \n👉 評語：稍微有點危險喔！你常常看到大漲就忍不住想追，看到大跌就想亂賣，這會讓你在不知不覺中交了好多手續費給券商。")
        else:
            st.error("🎖️ **獲得財商尊號：【🚨 散財童子 / 終極韭菜】**  \n👉 評語：完全是憑著感覺和情緒在盲目操作！頻繁追高殺低、把子彈一次打光、不給自己留退路。請重新多玩幾次，好好看導師的白話文建議！")
        
        if total_asset >= st.session_state.TARGET:
            st.balloons()
            st.success("🏆 恭喜你達成目標金額，成功通關！")
        else:
            st.error("📉 很可惜，你沒有達到目標金額。")
            
        if st.session_state.advisor.achievements:
            st.warning("🏅 [ 你的榮耀勳章 (解鎖成就) ]")
            for ach in st.session_state.advisor.achievements:
                st.markdown(f"**- {ach}**")
                
        st.divider()
        if st.button("🔄 重新開始遊戲", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    else:
        st.markdown("### ⚡ 你的決策 (請選擇)")
        st.caption("ℹ️ 提示：買入時將收取 0.1425% 手續費；賣出時將收取 0.1425% 手續費與 0.3% 交易稅。")
        
        # 操作區 Callback
        def handle_action(action_type):
            action = action_type
            qty = st.session_state.get(f"{action}_qty", 0) if action in ["b", "s"] else 0
            current_color = "red"
            action_log = []
            
            if action == "b":
                if qty <= 0:
                    st.session_state.logs = ["❌ 買入失敗：股數必須大於 0"]
                    return
                fee = current_price * qty * 0.001425
                total_cost = current_price * qty + fee
                if st.session_state.cash >= total_cost:
                    stock_cost = st.session_state.avg_price * st.session_state.stock + current_price * qty
                    st.session_state.stock += qty
                    st.session_state.avg_price = stock_cost / st.session_state.stock
                    st.session_state.cash -= total_cost
                    action_log.append(f"✅ 成功買入 {qty} 股 (手續費：${fee:.2f})")
                    current_color = "green"
                else:
                    st.session_state.logs = ["❌ 買入失敗：現金不足"]
                    return
                    
            elif action == "s":
                if qty <= 0:
                    st.session_state.logs = ["❌ 賣出失敗：股數必須大於 0"]
                    return
                if st.session_state.stock >= qty:
                    fee = current_price * qty * 0.001425
                    tax = current_price * qty * 0.003
                    st.session_state.cash += current_price * qty - fee - tax
                    st.session_state.stock -= qty
                    if st.session_state.stock == 0:
                        st.session_state.avg_price = 0
                    action_log.append(f"✅ 成功賣出 {qty} 股 (手續費：${fee:.2f} / 交易稅：${tax:.2f})")
                    current_color = "blue"
                else:
                    st.session_state.logs = ["❌ 賣出失敗：股票不足"]
                    return
                    
            elif action == "n":
                action_log.append("⏳ 本週沒有操作，抱緊處理。")
                current_color = "red"
                
            # 紀錄歷史
            st.session_state.trade_days_x.append(current_day_label)
            st.session_state.trade_prices_y.append(current_price)
            st.session_state.trade_actions_color.append(current_color)
            
            # 呼叫導師系統
            current_ma10 = history_ma10.iloc[-1] if not pd.isna(history_ma10.iloc[-1]) else current_price
            advisor_logs = st.session_state.advisor.evaluate(
                action, current_price, st.session_state.prev_price, 
                st.session_state.avg_price, current_ma10, 
                st.session_state.cash, total_asset, st.session_state.stock, ui_mode=True
            )
            
            # 處理隨機事件 (每週一次)
            event_logs = []
            event = draw_event()
            st.session_state.cash += event["amount"]
            if event["amount"] != 0:
                event_logs.append(f"📌 【隨機事件】：{event['name']}")
                if event["amount"] > 0:
                    event_logs.append(f"🎉 獲得 ${event['amount']}")
                elif event["amount"] < 0:
                    event_logs.append(f"⚠️ 損失 ${abs(event['amount'])}")
                    
            # 處理薪水 (每四週一次)
            if week % 4 == 0:
                salary = 30000
                st.session_state.cash += salary
                event_logs.append(f"💼 【發薪日】辛苦工作了一個月，獲得薪資 ${salary:,}！")
                    
            # 更新狀態
            st.session_state.prev_price = current_price
            st.session_state.week += 1
            
            if total_asset < 0 or st.session_state.week > st.session_state.MAX_WEEKS:
                st.session_state.game_over = True
                
            week_separator = [f"📅 --- 【 第 {week} 週 結算 】 ---"]
            st.session_state.logs = week_separator + action_log + event_logs + advisor_logs + st.session_state.logs
    
        # UI 配置
        st.container()
        col_b, col_s, col_n = st.columns(3)
        
        with col_b:
            st.number_input("買入數量 (股)", min_value=1, step=100, key="b_qty")
            st.button("🟢 買入 (Buy)", on_click=handle_action, args=("b",), use_container_width=True)
            
        with col_s:
            max_sell = max(1, st.session_state.stock)
            st.number_input("賣出數量 (股)", min_value=1, max_value=max_sell, step=100, key="s_qty")
            st.button("🔵 賣出 (Sell)", on_click=handle_action, args=("s",), use_container_width=True)
            
        with col_n:
            st.markdown("<br><br>", unsafe_allow_html=True) # 用空行對齊前面的 input
            st.button("🔴 觀望 (Hold)", on_click=handle_action, args=("n",), use_container_width=True)

with main_col_right:
    # =====================
    # 對話與紀錄區 (永遠顯示)
    # =====================
    st.subheader("📝 遊戲紀錄與回饋")
    
    # 使用固定高度的 container 產生獨立捲軸
    with st.container(height=650, border=True):
        for log in st.session_state.logs:
            if log.startswith("📅"):
                st.markdown(f"#### {log}")
            elif log.startswith("❌") or log.startswith("💥") or log.startswith("⚠️"):
                st.error(log)
            elif log.startswith("✅") or log.startswith("✨") or log.startswith("🎉"):
                st.success(log)
            elif log.startswith("🌟"):
                st.warning(log)
            elif "═" in log:
                pass # 忽略分隔線
            else:
                st.info(log)
