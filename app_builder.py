from flask import Flask, render_template
from facebook_api import FacebookAPI

def create_app(api_client) -> Flask:
    """
    创建并配置Flask应用
    @param api_client: FacebookAPI实例
    @return: Flask应用实例
    """
    app = Flask(__name__)
    
    # 配置应用
    app.config.update(
        SECRET_KEY='dev',
        JSON_AS_ASCII=False
    )
    
    @app.route('/')
    def index():
        """渲染主页"""
        return render_template('index.html')
    
    return app 