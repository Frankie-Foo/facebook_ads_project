"""
@file: main.py
@description: 主程序入口，用于协调和调用各个模块
"""

import os
import sys
from flask import Flask, jsonify, request, render_template
from facebook_api import FacebookAPI
from dotenv import load_dotenv

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from app_builder import create_app
from config import Config

app = Flask(__name__)

# 加载环境变量
load_dotenv()

# 初始化Facebook API客户端
api = FacebookAPI(
    access_token=os.getenv('FB_ACCESS_TOKEN'),
    app_id=os.getenv('FB_AD_ACCOUNT_ID'),
    app_secret=os.getenv('FB_APP_SECRET')
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/detailed-insights')
def get_detailed_insights():
    try:
        # 获取日期参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 调用 API 获取数据
        data = api.get_detailed_insights(start_date, end_date)
        
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
if os.getenv('VERCEL_ENV') == 'production':
    return app  # Vercel需要直接返回app对象
else:
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True) 