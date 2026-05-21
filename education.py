import random

class FinancialAdvisor:
    def __init__(self):
        self.consecutive_buy = 0
        self.consecutive_sell = 0
        self.current_week = 0
        
        # 狀態追蹤
        self.last_action = None
        self.last_price = 0
        self.achievements = set()
        
        self.ui_mode = False
        self.logs = []

    def _out(self, msg):
        self.logs.append(msg)
        if not self.ui_mode:
            print(msg)
            
    def evaluate(self, action, current_price, next_price, prev_price, avg_price, ma10_price, cash, total_asset, stock, ui_mode=False):
        self.ui_mode = ui_mode
        self.logs = []
        
        self.current_week += 1
        week = self.current_week
        
        if prev_price == 0:
            prev_price = current_price
            
        context_change = ((current_price - prev_price) / prev_price) * 100 if prev_price != 0 else 0
        outcome_change = ((next_price - current_price) / current_price) * 100 if current_price != 0 else 0
        
        # 紀錄連續操作狀態
        if action == "b":
            self.consecutive_buy += 1
            self.consecutive_sell = 0
        elif action == "s":
            self.consecutive_sell += 1
            self.consecutive_buy = 0
        else:
            self.consecutive_buy = 0
            self.consecutive_sell = 0
            
        self._out("\n" + "═"*45)
        self._out(f"📚 【 財商導師 - 第 {week} 週盤後教室 】")
        self._out("═"*45)

        # 1. 玩家行為診斷
        self._diagnose_action(action, current_price, prev_price, avg_price, ma10_price, context_change)
        
        # 2. 市場環境分析（下週結果）
        self._analyze_market(outcome_change)
        
        # 3. 決策結果揭曉
        self._cause_and_effect(action, outcome_change)
        
        # 4. 資金控管診斷
        self._check_wallet(cash, total_asset)
        
        # 5. 徽章成就檢查
        self._check_achievements(action, current_price, avg_price, context_change, outcome_change, stock)
        
        # 6. 今日財商進階課
        self._daily_lesson(week)
        
        # 更新紀錄
        self.last_action = action
        self.last_price = current_price
        
        return self.logs
        
    def _analyze_market(self, change_percent):
        if change_percent > 3:
            msgs = [
                f"📈 【市場熱烘烘】：這週股價大漲了 {change_percent:.2f}%！就像限量球鞋突然變超火熱，大家都搶著想買，價格就被推高了。",
                f"📈 【買氣大噴發】：本週股價強勢上漲 {change_percent:.2f}%！市場上充滿樂觀氣氛。"
            ]
            self._out(random.choice(msgs))
        elif change_percent < -3:
            msgs = [
                f"📉 【市場冷冰冰】：這週股價大跌了 {abs(change_percent):.2f}%！大家因為害怕紛紛想拋售。",
                f"📉 【空頭來敲門】：本週股價慘跌 {abs(change_percent):.2f}%！市場出現壞消息，抱著股票的人開始緊張了。"
            ]
            self._out(random.choice(msgs))
        else:
            msgs = [
                f"📊 【市場在散步】：這週股價只波動了 {change_percent:.2f}%。買賣雙方還在觀望，價格像在原地踏步。",
                f"📊 【風平浪靜】：股價微幅變動 {change_percent:.2f}%。市場正在大口呼吸、調整節奏。"
            ]
            self._out(random.choice(msgs))
            
    def _cause_and_effect(self, action, outcome_change):
        if action in ["n", None]:
            return
            
        self._out("\n🔄 [ 決策結果揭曉 ]")
        if action == "b":
            if outcome_change < -3:
                self._out("💥 市場無情：你剛買進，市場立刻大跌。別灰心，短期的漲跌本來就是隨機的，重點是你有沒有設定好停損點！")
            elif outcome_change > 3:
                self._out("✨ 市場給糖：運氣不錯！剛買進就遇到大漲。但請記住，這只是帳面數字，還沒賣掉前都不算真正賺錢。")
            else:
                self._out("⚖️ 市場觀望：買進後目前股價沒有太大波動，耐心等待趨勢發動吧。")
        elif action == "s":
            if outcome_change < -3:
                self._out("🛡️ 完美閃避：太神啦！你剛賣掉，市場就暴跌。這波操作成功幫你避開了巨大的風險！")
            elif outcome_change > 3:
                self._out("😅 賣飛體驗：剛賣掉結果市場繼續大漲，心裡一定很嘔吧？但記住，『少賺總比大賠好』，紀律永遠擺第一！")
            else:
                self._out("⚖️ 防守成功：賣出後市場平靜，是不錯的現金防守策略。")
                
    def _diagnose_action(self, action, current_price, prev_price, avg_price, ma10_price, change_percent):
        self._out("\n🎯 [ 本週操作行為診斷 ]")
        
        # 計算乖離率 (Bias)
        bias_percent = ((current_price - ma10_price) / ma10_price) * 100 if ma10_price > 0 else 0
        
        if action == "b":
            self._out(f"🛒 你的行動：買入股票 (已連續買入 {self.consecutive_buy} 週)")
            
            if bias_percent > 10:
                self._out("⚠️ 專業術語：【嚴重追高 / FOMO】")
                self._out(f"💡 大白話：目前股價已經偏離 10 日均線高達 {bias_percent:.1f}%！在這個位階還衝進去買，面臨的回檔風險極大，這是不理性的『錯失恐懼症』！")
            elif avg_price > 0 and current_price < avg_price * 0.8:
                self._out("🚨 專業術語：【凹單攤平 / 沉沒成本謬誤】")
                self._out("💡 大白話：你的帳面虧損已經超過 20%，你不僅沒有停損，反而還繼續加碼！這在專業交易中是絕對的大忌。")
            elif avg_price > 0 and current_price < avg_price:
                self._out("💡 專業術語：【逢低攤平】")
                self._out("💡 大白話：在小幅虧損時選擇買進降低成本。只要確定趨勢還在，這是合理的策略。")
            elif bias_percent > 0 and bias_percent <= 10:
                self._out("✅ 專業術語：【順勢交易 / 動能買進】")
                self._out("💡 大白話：股價在均線之上且乖離率合理，你選擇順著趨勢買進，是非常標準的右側交易策略！")
            else:
                self._out("✅ 專業術語：【逢低佈局】")
                self._out("💡 大白話：在股價貼近或低於均線時買進，風險較低，是不錯的左側佈局。")
                
        elif action == "s":
            self._out(f"💰 你的行動：賣出股票 (已連續賣出 {self.consecutive_sell} 週)")
            
            if avg_price > 0 and current_price < avg_price:
                loss_percent = ((current_price - avg_price) / avg_price) * 100
                if loss_percent <= -10:
                    self._out("🏆 專業術語：【嚴格執行停損】")
                    self._out(f"💡 大白話：面對高達 {abs(loss_percent):.1f}% 的虧損，你沒有選擇凹單，而是果斷砍倉。能克服人性弱點執行停損，你已經具備職業操盤手的素質了！")
                else:
                    self._out("✅ 專業術語：【風險控制 / 小損出場】")
                    self._out("💡 大白話：發現苗頭不對立刻小賠出場，保住本金永遠是第一要務。")
            elif avg_price > 0 and current_price > avg_price:
                if self.consecutive_sell >= 2:
                    self._out("✅ 專業術語：【分批停利】")
                    self._out("💡 大白話：不一次賣光，而是分批賣出。這樣既能鎖住獲利，又能保留剩餘部位參與未來的上漲。")
                else:
                    self._out("✅ 專業術語：【獲利了結】")
                    self._out("💡 大白話：恭喜賺錢！把螢幕上的數字變成實實在在的現金，落袋為安永遠不嫌少。")
            else:
                self._out("⚠️ 專業術語：【清倉退出】")
                self._out("💡 大白話：將手中籌碼全數換回現金。")
                
        elif action == "n":
            self._out("⏳ 你的行動：觀望（不買不賣）")
            if avg_price > 0 and current_price < avg_price * 0.8:
                self._out("🚨 專業術語：【腳麻 / 凹單】")
                self._out("💡 大白話：虧損已經超過 20% 了，你卻選擇蓋牌不看！不設定停損點放任虧損擴大，是破產的最快途徑！")
            elif abs(change_percent) > 5:
                self._out("📘 專業術語：【以靜制動】")
                self._out("💡 大白話：市場波動劇烈，但你選擇不亂動，避免被多空雙巴。")
            else:
                self._out("💡 大白話：市場沒有明顯方向，空手觀望也是一種操作。")
        else:
            self._out("❌ 收到無效指令")
            
    def _check_wallet(self, cash, total_asset):
        self._out("\n🚨 [ 資金控管診斷 ]")
        if total_asset == 0:
            return
            
        cash_ratio = cash / total_asset
        
        if cash_ratio < 0.05:
            self._out("💥 【極度危險 / All-In】：你把超過 95% 的資金全押在股市裡！這代表你完全沒有保留『緊急預備金』，一旦遇到突發黑天鵝事件，你只能被迫低價變賣股票，這是通往破產的最快路徑！")
        elif cash_ratio < 0.15:
            self._out("⚠️ 【流動性偏低】：你的現金水位偏低，建議至少保留 20% 的現金，讓你在大跌時還有子彈可以危機入市。")
        elif cash_ratio > 0.8:
            self._out("💵 【資金閒置】：你的現金佔比過高（超過 80%）。這很安全，但也代表你的資產會漸漸被通貨膨脹吃掉。")
        else:
            self._out("💚 【黃金比例】：現金與股票配置適中（保有彈性與流動性），展現了專業的資金控管能力！")

    def _check_achievements(self, action, current_price, avg_price, context_change, outcome_change, stock):
        new_achievements = []
        
        # 1. 鑽石手：帳面虧損嚴重但死不賣
        if stock > 0 and avg_price > 0 and current_price < avg_price * 0.8 and action != "s":
            if "💎 鑽石手 (承受 -20% 虧損仍抱緊)" not in self.achievements:
                new_achievements.append("💎 鑽石手 (承受 -20% 虧損仍抱緊)")
                
        # 2. 危機入市：在大跌時勇敢買進
        if action == "b" and context_change < -5:
            if "🎯 危機入市 (在大跌超過 5% 時買進)" not in self.achievements:
                new_achievements.append("🎯 危機入市 (在大跌超過 5% 時買進)")
                
        # 3. 神機妙算：賣出後市場大跌
        if action == "s" and outcome_change < -5:
            if "🏃 神機妙算 (賣出後市場隨即暴跌)" not in self.achievements:
                new_achievements.append("🏃 神機妙算 (賣出後市場隨即暴跌)")

        # 4. 嚴格停損：虧損超過 10% 仍執行停損
        if action == "s" and avg_price > 0 and ((current_price - avg_price) / avg_price) <= -0.10:
            if "🏆 鐵血紀律 (虧損超過 10% 仍嚴格執行停損)" not in self.achievements:
                new_achievements.append("🏆 鐵血紀律 (虧損超過 10% 仍嚴格執行停損)")
                
        # 5. 韭菜王：買完立刻大跌
        if action == "b" and outcome_change < -5:
            if "💸 終極韭菜 (剛買完就遇上暴跌)" not in self.achievements:
                new_achievements.append("💸 終極韭菜 (剛買完就遇上暴跌)")
                
        for ach in new_achievements:
            self.achievements.add(ach)
            self._out(f"\n🌟 【解鎖成就！】：獲得徽章 {ach} 🌟")
            
    def _daily_lesson(self, week):
        self._out("\n💡 [ 今日財商進階課 ]")
        if week <= 3:
            stage_knowledge = [
                "📖 【什麼是股票？】\n   👉 大白話：買股票就是買下一家公司的一小部分。公司賺錢，你就分紅。",
                "📖 【手續費是隱形吸血鬼】\n   👉 大白話：每次交易券商都會收手續費，頻繁買賣會把本金吃光！",
            ]
        elif 4 <= week <= 7:
            stage_knowledge = [
                "📖 【什麼是 攤平 (Averaging Down)？】\n   👉 大白話：下跌時加碼買進，拉低平均買入成本。但爛公司越攤只會越平！",
                "📖 【心理學陷阱：處置效應】\n   👉 大白話：賺一點就急著賣，賠錢卻死抱著不賣。結果往往是『賺小錢、賠大錢』！",
            ]
        else:
            stage_knowledge = [
                "📖 【資產配置 (Asset Allocation)】\n   👉 大白話：把資金分成『進攻（股票）』和『防守（現金）』。現金是災難時的救命稻草。",
                "📖 【安全邊際 (Margin of Safety)】\n   👉 大白話：巴菲特買股票，一定會等打折才出手，這能保證就算看錯也不會受重傷。",
            ]
            
        self._out(random.choice(stage_knowledge))
        
        gurus_quotes = [
            "💬 巴菲特：『投資的第一條準則是不要賠錢；第二條準則是永遠不要忘記第一條。』",
            "💬 科斯托蘭尼：『投資就像坐計程車，你必須知道要去哪裡，否則只會白白花費車資。』",
        ]
        self._out(random.choice(gurus_quotes))
        self._out("═"*45)