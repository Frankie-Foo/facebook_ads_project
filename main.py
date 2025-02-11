"""
@file: main.py
@description: 主程序入口，用于协调和调用各个模块
"""

import os
import sys
from flask import Flask, jsonify, request

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from app_builder import create_app
from config import Config
from facebook_api import FacebookAdsAPI

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
    
    @app.route('/api/detailed-insights')
    def get_detailed_insights():
        try:
            # 获取日期参数
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            # 调用 API 获取数据
            data = fb_client.get_detailed_insights(start_date, end_date)
            
            return jsonify({
                'data': data.get('data', []),
                'date_range': {
                    'since': start_date or data.get('data', [{}])[0].get('date_start', ''),
                    'until': end_date or data.get('data', [{}])[-1].get('date_start', '')
                }
            })
            
        except Exception as e:
            return jsonify({
                'error': str(e)
            }), 500
    
    @app.after_request
    def add_security_headers(response):
        """添加安全相关的响应头"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    
    # 运行应用
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main() 