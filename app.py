import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from market import load_stock_data
from education import FinancialAdvisor
from events import draw_event, historical_news
from datetime import datetime, timedelta
import random

# =====================
# 頁面設定
# =====================
st.set_page_config(page_title="華爾街見習生", page_icon="📈", layout="wide")

# =====================
# 自訂 CSS 美化介面
# =====================
st.markdown("""
<style>
    /* 主標題漸層效果 */
    h1 {
        background: linear-gradient(90deg, #f7971e, #ffd200);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    /* 側邊欄背景 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    /* 按鈕樣式 */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.6rem 1.2rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    /* Metric 卡片 */
    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 12px 16px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    /* 遊戲紀錄容器 */
    [data-testid="stVerticalBlock"] > div:has(> [data-testid="stAlert"]) {
        animation: fadeIn 0.3s ease-in;
    }
    section[data-testid="stSidebar"] div.block-container {
        padding-top: 0.7rem;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# =====================
# 初始化 Session State
# =====================
if "initialized" not in st.session_state:
    st.session_state.initialized = True

    with st.spinner('🕰️ 正在搭乘時光機，下載歷史行情...'):
        try:
            st.session_state.df = load_stock_data()
        except RuntimeError as exc:
            st.error(str(exc))
            st.stop()
        except Exception as exc:
            st.error("資料初始化失敗，請稍後重新整理頁面。")
            st.exception(exc)
            st.stop()

    # 攤平 yfinance 可能產生的 MultiIndex 欄位
    if hasattr(st.session_state.df.columns, 'levels'):
        st.session_state.df.columns = st.session_state.df.columns.get_level_values(0)

    if st.session_state.df.empty:
        st.error("目前沒有可用的股票資料，請重新整理頁面再試一次。")
        st.stop()

    st.session_state.MAX_WEEKS = 156
    st.session_state.TARGET = 800000

    required_days = st.session_state.MAX_WEEKS * 5 + 1
    max_offset = max(0, len(st.session_state.df) - required_days)
    min_offset = 30 if max_offset >= 30 else 0
    st.session_state.START_OFFSET = random.randint(min_offset, max_offset)
    st.session_state.week = 1

    st.session_state.cash = 500000
    st.session_state.stock = 0
    st.session_state.avg_price = 0

    # 若起始偏移超出資料長度，調整為最後一筆資料的索引
    if st.session_state.START_OFFSET >= len(st.session_state.df):
        st.session_state.START_OFFSET = max(0, len(st.session_state.df) - 1)
        st.warning(f"START_OFFSET 超出資料長度，已自動調整為 {st.session_state.START_OFFSET}")

    # 取得起始收盤價
    initial_close = st.session_state.df["Close"].iloc[st.session_state.START_OFFSET]
    st.session_state.prev_price = float(
        initial_close.iloc[0] if hasattr(initial_close, "iloc") else initial_close
    )

    st.session_state.trade_days_x = []
    st.session_state.trade_prices_y = []
    st.session_state.trade_actions_color = []

    st.session_state.advisor = FinancialAdvisor()
    st.session_state.logs = [
        "🎮 歡迎來到【華爾街見習生】網頁版！",
        "準備好開始你的投資之旅了嗎？請在左方進行操作！"
    ]
    st.session_state.game_over = False
    st.session_state.total_salary_net = 0   # 累計薪水淨收入
    st.session_state.total_event_net = 0    # 累計隨機事件淨收入
    st.session_state.realized_profit = 0    # 已實現投資損益
    st.session_state.total_invested_cost = 0  # 累計投入股市成本（買入本金 + 手續費）
    st.session_state.shown_news = set()     # 記錄已顯示的歷史新聞

    # 記錄遊戲開始的第一天真實日期
    start_date_obj = st.session_state.df["Date"].iloc[st.session_state.START_OFFSET]
    if hasattr(start_date_obj, 'date'):
        st.session_state.game_start_date = start_date_obj.date()
    else:
        st.session_state.game_start_date = datetime.strptime(
            str(start_date_obj)[:10], "%Y-%m-%d"
        ).date()

if "realized_profit" not in st.session_state:
    st.session_state.realized_profit = 0

if "total_invested_cost" not in st.session_state:
    st.session_state.total_invested_cost = 0

INVESTMENT_QUOTES = [
    "💬 巴菲特｜風險來自於你不知道自己正在做什麼。",
    "💬 巴菲特｜價格是你付出的，價值是你得到的。",
    "💬 彼得林區｜買股票前，先知道你為什麼買它。",
    "💬 彼得林區｜投資不是猜測市場，而是理解企業。",
    "💬 班傑明葛拉漢｜短期市場是投票機，長期市場是 weighing machine。",
    "💬 霍華馬克斯｜最重要的不是買好資產，而是用好價格買進。",
    "💬 約翰柏格｜時間是投資人的朋友，衝動是投資人的敵人。",
    "💬 查理蒙格｜反過來想，總是反過來想。",
    "💬 傑西李佛摩｜市場永遠不會錯，錯的是人的看法。",
    "💬 塞斯卡拉曼｜耐心和紀律，往往比聰明更稀有。"
]

if "shown_quotes" not in st.session_state:
    st.session_state.shown_quotes = set()

# =====================
# 準備本週資料
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
unrealized = (
    (current_price - st.session_state.avg_price) * st.session_state.stock
    if st.session_state.stock > 0 else 0
)

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
def sidebar_value(label, value, color="#e0e0e0", size=22):
    st.markdown(f"##### {label}")
    st.markdown(
        f"""
        <div style="
            font-size:{size}px;
            font-weight:700;
            color:{color};
            line-height:1.05;
            margin-bottom:0.35rem;
        ">
            {value}
        </div>
        """,
        unsafe_allow_html=True
    )


def money(value):
    return f"${value:,.0f}"


def pct(value):
    return f"{value:+.2f}%"


def get_investment_quote():
    if len(st.session_state.shown_quotes) >= len(INVESTMENT_QUOTES):
        st.session_state.shown_quotes = set()

    available_quotes = [
        quote for i, quote in enumerate(INVESTMENT_QUOTES)
        if i not in st.session_state.shown_quotes
    ]
    quote = random.choice(available_quotes)
    st.session_state.shown_quotes.add(INVESTMENT_QUOTES.index(quote))
    return f"📚 投資佳句｜{quote}"


def build_strategy_notes(action, outcome_change, bias_percent, cash_ratio, stock, current_price, avg_price):
    notes = []

    if action == "b":
        notes.append(random.choice([
            "買入後先設定一個退出條件：跌破均線、虧損達一定比例，或現金水位低於安全線。",
            "這次增加部位後，下一週先不要連續追價，等股價確認站穩再考慮加碼。",
            "買進完成後，請檢查單一持股是否過重；如果現金太少，下一步應優先保留流動性。"
        ]))
    elif action == "s":
        notes.append(random.choice([
            "賣出後先記錄原因：停利、停損、降低風險，避免下次只憑感覺進出場。",
            "這次減碼後，若股價續漲，不急著追回；先等拉回或新的買點。",
            "手上現金增加後，下一步可以等待風險報酬比更好的位置。"
        ]))
    else:
        notes.append(random.choice([
            "觀望時請明確定義觸發條件：突破均線買、跌破支撐賣，或現金比例達標再行動。",
            "這週沒有交易，可以把重點放在確認趨勢，而不是急著找操作。",
            "沒有動作也要有理由；如果只是猶豫，下一週請先決定你的交易規則。"
        ]))

    if outcome_change >= 3:
        notes.append(random.choice([
            f"下週股價上漲 {pct(outcome_change)}，若已持股，可考慮分批停利；若空手，避免情緒追高。",
            f"價格推進 {pct(outcome_change)}，下一步觀察是否能守住 10 日均線。",
            f"本週偏多，漲幅 {pct(outcome_change)}；請把停利點往上調，而不是放任獲利回吐。"
        ]))
    elif outcome_change <= -3:
        notes.append(random.choice([
            f"下週股價下跌 {pct(outcome_change)}，先檢查是否需要降部位，不要急著攤平。",
            f"市場轉弱 {pct(outcome_change)}，如果現金不足，下一步應先降低風險。",
            f"價格回落 {pct(outcome_change)}；若跌破你的停損規則，就應執行而不是找理由。"
        ]))
    else:
        notes.append(random.choice([
            f"股價變動 {pct(outcome_change)}，訊號偏中性；下一週可等突破或跌破再決策。",
            f"市場波動不大，變化 {pct(outcome_change)}；適合檢查持股比例，不急著操作。",
            f"價格暫時整理，{pct(outcome_change)} 的變動不必過度解讀，先看量價和均線。"
        ]))

    if cash_ratio < 0.15:
        notes.append(random.choice([
            "現金水位偏低，遇到突發事件時會比較被動。",
            "資金幾乎都在市場裡，接下來要特別注意流動性。",
            "現金緩衝不足，建議先避免連續加碼。"
        ]))
    elif cash_ratio > 0.75:
        notes.append(random.choice([
            "現金比例很高，風險低，但也可能錯過行情。",
            "你目前偏保守，若趨勢明確，可以思考分批進場。",
            "防守做得不錯，但投資目標也需要適度承擔風險。"
        ]))
    elif stock > 0 and avg_price > 0 and current_price < avg_price:
        notes.append(random.choice([
            "目前持股在成本下方，先控制部位，再討論是否攤平。",
            "帳面虧損時最容易情緒化，建議用規則取代直覺。",
            "股價低於平均成本，重點是判斷這是短期回檔還是趨勢轉弱。"
        ]))
    elif abs(bias_percent) > 8:
        notes.append(random.choice([
            f"股價和 10 日均線乖離 {pct(bias_percent)}，短線波動風險提高。",
            f"目前乖離率 {pct(bias_percent)}，不宜只因為漲跌幅就衝動交易。",
            f"價格離均線較遠，乖離 {pct(bias_percent)}，可以等拉回或整理。"
        ]))

    return [f"🎯 策略提醒｜{note}" for note in notes[:3]]


def build_weekly_summary(week, current_price, next_price, total_asset_before, total_asset_after, cash, stock):
    asset_change = total_asset_after - total_asset_before
    price_change = ((next_price - current_price) / current_price) * 100 if current_price else 0
    cash_ratio = cash / total_asset_after if total_asset_after else 0
    return [
        f"📅 第 {week} 週結算",
        f"📊 本週摘要｜總資產 {money(total_asset_after)}（{asset_change:+,.0f}）｜股價變化 {pct(price_change)}｜現金水位 {cash_ratio * 100:.1f}%｜持股 {stock} 股"
    ]


with st.sidebar:
    st.markdown("##### 📈 儀表板")

    sidebar_value("週數", f"{display_week} / {st.session_state.MAX_WEEKS}", size=26)
    sidebar_value("🗓️ 目前日期", current_date_str, size=20)
    sidebar_value("當前股價", f"${current_price:.2f}", size=26)

    col1, col2 = st.columns(2)
    with col1:
        sidebar_value("現金 (Cash)", f"${st.session_state.cash:,.0f}", color="#80d996", size=18)
    with col2:
        sidebar_value("持股 (Stock)", f"{st.session_state.stock} 股", color="#8ab4f8", size=18)

    realized_color = "#80d996" if st.session_state.realized_profit >= 0 else "#ff8a80"
    unrealized_color = "#80d996" if unrealized >= 0 else "#ff8a80"
    sidebar_value("已實現損益", f"${st.session_state.realized_profit:,.0f}", color=realized_color, size=18)
    st.metric(label="", value="", delta=f"{st.session_state.realized_profit:,.1f}")
    sidebar_value("未實現損益", f"${unrealized:,.0f}", color=unrealized_color, size=18)
    st.metric(label="", value="", delta=f"{unrealized:,.1f}")

    st.divider()

    sidebar_value("總資產", f"${total_asset:,.0f}", color="#ffd166", size=26)
    st.metric(label="", value="", delta=f"{total_asset - 500000:,.2f}")

    # 進度條
    progress = min(total_asset / st.session_state.TARGET, 1.0)
    st.caption(f"🏆 目標達成率：{progress * 100:.1f}%")
    st.progress(progress)

# =====================
# 遊戲主畫面
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
    - 💰 **起始資金**：\\$500,000
    - ⏳ **遊戲時間**：156 週（3 年）
    - 🏆 **目標總資產**：\\$800,000 (達標即可通關！)
    - 💼 **薪水機制**：每 4 週發薪 \\$50,000，同時扣除生活費 \\$40,000，淨入帳 \\$10,000

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
main_col_left, main_col_right = st.columns([1.5, 1.5], gap="medium")

with main_col_left:
    # =====================
    # 繪製走勢圖 (永遠顯示)
    # =====================
    history_close = df["Close"].iloc[0:day_index + 1]
    history_ma10 = df["Close"].rolling(window=10).mean().iloc[0:day_index + 1]
    history_dates = df["Date"].iloc[0:day_index + 1]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(history_dates, history_close.values, label="Stock Price", color="#2c3e50", linewidth=2)
    ax.fill_between(history_dates, history_close.values, color="#3498db", alpha=0.1)
    ax.plot(history_dates, history_ma10.values, label="10-Day MA", color="#e74c3c", linestyle="--", alpha=0.8)

    if st.session_state.stock > 0:
        ax.axhline(y=st.session_state.avg_price, color="#27ae60", linestyle="-.", label="My Avg Cost", zorder=3)

    if st.session_state.trade_days_x:
        ax.scatter(
            st.session_state.trade_days_x,
            st.session_state.trade_prices_y,
            c=st.session_state.trade_actions_color,
            s=70, zorder=5, edgecolors='white'
        )

    current_day_label = history_dates.iloc[-1]
    ax.scatter(current_day_label, current_price, color="#f1c40f", s=150, edgecolors='black', label="Decision Point", zorder=6)

    ax.scatter([], [], color="green", label="Buy", s=50)
    ax.scatter([], [], color="blue", label="Sell", s=50)
    ax.scatter([], [], color="red", label="Hold", s=50)

    view_window = 30
    start_x = max(0, day_index - view_window)
    end_x = min(len(df) - 1, day_index + 2)
    ax.set_xlim(df["Date"].iloc[start_x], df["Date"].iloc[end_x])

    visible_history = df["Close"].iloc[start_x:day_index + 1]
    y_min = visible_history.min() * 0.98
    y_max = visible_history.max() * 1.02

    if st.session_state.stock > 0:
        y_min = min(y_min, st.session_state.avg_price * 0.98)
        y_max = max(y_max, st.session_state.avg_price * 1.02)

    ax.set_ylim(y_min, y_max)
    ax.set_title(
        f"Market View - {chart_date_str}  (Week {display_week} / {st.session_state.MAX_WEEKS})",
        fontsize=13, fontweight="bold"
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc='upper left', fontsize='small')
    fig.tight_layout()

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    # =====================
    # 操作區與結算區
    # =====================
    if st.session_state.game_over:
        st.success("🎉 遊戲結束！")
        st.subheader(f"💰 最終總資產：\\${total_asset:,.2f} (目標: \\${st.session_state.TARGET:,.0f})")

        # 計算純投資損益
        START_CAPITAL = 500000
        invest_gain = total_asset - START_CAPITAL - st.session_state.total_salary_net - st.session_state.total_event_net
        invested_cost = st.session_state.total_invested_cost
        investment_roi = (invest_gain / invested_cost * 100) if invested_cost > 0 else 0
        total_asset_growth = (total_asset - START_CAPITAL) / START_CAPITAL * 100

        st.divider()
        st.markdown("#### 📊 投資損益分析")
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("起始資金", f"${START_CAPITAL:,.0f}")
        col_b.metric("薪水淨收入", f"${st.session_state.total_salary_net:,.0f}")
        col_c.metric("事件淨收益", f"${st.session_state.total_event_net:,.0f}")
        col_d.metric("投入股市成本", f"${invested_cost:,.0f}")
        st.caption("ROI 使用「投資損益 ÷ 累計投入股市成本」計算；總資產成長率則使用「總資產變化 ÷ 起始資金」計算。")

        roi_text = "尚未投入股市，無法計算 ROI。" if invested_cost == 0 else f"投資 ROI：{investment_roi:.1f}%"
        if invest_gain >= 0:
            st.success(
                f"📈 **你靠投資賺了 ${invest_gain:,.0f}！**"
                f"（{roi_text}｜總資產成長率：{total_asset_growth:.1f}%）"
            )
        else:
            st.error(
                f"📉 **你靠投資虧了 ${abs(invest_gain):,.0f}。**"
                f"（{roi_text}｜總資產成長率：{total_asset_growth:.1f}%）"
            )

        if total_asset >= st.session_state.TARGET:
            st.balloons()
            st.success("🏆 恭喜你達成目標金額，成功通關！")
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

        # =====================
        # 操作區 Callback
        # =====================
        def handle_action(action_type):
            action = action_type
            qty = st.session_state.get(f"{action}_qty", 0) if action in ["b", "s"] else 0
            current_color = "red"
            action_log = []

            if action == "b":
                if qty <= 0:
                    st.session_state.logs = ["❌ 買入失敗：股數必須大於 0"] + st.session_state.logs
                    return
                fee = current_price * qty * 0.001425
                total_cost = current_price * qty + fee
                if st.session_state.cash >= total_cost:
                    stock_cost = st.session_state.avg_price * st.session_state.stock + current_price * qty
                    st.session_state.stock += qty
                    st.session_state.avg_price = stock_cost / st.session_state.stock
                    st.session_state.cash -= total_cost
                    st.session_state.total_invested_cost += total_cost
                    action_log.append(f"✅ 成功買入 {qty} 股 (手續費：\\${fee:.2f})")
                    current_color = "green"
                else:
                    st.session_state.logs = [
                        f"❌ 買入失敗：現金不足。需要 \\${total_cost:,.0f}，目前現金 \\${st.session_state.cash:,.0f}。"
                    ] + st.session_state.logs
                    return

            elif action == "s":
                if qty <= 0:
                    st.session_state.logs = ["❌ 賣出失敗：股數必須大於 0"] + st.session_state.logs
                    return
                if st.session_state.stock >= qty:
                    fee = current_price * qty * 0.001425
                    tax = current_price * qty * 0.003
                    profit = (current_price - st.session_state.avg_price) * qty - fee - tax
                    st.session_state.cash += current_price * qty - fee - tax
                    st.session_state.stock -= qty
                    st.session_state.realized_profit += profit
                    if st.session_state.stock == 0:
                        st.session_state.avg_price = 0
                    action_log.append(f"✅ 成功賣出 {qty} 股 (手續費：\\${fee:.2f} / 交易稅：\\${tax:.2f} / 已實現損益：\\${profit:,.0f})")
                    current_color = "blue"
                else:
                    st.session_state.logs = [
                        f"❌ 賣出失敗：股票不足。你想賣 {qty} 股，目前持有 {st.session_state.stock} 股。"
                    ] + st.session_state.logs
                    return

            elif action == "n":
                action_log.append("⏳ 本週沒有操作，抱緊處理。")
                current_color = "red"

            # 紀錄歷史
            st.session_state.trade_days_x.append(current_day_label)
            st.session_state.trade_prices_y.append(current_price)
            st.session_state.trade_actions_color.append(current_color)

            latest_total_asset = st.session_state.cash + st.session_state.stock * current_price

            # 計算下一週的價格 (即將揭曉的結果)
            next_week = st.session_state.week + 1
            next_display_week = min(next_week, st.session_state.MAX_WEEKS)
            next_day_index = st.session_state.START_OFFSET + next_display_week * 5
            next_day_index = min(next_day_index, len(df) - 1)
            next_close = df["Close"].iloc[next_day_index]
            next_price = float(next_close.iloc[0] if hasattr(next_close, "iloc") else next_close)

            # 呼叫導師系統
            current_ma10 = history_ma10.iloc[-1] if not pd.isna(history_ma10.iloc[-1]) else current_price
            st.session_state.advisor.evaluate(
                action, current_price, next_price, st.session_state.prev_price,
                st.session_state.avg_price, current_ma10,
                st.session_state.cash, latest_total_asset, st.session_state.stock, ui_mode=True
            )
            outcome_change = ((next_price - current_price) / current_price) * 100 if current_price else 0
            bias_percent = ((current_price - current_ma10) / current_ma10) * 100 if current_ma10 else 0

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
                    # 若新聞不是週五，提前一週提醒玩家，讓每週決策更有事件感。
                    trigger_date = news_date if news_date.weekday() == 4 else news_date - timedelta(days=7)
                    if st.session_state.game_start_date <= trigger_date <= current_date_val:
                        news_logs.append(f"📰 【歷史新聞快訊】 {news['date']} - {news['text']}")
                        st.session_state.shown_news.add(i)

            # 處理隨機事件：約 40% 機率觸發
            event_logs = []
            if random.random() < 0.4:
                event = draw_event()
                st.session_state.cash += event["amount"]
                st.session_state.total_event_net += event["amount"]
                if event["amount"] != 0:
                    event_logs.append(f"📌 【隨機事件】：{event['name']}")
                    if event["amount"] > 0:
                        event_logs.append(f"🎉 獲得 \\${event['amount']}")
                    elif event["amount"] < 0:
                        event_logs.append(f"⚠️ 損失 \\${abs(event['amount'])}")
            else:
                event_logs.append(random.choice([
                    "🏠 生活事件｜本週生活平穩，沒有額外收支。",
                    "🏠 生活事件｜這週沒有突發支出，可以專心觀察市場。",
                    "🏠 生活事件｜日常開銷維持穩定，資金沒有額外變化。"
                ]))

            # 處理薪水 (每四週一次)
            if week % 4 == 0:
                salary = 50000
                living_cost = 40000
                net = salary - living_cost
                st.session_state.cash += net
                st.session_state.total_salary_net += net
                event_logs.append(
                    f"💼 【發薪日】薪資 \\${salary:,} 已入帳，扣除生活費 \\${living_cost:,}，實際淨入帳 \\${net:,}"
                )

            # ===== 現金不足時強制賣股 =====
            if st.session_state.cash < 0 and st.session_state.stock > 0:
                deficit = abs(st.session_state.cash)
                fee_rate = 0.001425 + 0.003
                shares_needed = int(deficit / (current_price * (1 - fee_rate))) + 1
                shares_to_sell = min(shares_needed, st.session_state.stock)

                fee = current_price * shares_to_sell * 0.001425
                tax = current_price * shares_to_sell * 0.003
                forced_profit = (current_price - st.session_state.avg_price) * shares_to_sell - fee - tax
                proceeds = current_price * shares_to_sell - fee - tax

                st.session_state.cash += proceeds
                st.session_state.stock -= shares_to_sell
                st.session_state.realized_profit += forced_profit
                if st.session_state.stock == 0:
                    st.session_state.avg_price = 0

                event_logs.append(
                    f"🚨 【強制賣股】現金不足！系統自動賣出 {shares_to_sell} 股以補充流動性 (入帳 ${proceeds:,.0f} / 已實現損益 ${forced_profit:,.0f})"
                )

            # 更新狀態
            latest_total_asset = st.session_state.cash + st.session_state.stock * current_price
            cash_ratio = st.session_state.cash / latest_total_asset if latest_total_asset else 0
            strategy_notes = build_strategy_notes(
                action,
                outcome_change,
                bias_percent,
                cash_ratio,
                st.session_state.stock,
                current_price,
                st.session_state.avg_price
            )
            st.session_state.prev_price = current_price
            st.session_state.week += 1

            if st.session_state.cash >= st.session_state.TARGET:
                st.session_state.logs = (
                    [f"🎉 恭喜！你的現金已達 ${st.session_state.cash:,.0f}，成功達成 ${st.session_state.TARGET:,.0f} 目標，遊戲提前結束！"]
                    + st.session_state.logs
                )
                st.session_state.game_over = True

            elif (
                (st.session_state.cash < 0 and st.session_state.stock == 0)
                or st.session_state.week > st.session_state.MAX_WEEKS
                or latest_total_asset < 0
            ):
                st.session_state.game_over = True

            weekly_summary = build_weekly_summary(
                week,
                current_price,
                next_price,
                total_asset,
                latest_total_asset,
                st.session_state.cash,
                st.session_state.stock
            )
            if news_logs:
                news_logs = [news_logs[0]]
            quote_logs = []
            if week % 3 == 1:
                quote_logs.append(get_investment_quote())
            st.session_state.logs = (
                weekly_summary + action_log + news_logs + event_logs + strategy_notes + quote_logs + st.session_state.logs
            )

        # =====================
        # UI 操作按鈕
        # =====================
        col_b, col_s, col_n = st.columns(3)

        with col_b:
            st.number_input("買入數量 (股)", min_value=1, step=1, key="b_qty")
            st.button("🟢 買入 (Buy)", on_click=handle_action, args=("b",), use_container_width=True)

        with col_s:
            max_sell = max(1, st.session_state.stock)
            st.number_input("賣出數量 (股)", min_value=1, max_value=max_sell, step=1, key="s_qty")
            st.button("🔵 賣出 (Sell)", on_click=handle_action, args=("s",), use_container_width=True)

        with col_n:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.button("🔴 觀望 (Hold)", on_click=handle_action, args=("n",), use_container_width=True)

with main_col_right:
    # =====================
    # 對話與紀錄區 (永遠顯示)
    # =====================
    st.subheader("📝 遊戲紀錄與回饋")

    with st.container(height=900, border=True):
        for log in st.session_state.logs:
            if log.startswith("📅"):
                st.markdown(f"#### {log}")
            elif log.startswith("📊"):
                st.info(log)
            elif log.startswith("🎯"):
                st.warning(log)
            elif log.startswith("📚"):
                st.info(log)
            elif log.startswith("📰"):
                st.warning(log)
            elif log.startswith("🏠") or log.startswith("💼"):
                st.info(log)
            elif log.startswith("❌") or log.startswith("💥") or log.startswith("⚠️"):
                st.error(log)
            elif log.startswith("✅") or log.startswith("✨") or log.startswith("🎉") or log.startswith("📌"):
                st.success(log)
            elif log.startswith("🌟"):
                st.warning(log)
            elif "═" in log:
                pass  # 忽略分隔線
            else:
                st.info(log)
