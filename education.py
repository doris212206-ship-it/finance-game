import random

class FinancialAdvisor:
    def __init__(self):
        self.fiq_score = 100
        self.consecutive_buy = 0
        self.consecutive_sell = 0
        self.current_week = 0
        
        # 狀態追蹤
        self.last_action = None       # "b", "s", "n"
        self.last_price = 0
        self.achievements = set()     # 用 set 避免重複獲得
        
        self.ui_mode = False
        self.logs = []

    def _out(self, msg):
        self.logs.append(msg)
        if not self.ui_mode:
            print(msg)
            
    def evaluate(self, action, current_price, prev_price, avg_price, ma10_price, cash, total_asset, stock, ui_mode=False):
        self.ui_mode = ui_mode
        self.logs = []
        
        self.current_week += 1
        week = self.current_week
        
        if prev_price == 0:
            prev_price = current_price
            
        change_percent = ((current_price - prev_price) / prev_price) * 100
        
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
        self._out(f"📚 【 財商導師 - 第 {week} 週盤後教室 】 (新手理財積分: {self.fiq_score} 分)")
        self._out("═"*45)

        # 1. 市場環境分析
        self._analyze_market(change_percent)
        
        # 2. 因果回饋 (Cause & Effect)
        self._cause_and_effect(current_price, change_percent)
        
        # 3. 玩家行為診斷 (加入成本與均線邏輯)
        self._diagnose_action(action, current_price, prev_price, avg_price, ma10_price, change_percent)
        
        # 4. 錢包安全診斷
        self._check_wallet(cash, total_asset)
        
        # 5. 徽章成就檢查
        self._check_achievements(action, current_price, avg_price, change_percent, stock)
        
        # 6. 今日財商進階課
        self._daily_lesson(week)
        
        # 更新上一週的紀錄
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
            
    def _cause_and_effect(self, current_price, change_percent):
        if self.last_action is None:
            return
            
        self._out("\n🔄 [ 跨週回顧：上週的決定對了嗎？ ]")
        if self.last_action == "b":
            if change_percent < -3:
                self._out("💥 導師碎碎念：你上週才剛買進，結果這週就迎來大跌！如果上週是追高，這就是 FOMO 嚐到的苦果啊！")
                self.fiq_score -= 2
            elif change_percent > 3:
                self._out("✨ 導師稱讚：你上週大膽買進，這週立刻享受大漲的獲利，眼光精準！")
                self.fiq_score += 2
            else:
                self._out("⚖️ 導師碎碎念：上週買進後，目前市場還沒表態，繼續耐心等待吧。")
        elif self.last_action == "s":
            if change_percent < -3:
                self._out("🛡️ 導師稱讚：太神啦！你上週剛賣掉，這週就暴跌。這波『完美閃避』幫你省下了一大筆錢！")
                self.fiq_score += 3
            elif change_percent > 3:
                self._out("😅 導師碎碎念：上週才賣，結果這週大漲，是不是覺得有點可惜（俗稱賣飛）？但記住，賺進口袋的才是錢，不要太在意沒賺到的！")
            else:
                self._out("⚖️ 導師碎碎念：上週賣出後市場平靜，是不錯的防守策略。")
                
    def _diagnose_action(self, action, current_price, prev_price, avg_price, ma10_price, change_percent):
        self._out("\n🎯 [ 本週操作行為診斷 ]")
        fiq_change = 0
        
        if action == "b":
            self._out(f"🛒 你的行動：買入股票 (已連續買入 {self.consecutive_buy} 週)")
            
            # 使用均線與平均成本來判斷
            if current_price > ma10_price * 1.05:
                # 乖離過大還買
                self._out("⚠️ 專業術語：【嚴重追高 / FOMO】")
                self._out("💡 大白話：現在股價已經遠高於近期 10 天的平均價，你還衝進去買！這就像去熱門餐廳排隊買黃牛票，非常危險！")
                fiq_change -= 2
            elif avg_price > 0 and current_price < avg_price:
                # 真正意義上的攤平
                self._out("💡 專業術語：【逢低攤平 (Averaging Down)】")
                self._out("💡 大白話：股價低於你的平均成本，你選擇趁打折多買一點來拉低整體成本。只要公司不會倒，這是戰勝恐懼的好策略！")
                fiq_change += 2
            elif current_price > prev_price:
                self._out("⚠️ 專業術語：【右側交易 / 動能追價】")
                self._out("💡 大白話：看到股價漲就跟著買。順勢交易是OK的，但要注意有沒有買在最高點的風險。")
                fiq_change -= 1
            else:
                self._out("✅ 專業術語：【逢低佈局】")
                self._out("💡 大白話：趁著這週沒怎麼漲，穩穩地佈局買進，有耐心！")
                fiq_change += 1
                
        elif action == "s":
            self._out(f"💰 你的行動：賣出股票 (已連續賣出 {self.consecutive_sell} 週)")
            
            if avg_price > 0 and current_price > avg_price:
                if self.consecutive_sell >= 2:
                    self._out("✅ 專業術語：【分批停利 / 階梯式獲利】")
                    self._out("💡 大白話：股票賺錢了，你選擇分批慢慢賣。這能讓你既保住獲利，又能享受如果繼續漲的紅利，非常成熟！")
                    fiq_change += 3
                else:
                    self._out("✅ 專業術語：【獲利了結 / 停利】")
                    self._out("💡 大白話：恭喜賺錢！把螢幕上的數字變成口袋裡的真鈔，落袋為安永遠是對的。")
                    fiq_change += 2
            elif avg_price > 0 and current_price < avg_price:
                self._out("⚠️ 專業術語：【執行停損 / 割肉】")
                self._out("💡 大白話：雖然這筆交易賠錢了，但及時認錯賣出，可以防止虧損繼續擴大。『留得青山在，不怕沒柴燒』。")
                fiq_change += 1
            else:
                self._out("⚠️ 專業術語：【清倉】")
                self._out("💡 大白話：將手中的持股賣出換回現金。")
                
        elif action == "n":
            self._out("⏳ 你的行動：不買也不賣（空倉/抱牢觀望）")
            if abs(change_percent) > 5:
                self._out("📘 專業術語：【以靜制動 / 抱緊處理】")
                self._out("💡 大白話：市場波動劇烈，但你選擇不亂動。減少無謂的交易摩擦，也是一種實力的展現。")
                fiq_change += 2
            else:
                self._out("💡 大白話：市場沒行情，你選擇省下手續費去喝杯咖啡，很棒。")
                fiq_change += 1
        else:
            self._out("❌ 收到無效指令")
            fiq_change -= 1
            
        self.fiq_score += fiq_change
        
    def _check_wallet(self, cash, total_asset):
        self._out("\n🚨 [ 錢包安全診斷 ]")
        if cash < 15000:
            self._out("⚠️ 【流動性危機】：現金太少！萬一遇到壞事件扣錢，你會陷入危機，甚至被迫低價賣掉股票。")
            self.fiq_score -= 2
        elif total_asset > 0 and cash > total_asset * 0.8:
            self._out("💵 【資金閒置】：你的現金佔比太高了。這很安全，但也代表你錯失了讓資產跟著市場翻倍的機會。")
        else:
            self._out("💚 【黃金比例】：現金與股票比例適中，攻守兼備！")
            
    def _check_achievements(self, action, current_price, avg_price, change_percent, stock):
        new_achievements = []
        
        # 1. 鑽石手：帳面虧損嚴重但死不賣 (或攤平)
        if stock > 0 and avg_price > 0 and current_price < avg_price * 0.8 and action != "s":
            if "💎 鑽石手 (承受 -20% 虧損仍抱緊)" not in self.achievements:
                new_achievements.append("💎 鑽石手 (承受 -20% 虧損仍抱緊)")
                
        # 2. 神槍手：在大跌時勇敢買進
        if action == "b" and change_percent < -5:
            if "🎯 危機入市 (在大跌超過 5% 時買進)" not in self.achievements:
                new_achievements.append("🎯 危機入市 (在大跌超過 5% 時買進)")
                
        # 3. 跑得快：完美躲避暴跌 (透過 cause_and_effect 判斷)
        if self.last_action == "s" and change_percent < -5:
            if "🏃 神機妙算 (在暴跌前一週成功賣出逃頂)" not in self.achievements:
                new_achievements.append("🏃 神機妙算 (在暴跌前一週成功賣出逃頂)")
                
        # 4. 韭菜王：高點買，這週跌
        if self.last_action == "b" and change_percent < -5:
            if "💸 終極韭菜 (剛買完就遇上暴跌)" not in self.achievements:
                new_achievements.append("💸 終極韭菜 (剛買完就遇上暴跌)")
                
        for ach in new_achievements:
            self.achievements.add(ach)
            self._out(f"\n🌟 【解鎖成就！】：獲得徽章 {ach} 🌟")
            self.fiq_score += 5 # 給予獎勵分數
            
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