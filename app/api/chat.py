"""
@file: chat.py
@description: AI 聊天接口
"""
from flask import Blueprint, request, jsonify
from app.services.ai_analysis import analyze_data

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        message = request.json.get('message')
        if not message:
            return jsonify({
                'success': False,
                'error': '消息不能为空'
            }), 400
            
        response = analyze_data(message)
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 