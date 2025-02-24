"""
@file: main.py
@description: 主程序入口，用于协调和调用各个模块
"""

import os
import sys
from flask import Flask, jsonify, request, make_response
import uuid
from config import Config

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from app_builder import create_app
from facebook_api import FacebookAdsAPI
from chat import ChatManager

def main():
    """
    主程序入口函数
    """
    # 初始化Facebook API客户端
    fb_client = FacebookAdsAPI(
        access_token=Config.FB_ACCESS_TOKEN,
        ad_account_id=Config.AD_ACCOUNT_ID
    )
    
    # 创建Flask应用
    app = create_app(fb_client)
    app.config.from_object(Config)
    
    # 初始化聊天管理器，传入fb_client以便访问广告数据
    chat_manager = ChatManager(fb_client)
    
    @app.route('/api/detailed-insights')
    def get_detailed_insights():
        try:
            account_id = request.args.get('account')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            # 验证账户是否存在
            if account_id not in app.config['FB_AD_ACCOUNTS']:
                return jsonify({'error': '无效的账户ID'}), 400
            
            # 使用指定的账户ID获取数据
            data = fb_client.get_detailed_insights(
                start_date=start_date,
                end_date=end_date,
                account_id=account_id
            )
            
            return jsonify({
                'data': data.get('data', []),
                'date_range': {
                    'since': start_date or data.get('data', [{}])[0].get('date_start', ''),
                    'until': end_date or data.get('data', [{}])[-1].get('date_start', '')
                }
            })
            
        except Exception as e:
            print(f"获取数据失败: {str(e)}")
            return jsonify({
                'error': str(e)
            }), 500
    
    @app.route('/api/chat/send', methods=['POST'])
    def send_message():
        """发送聊天消息"""
        try:
            data = request.get_json()
            message = data.get('message')
            
            # 获取或创建 session_id
            session_id = request.cookies.get('session_id')
            if not session_id:
                session_id = str(uuid.uuid4())
            
            if not message:
                return jsonify({'error': '无效的消息'}), 400
                
            # 添加消息并获取回复
            message_data = chat_manager.add_message(session_id, message)
            
            # 创建响应
            response = jsonify({
                'success': True,
                'message': message_data
            })
            
            # 如果是新会话，设置 cookie
            if 'session_id' not in request.cookies:
                response.set_cookie('session_id', session_id, max_age=86400)  # 24小时有效
                
            return response
            
        except Exception as e:
            print(f"发送消息失败: {str(e)}")
            return jsonify({
                'error': str(e)
            }), 500
            
    @app.route('/api/chat/history')
    def get_chat_history():
        """获取聊天历史"""
        try:
            # 获取或创建 session_id
            session_id = request.cookies.get('session_id')
            if not session_id:
                session_id = str(uuid.uuid4())
                
            history = chat_manager.get_conversation(session_id)
            
            # 创建响应
            response = jsonify({
                'success': True,
                'history': history
            })
            
            # 如果是新会话，设置 cookie
            if 'session_id' not in request.cookies:
                response.set_cookie('session_id', session_id, max_age=86400)  # 24小时有效
                
            return response
            
        except Exception as e:
            print(f"获取历史记录失败: {str(e)}")
            return jsonify({
                'error': str(e)
            }), 500
    
    @app.after_request
    def add_security_headers(response):
        """添加安全相关的响应头"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    
    # 在 create_app 函数中添加
    app.jinja_env.variable_start_string = '[['
    app.jinja_env.variable_end_string = ']]'
    
    # 运行应用
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main() 