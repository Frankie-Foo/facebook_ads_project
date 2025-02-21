"""聊天管理器"""
from typing import Dict, List
import json
from datetime import datetime
from .ai_analyzer import AIAnalyzer

class ChatManager:
    def __init__(self, fb_client=None):
        self.conversations: Dict[str, List[Dict]] = {}  # 存储会话历史
        self.ai_analyzer = AIAnalyzer()
        self.fb_client = fb_client
    
    def add_message(self, session_id: str, message: str, is_user: bool = True) -> Dict:
        """添加新消息并获取AI回复"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        # 记录用户消息
        message_data = {
            'content': message,
            'timestamp': datetime.now().isoformat(),
            'is_user': is_user
        }
        self.conversations[session_id].append(message_data)
        
        # 如果是用户消息，使用AI分析并生成回复
        if is_user:
            try:
                # 获取AI回复
                ai_response = self.ai_analyzer.analyze_and_respond(
                    message,
                    self.conversations[session_id]
                )
                
                # 记录AI回复
                ai_message = {
                    'content': ai_response,
                    'timestamp': datetime.now().isoformat(),
                    'is_user': False
                }
                self.conversations[session_id].append(ai_message)
                return ai_message
                
            except Exception as e:
                print(f"处理消息错误: {str(e)}")
                error_message = "抱歉，处理您的请求时出现错误。"
                error_data = {
                    'content': error_message,
                    'timestamp': datetime.now().isoformat(),
                    'is_user': False
                }
                self.conversations[session_id].append(error_data)
                return error_data
        
        return message_data
    
    def get_conversation(self, session_id: str) -> List[Dict]:
        """获取会话历史"""
        return self.conversations.get(session_id, []) 