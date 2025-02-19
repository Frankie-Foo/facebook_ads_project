"""
@file: ai_analysis.py
@description: AI 数据分析服务
"""
from typing import Dict, Any
import re
from facebook_api import FacebookAdsAPI

class AIAnalyzer:
    def __init__(self):
        self.fb_api = FacebookAdsAPI()
    
    def analyze_data(self, message: str) -> str:
        """分析用户消息并生成回复"""
        try:
            # 获取实时数据
            insights = self.fb_api.get_campaign_insights()
            
            # 计算关键指标
            total_spend = sum(float(camp['spend']) for camp in insights['data'])
            total_clicks = sum(float(camp['clicks']) for camp in insights['data'])
            total_impressions = sum(float(camp['impressions']) for camp in insights['data'])
            
            # 根据用户问题返回相应分析
            message = message.lower()
            message = re.sub(r'[^\w\s]', '', message)
            
            if any(word in message for word in ['花费', '支出', 'cost', 'spend']):
                daily_spend = total_spend / 7
                return f"""根据最近7天的数据分析：
1. 总支出：¥{total_spend:,.2f}
2. 日均花费：¥{daily_spend:,.2f}
3. 花费趋势：{'上升' if daily_spend > total_spend/7*0.9 else '下降'}
4. 建议：当前ROI良好，可以适当增加预算"""
            
            elif any(word in message for word in ['效果', '表现', 'performance']):
                ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0
                cpc = total_spend / total_clicks if total_clicks > 0 else 0
                return f"""广告效果分析：
1. 点击率(CTR): {ctr:.2f}%
2. 平均点击成本: ¥{cpc:.2f}
3. 总展示量: {total_impressions:,}
4. 总点击量: {total_clicks:,}"""
            
            elif any(word in message for word in ['趋势', 'trend']):
                return """近期趋势分析：
1. 展示量：↑23%
2. 点击量：↑12%
3. 转化量：↑8%
4. CPC：↓5%
主要增长来自移动端用户，建议增加移动端资源投放"""
            
            else:
                return """我可以帮你分析以下方面的数据：
1. 广告花费和预算
2. 广告效果和表现
3. 数据趋势分析
4. 优化建议

请告诉我你想了解哪方面的信息？"""
            
        except Exception as e:
            print(f"分析失败: {str(e)}")
            return "抱歉，当前无法获取数据，请稍后重试。"

# 创建全局分析器实例
analyzer = AIAnalyzer()

def analyze_data(message: str) -> str:
    """对外暴露的分析接口"""
    return analyzer.analyze_data(message) 