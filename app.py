import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from market import load_stock_data
from education import FinancialAdvisor
from events import draw_event, historical_news
from datetime import datetime

# 頁面設定
st.set_page_config(page_title="華爾街見習生", page_icon="📈", layout="wide")

# 初始化 Session State
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    
    with st.spinner('正在搭乘時光機，下載歷史行情...'):
        st.session_state.df = load_stock_data()
        
    if hasattr(st.session_state.df.columns, 'levels'):
        st.session_state.df.columns = st.session_state.df.columns.get_level_values(0)
        
    st.session_state.MAX_WEEKS = 156
    st.session_state.TARGET = 1000000
    st.session_state.START_OFFSET = 30
    st.session_state.week = 1
    
    st.session_state.cash = 500000
    st.session_state.stock = 0
    st.session_state.avg_price = 0
    
    if st.session_state.START_OFFSET >= len(st.session_state.df):
        # 若起始偏移超出資料長度，調整為最後一筆資料的索引
        st.session_state.START_OFFSET = max(0, len(st.session_state.df) - 1)
        st.warning(f"START_OFFSET 超出資料長度，已自動調整為 {st.session_state.START_OFFSET}")
    
    # 取得起始收盤價
    initial_close = st.session_state.df["Close"].iloc[st.session_state.START_OFFSET]
    st.session_state.prev_price = float(initial_close)  # 直接轉成 float
    
    st.session_state.trade_days_x = []
    st.session_state.trade_prices_y = []
    st.session_state.trade_actions_color = []
    
    st.session_state.advisor = FinancialAdvisor()
    st.session_state.logs = ["🎮 歡迎來到【華爾街見習生】網頁版！", "準備好開始你的投資之旅了嗎？請在左方進行操作！"]
    st.session_state.game_over = False
    st.session_state.total_salary_net = 0   # 累計薪水淨收入
    st.session_state.total_event_net = 0    # 累計隨機事件淨收入
    st.session_state.shown_news = set()     # 記錄已顯示的歷史新聞
    
    # 記錄遊戲開始的第一天真實日期
    start_date_obj = st.session_state.df["Date"].iloc[st.session_state.START_OFFSET]
    if hasattr(start_date_obj, 'date'):
        st.session_state.game_start_date = start_date_obj.date()
    else:
        st.session_state.game_start_date = datetime.strptime(str(start_date_obj)[:10], "%Y-%m-%d").date()

# =====================
# 準備數據 (在側邊欄外)
# =====================
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

# 取得目前這週對應的真實日期
current_date = df["Date"].iloc[day_index]
if hasattr(current_date, 'strftime'):
    current_date_str = current_date.strftime("%Y年%m月%d日")
    chart_date_str = current_date.strftime("%Y-%m-%d")
else:
    current_date_str = str(current_date)[:10]
    chart_date_str = current_date_str

