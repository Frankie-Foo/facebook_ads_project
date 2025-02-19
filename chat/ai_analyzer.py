"""AI分析器"""
from typing import Dict, List
import json
import requests
from datetime import datetime
from config import Config

class AIAnalyzer:
    def __init__(self):
        self.context = {}
        self.api_key = Config.DEEPSEEK_API_KEY
        self.api_url = Config.DEEPSEEK_API_URL
        
        # 系统提示词
        self.system_prompt = """
        你是一个专业的Facebook广告数据分析助手。你可以：
        1. 分析广告数据和趋势
        2. 提供优化建议
        3. 回答广告相关问题
        4. 生成数据报告
        请用简洁专业的中文回答。
        """
    
    def analyze_and_respond(self, message: str, conversation_history: List[Dict]) -> str:
        """使用Deepseek分析消息并生成回复"""
        try:
            # 构建对话历史
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # 添加历史对话记录
            for msg in conversation_history[-5:]:  # 只取最近5条记录
                role = "user" if msg['is_user'] else "assistant"
                messages.append({
                    "role": role,
                    "content": msg['content']
                })
            
            # 添加当前用户消息
            messages.append({
                "role": "user",
                "content": message
            })
            
            # 调用Deepseek API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": False,
                "api_version": "2024-02"  # 添加 API 版本
            }
            
            print("发送到 Deepseek 的请求:", json.dumps(data, ensure_ascii=False, indent=2))
            
            # 创建 Session 对象
            session = requests.Session()
            
            try:
                response = session.post(
                    self.api_url,
                    headers=headers,
                    json=data,
                    timeout=30,
                    verify=True   # 启用 SSL 验证
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("Deepseek API 响应:", json.dumps(result, ensure_ascii=False, indent=2))
                    return result['choices'][0]['message']['content']
                else:
                    error_msg = f"API调用失败: {response.status_code} - {response.text}"
                    print(error_msg)
                    return "抱歉，AI服务暂时不可用，请稍后再试。"
                    
            except requests.exceptions.RequestException as e:
                print(f"请求错误: {str(e)}")
                return "连接服务器时出现错误，请稍后再试。"
                
        except Exception as e:
            print(f"AI分析错误: {str(e)}")
            return "抱歉，我现在无法回答您的问题。请稍后再试。"
            
        finally:
            if 'session' in locals():
                session.close()
    
    def _analyze_data(self, data: Dict) -> str:
        """分析广告数据"""
        try:
            # 这里可以添加具体的数据分析逻辑
            total_spend = sum(float(item.get('spend', 0)) for item in data)
            total_clicks = sum(int(item.get('clicks', 0)) for item in data)
            total_impressions = sum(int(item.get('impressions', 0)) for item in data)
            
            analysis = f"""
            根据数据分析：
            1. 总支出：${total_spend:.2f}
            2. 总点击：{total_clicks}
            3. 总展示：{total_impressions}
            4. 平均点击成本：${(total_spend/total_clicks if total_clicks else 0):.2f}
            5. 点击率：{(total_clicks/total_impressions*100 if total_impressions else 0):.2f}%
            """
            
            return analysis
        except Exception as e:
            print(f"数据分析错误: {str(e)}")
            return "数据分析过程中出现错误。"
        
    def _generate_report(self, message: str) -> str:
        """生成数据报表"""
        # TODO: 集成报表生成逻辑
        return "已为您生成本周广告报表，主要指标都有明显提升。"
        
    def _general_response(self, message: str) -> str:
        """生成一般性回复"""
        return "我是您的广告助手，请问有什么可以帮您？" 