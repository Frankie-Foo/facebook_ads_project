"""数据管理模块"""
import pandas as pd
from datetime import datetime, timedelta
import os
from typing import Dict
from facebook_api import FacebookAdsAPI

class DataManager:
    def __init__(self, fb_client: FacebookAdsAPI):
        self.fb_client = fb_client
        self.data_dir = "data"
        self.cached_data = None  # 用于存储数据
        self.ensure_data_dir()
        
    def ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_and_save_data(self):
        """获取并保存最近两个月的数据"""
        try:
            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=60)
            
            # 获取数据
            data = self.fb_client.get_detailed_insights(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            
            # 转换为DataFrame并保存
            if data and 'data' in data:
                df = pd.DataFrame(data['data'])
                
                # 保存为CSV
                filename = f"fb_ads_data_{datetime.now().strftime('%Y%m%d')}.csv"
                filepath = os.path.join(self.data_dir, filename)
                df.to_csv(filepath, index=False)
                
                return filepath
            
            return None
            
        except Exception as e:
            print(f"获取数据失败: {str(e)}")
            return None 

    def get_data_by_date(self, target_date: str) -> Dict:
        """获取指定日期的数据"""
        try:
            if self.cached_data is None:
                # 如果缓存为空，先加载数据
                self.load_cached_data()
            
            if self.cached_data is not None:
                df = pd.DataFrame(self.cached_data)
                # 解析日期
                df['date_start'] = pd.to_datetime(df['date_start'])
                
                # 获取目标日期的数据
                target_date = pd.to_datetime(target_date)
                daily_data = df[df['date_start'].dt.date == target_date.date()]
                
                # 获取上月同期数据
                last_month_date = target_date - pd.DateOffset(months=1)
                last_month_data = df[df['date_start'].dt.date == last_month_date.date()]
                
                if not daily_data.empty:
                    result = {
                        'current': daily_data.to_dict('records')[0],
                        'last_month': last_month_data.to_dict('records')[0] if not last_month_data.empty else None,
                        'date': target_date.strftime('%Y-%m-%d')
                    }
                    return result
            
            return None
            
        except Exception as e:
            print(f"获取日期数据失败: {str(e)}")
            return None

    def load_cached_data(self):
        """加载缓存数据"""
        try:
            latest_file = self._get_latest_data_file()
            if latest_file:
                df = pd.read_csv(latest_file)
                self.cached_data = df.to_dict('records')
        except Exception as e:
            print(f"加载缓存数据失败: {str(e)}")

    def _get_latest_data_file(self) -> str:
        """获取最新的数据文件"""
        try:
            files = [f for f in os.listdir(self.data_dir) if f.startswith('fb_ads_data_')]
            if files:
                latest = max(files)
                return os.path.join(self.data_dir, latest)
            return None
        except Exception as e:
            print(f"获取最新数据文件失败: {str(e)}")
            return None 

    def get_trend_data(self, days: int = 30) -> Dict:
        """获取趋势数据"""
        try:
            if self.cached_data is None:
                self.load_cached_data()
            
            if self.cached_data is not None:
                df = pd.DataFrame(self.cached_data)
                df['date_start'] = pd.to_datetime(df['date_start'])
                
                # 获取最近N天的数据
                end_date = df['date_start'].max()
                start_date = end_date - pd.Timedelta(days=days)
                mask = (df['date_start'] >= start_date) & (df['date_start'] <= end_date)
                trend_data = df[mask].sort_values('date_start')
                
                return {
                    'dates': trend_data['date_start'].dt.strftime('%Y-%m-%d').tolist(),
                    'spend': trend_data['spend'].tolist(),
                    'clicks': trend_data['clicks'].tolist(),
                    'impressions': trend_data['impressions'].tolist(),
                    'ctr': (trend_data['clicks'] / trend_data['impressions'] * 100).tolist()
                }
            
            return None
            
        except Exception as e:
            print(f"获取趋势数据失败: {str(e)}")
            return None 