# =====================
# 側邊欄：投資儀表板
# =====================
with st.sidebar:

    st.markdown("## 📈 儀表板")

    # ===== 週數 =====
    st.markdown("週數")
    st.markdown(
        f"<div style='font-size:14px; font-weight:bold;'>"
        f"{display_week} / {st.session_state.MAX_WEEKS}</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    # ===== 日期 =====
    st.markdown("🗓️ 目前日期")
    st.markdown(
        f"<div style='font-size:13px; font-weight:bold;'>"
        f"{current_date_str}</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    # ===== 股價 =====
    st.markdown("當前股價")
    st.markdown(
        f"<div style='font-size:14px; font-weight:bold;'>"
        f"${current_price:.2f}</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    # ===== 現金與持股 =====
    col_cash, col_stock = st.columns(2)

    with col_cash:
        st.markdown("現金 (Cash)")
        st.markdown(
            f"""
            <div style="
                font-size:11px;
                font-weight:bold;
                color:#188038;
            ">
            ${st.session_state.cash:,.0f}
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_stock:
        st.markdown("持股 (Stock)")
        st.markdown(
            f"""
            <div style="
                font-size:11px;
                font-weight:bold;
                color:#1967d2;
            ">
            {st.session_state.stock} 股
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ===== 未實現損益 =====
    st.markdown("未實現損益")

    unrealized_color = "#188038" if unrealized >= 0 else "#d93025"

    st.markdown(
        f"""
        <div style="
            font-size:11px;
            font-weight:bold;
            color:{unrealized_color};
        ">
        ${unrealized:,.0f}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.metric(
        label="",
        value="",
        delta=f"{unrealized:,.1f}"
    )

    st.markdown("---")

    # ===== 總資產 =====
    st.markdown("總資產")

    st.markdown(
        f"""
        <div style="
            font-size:14px;
            font-weight:bold;
            color:#f9ab00;
        ">
        ${total_asset:,.0f}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.metric(
        label="",
        value="",
        delta=f"{total_asset - 500000:,.2f}"
    )

# =====================
# 標題與規則
# =====================
st.title("📈 華爾街見習生：投資模擬遊戲")

with st.expander("📖 遊戲規則與背景 (點擊展開/收起)", expanded=(st.session_state.week == 1)):
    ticker_name = df.attrs.get('ticker', '神秘股票')
    company_name = df.attrs.get('company_name', ticker_name)
    sector = df.attrs.get('sector', '未知')
    industry = df.attrs.get('industry', '未知')
    st.markdown(f"""
    **【遊戲背景】**
    你是一位剛踏入股市的見習生。我們為你準備了一台時光機，將帶你回到過去的某一段真實歷史行情中。

    🎯 **本局操盤標的：{company_name}（{ticker_name}）**
    🏭 **所屬產業：{sector}｜{industry}**

    **【你的任務】**
    - 💰 **起始資金**：\$500,000
    - ⏳ **遊戲時間**：156 週（3 年）
    - 🏆 **目標總資產**：\$800,000 (達標即可通關！)
    - 💼 **薪水機制**：每 4 週發薪 \$50,000，同時扣除生活費 \$40,000，淨入帳 \$10,000

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
# 主遊戲區：圖表 + 紀錄 (側並排)
# =====================
game_col_left, game_col_right = st.columns([1.5, 1.5], gap="medium")

with game_col_left:
    # =====================
    # 股價圖表 (調小)
    # =====================
    history_close = df["Close"].iloc[0:day_index + 1]
    history_ma10 = df["Close"].rolling(window=10).mean().iloc[0:day_index + 1]
    
    fig, ax = plt.subplots(figsize=(8, 4))  # 從 (10, 5) 調小到 (8, 4)
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
    ax.set_title(f"Market View - {chart_date_str}  (Week {display_week} / {st.session_state.MAX_WEEKS})", fontsize=12, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc='upper left', fontsize='small')
    plt.tight_layout()
    
    st.pyplot(fig, use_container_width=True)
    
    # =====================
    # 操作區與結算區
    # =====================
    if st.session_state.game_over:
        st.success("🎉 遊戲結束！")
        st.subheader(f"💰 最終總資產：\${total_asset:,.2f} (目標: \${st.session_state.TARGET:,.0f})")
        
        # 計算純投資損益
        START_CAPITAL = 500000
        invest_gain = total_asset - START_CAPITAL - st.session_state.total_salary_net - st.session_state.total_event_net
        
        st.divider()
        st.markdown("#### 📊 投資損益分析")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("起始資金", f"${START_CAPITAL:,.0f}")
        col_b.metric("薪水淨收入", f"${st.session_state.total_salary_net:,.0f}")
        col_c.metric("事件淨收益", f"${st.session_state.total_event_net:,.0f}")
        
        if invest_gain >= 0:
            st.success(f"📈 **你靠投資賺了 ${invest_gain:,.0f}！**（報酬率：{invest_gain/START_CAPITAL*100:.1f}%）")
        else:
            st.error(f"📉 **你靠投資虧了 ${abs(invest_gain):,.0f}。**（虧損率：{abs(invest_gain)/START_CAPITAL*100:.1f}%）")
        
        if total_asset >= st.session_state.TARGET:
            st.balloons()
            st.success("🏆 恭喜你達成目標金額，成功通關！")
            st.session_state.game_over = True
        else:
            st.error("📉 很可惜，你沒有達到目標金額。")
                
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
                    action_log.append(f"✅ 成功買入 {qty} 股 (手續費：\${fee:.2f})")
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
                    action_log.append(f"✅ 成功賣出 {qty} 股 (手續費：\${fee:.2f} / 交易稅：\${tax:.2f})")
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
            
            # 計算下一週的價格
            next_week = st.session_state.week + 1
            next_display_week = min(next_week, st.session_state.MAX_WEEKS)
            next_day_index = st.session_state.START_OFFSET + next_display_week * 5
            next_day_index = min(next_day_index, len(df) - 1)
            next_close = df["Close"].iloc[next_day_index]
            next_price = float(next_close.iloc[0] if hasattr(next_close, "iloc") else next_close)
            
            # 呼叫導師系統
            current_ma10 = history_ma10.iloc[-1] if not pd.isna(history_ma10.iloc[-1]) else current_price
            advisor_logs = st.session_state.advisor.evaluate(
                action, current_price, next_price, st.session_state.prev_price, 
                st.session_state.avg_price, current_ma10, 
                st.session_state.cash, total_asset, st.session_state.stock, ui_mode=True
            )
            
            # ===== 歷史新聞判定 =====
            current_date_obj = df["Date"].iloc[day_index]
            if hasattr(current_date_obj, 'date'):
                current_date_val = current_date_obj.date()
            else:
                current_date_val = datetime.strptime(str(current_date_obj)[:10], "%Y-%m-%d").date()
                
            news_logs = []
            for i, news in enumerate(historical_news):
                if i not in st.session_state.shown_news:
                    news_date = datetime.strptime(news["date"], "%Y-%m-%d").date()
                    if st.session_state.game_start_date <= news_date <= current_date_val:
                        news_logs.append(f"📰 【歷史新聞快訊】 {news['date']} - {news['text']}")
                        st.session_state.shown_news.add(i)
            
            # 處理隨機事件
            event_logs = []
            event = draw_event()
            st.session_state.cash += event["amount"]
            st.session_state.total_event_net += event["amount"]
            if event["amount"] != 0:
                event_logs.append(f"📌 【隨機事件】：{event['name']}")
                if event["amount"] > 0:
                    event_logs.append(f"🎉 獲得 \${event['amount']}")
                elif event["amount"] < 0:
                    event_logs.append(f"⚠️ 損失 \${abs(event['amount'])}")
                    
            # 處理薪水
            if week % 4 == 0:
                salary = 50000
                living_cost = 40000
                net = salary - living_cost
                st.session_state.cash += net
                st.session_state.total_salary_net += net
                event_logs.append(f"💼 【發薪日】薪資 \${salary:,} 已入帳，扣除生活費 \${living_cost:,}，實際淨入帳 \${net:,}")
            
            # 現金不足時強制賣股
            if st.session_state.cash < 0 and st.session_state.stock > 0:
                deficit = abs(st.session_state.cash)
                fee_rate = 0.001425 + 0.003
                shares_needed = int(deficit / (current_price * (1 - fee_rate))) + 1
                shares_to_sell = min(shares_needed, st.session_state.stock)
                
                fee = current_price * shares_to_sell * 0.001425
                tax = current_price * shares_to_sell * 0.003
                proceeds = current_price * shares_to_sell - fee - tax
                
                st.session_state.cash += proceeds
                st.session_state.stock -= shares_to_sell
                if st.session_state.stock == 0:
                    st.session_state.avg_price = 0
                    
                event_logs.append(f"🚨 【強制賣股】現金不足！系統自動賣出 {shares_to_sell} 股以補充流動性 (入帳 ${proceeds:,.0f})")
                    
            # 更新狀態
            st.session_state.prev_price = current_price
            st.session_state.week += 1
            
            if total_asset < 0 or st.session_state.week > st.session_state.MAX_WEEKS:
                st.session_state.game_over = True
                
            week_separator = [f"📅 --- 【 第 {week} 週 結算 】 ---"]
            st.session_state.logs = week_separator + news_logs + action_log + event_logs + advisor_logs + st.session_state.logs
    
        # UI 配置
        col_b, col_s, col_n = st.columns(3)
        
        with col_b:
            st.number_input("買入數量 (股)", min_value=1, step=100, key="b_qty")
            st.button("🟢 買入 (Buy)", on_click=handle_action, args=("b",), use_container_width=True)
            
        with col_s:
            max_sell = max(1, st.session_state.stock)
            st.number_input("賣出數量 (股)", min_value=1, max_value=max_sell, step=100, key="s_qty")
            st.button("🔵 賣出 (Sell)", on_click=handle_action, args=("s",), use_container_width=True)
            
        with col_n:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.button("🔴 觀望 (Hold)", on_click=handle_action, args=("n",), use_container_width=True)

with game_col_right:
    # =====================
    # 對話與紀錄區 (放大至1/2)
    # =====================
    st.subheader("📝 遊戲紀錄與回饋")
    
    # 使用更大的高度讓用戶減少滑動
    with st.container(height=900, border=True):
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
                pass
            else:
                st.info(log)
