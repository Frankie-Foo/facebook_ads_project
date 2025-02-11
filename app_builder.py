from flask import Flask, render_template
from facebook_api import FacebookAdsAPI

def create_app(fb_client: FacebookAdsAPI) -> Flask:
    """创建Flask应用"""
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        """渲染主页"""
        return render_template('index.html')
    
    return app 