import requests
import json
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from config import Config
import traceback

class FacebookAPIError(Exception):
    """Facebook API 错误类"""
    pass

class FacebookAdsAPI:
    """Facebook广告API客户端类"""
    
    API_VERSION = "v22.0"  # 使用最新的API版本
    
    # API错误代码映射
    ERROR_CODES = {
        1: "API未知错误",
        2: "服务暂时不可用",
        4: "应用请求次数限制",
        17: "用户请求次数限制",
        10: "应用权限不足",
        190: "访问令牌无效",
        200: "权限错误",
        294: "广告账户被禁用"
    }
    
    def __init__(self, access_token=None, ad_account_id=None):
        """
        初始化API客户端
        @param access_token: API访问令牌
        @param ad_account_id: 广告账户ID
        """
        self.base_url = Config.FB_API_BASE_URL
        self.api_version = Config.FB_API_VERSION
        self.default_access_token = access_token
        self.default_account_id = ad_account_id
        self.timeout = Config.REQUEST_TIMEOUT
        self.proxies = Config.PROXIES
        
        # 验证访问令牌
        self._validate_token()

    def _validate_token(self):
        """验证访问令牌"""
        try:
            endpoint = f"{self.base_url}/debug_token"
            params = {
                "input_token": self.default_access_token,
                "access_token": self.default_access_token
            }
            
            # 增加重试次数
            max_retries = 3
            for i in range(max_retries):
                try:
                    response = self._make_request("GET", endpoint, params)
                    if "error" not in response:
                        return True
                    time.sleep(1)  # 重试前等待1秒
                except Exception as e:
                    if i == max_retries - 1:  # 最后一次重试
                        print(f"Token验证失败: {str(e)}")
                        return False
                    continue
            
            return True
            
        except Exception as e:
            print(f"Token验证出错: {str(e)}")
            return False

    def _handle_error(self, error_data: Dict) -> Dict:
        """
        处理API错误
        @param error_data: 错误数据
        @return: 格式化的错误信息
        """
        error_code = error_data.get("code", 1)
        error_message = error_data.get("message", "未知错误")
        error_subcode = error_data.get("error_subcode")
        
        error_type = self.ERROR_CODES.get(error_code, "未知错误类型")
        
        return {
            "error": {
                "code": error_code,
                "type": error_type,
                "message": error_message,
                "subcode": error_subcode
            }
        }

    def _make_request(self, method: str, endpoint: str, params: Dict, 
                     files: Optional[Dict] = None) -> Dict[str, Any]:
        """
        执行API请求
        @param method: HTTP方法
        @param endpoint: API端点
        @param params: 请求参数
        @param files: 文件上传（可选）
        @return: API响应
        """
        try:
            print(f"Request URL: {endpoint}")
            print(f"Parameters: {json.dumps(params, indent=2)}")
            
            # 添加调试模式参数
            params["debug"] = "all"
            
            response = requests.request(
                method=method,
                url=endpoint,
                params=params if method == "GET" else None,
                data=params if method != "GET" and not files else None,
                files=files,
                timeout=self.timeout,
                proxies=self.proxies
            )
            
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            if 'error' in response_data:
                return self._handle_error(response_data['error'])
                
            return response_data
            
        except requests.exceptions.Timeout:
            return {"error": {"code": -1, "type": "超时", "message": "请求超时"}}
        except requests.exceptions.ConnectionError:
            return {"error": {"code": -2, "type": "连接错误", "message": "网络连接错误"}}
        except Exception as e:
            return {"error": {"code": -3, "type": "未知错误", "message": str(e)}}

    def get_object(self, object_id: str, fields: List[str]) -> Dict[str, Any]:
        """
        获取任意对象的数据
        @param object_id: 对象ID
        @param fields: 需要获取的字段列表
        @return: 对象数据
        """
        endpoint = f"{self.base_url}/{object_id}"
        params = {
            "access_token": self.default_access_token,
            "fields": ",".join(fields)
        }
        
        return self._make_request("GET", endpoint, params)

    def create_object(self, parent_id: str, edge: str, data: Dict) -> Dict[str, Any]:
        """
        创建新对象
        @param parent_id: 父对象ID
        @param edge: 边名称
        @param data: 创建数据
        @return: 创建结果
        """
        endpoint = f"{self.base_url}/{parent_id}/{edge}"
        params = {
            "access_token": self.default_access_token,
            **data
        }
        
        return self._make_request("POST", endpoint, params)

    def update_object(self, object_id: str, data: Dict) -> Dict[str, Any]:
        """
        更新对象
        @param object_id: 对象ID
        @param data: 更新数据
        @return: 更新结果
        """
        endpoint = f"{self.base_url}/{object_id}"
        params = {
            "access_token": self.default_access_token,
            **data
        }
        
        return self._make_request("POST", endpoint, params)

    def delete_object(self, object_id: str) -> Dict[str, Any]:
        """
        删除对象
        @param object_id: 对象ID
        @return: 删除结果
        """
        endpoint = f"{self.base_url}/{object_id}"
        params = {
            "access_token": self.default_access_token
        }
        
        return self._make_request("DELETE", endpoint, params)

    def upload_file(self, parent_id: str, edge: str, file_path: str, 
                   file_type: str) -> Dict[str, Any]:
        """
        上传文件
        @param parent_id: 父对象ID
        @param edge: 边名称
        @param file_path: 文件路径
        @param file_type: 文件类型
        @return: 上传结果
        """
        endpoint = f"{self.base_url}/{parent_id}/{edge}"
        
        with open(file_path, 'rb') as f:
            files = {
                'source': (file_path, f, f'image/{file_type}')
            }
            
            params = {
                "access_token": self.default_access_token
            }
            
            return self._make_request("POST", endpoint, params, files=files)

    def get_ad_account_details(self) -> Dict[str, Any]:
        """
        获取广告账户详细信息
        @return: 广告账户信息
        """
        fields = [
            "account_id",
            "account_status",
            "balance",
            "currency",
            "name",
            "timezone_name",
            "funding_source_details"
        ]
        
        endpoint = f"{self.base_url}/act_{self.default_account_id}"
        params = {
            "access_token": self.default_access_token,
            "fields": ",".join(fields)
        }
        
        return self._make_request("GET", endpoint, params)

    def get_campaign_insights(self, campaign_id: str, date_range: Optional[Dict] = None) -> Dict[str, Any]:
        """
        获取单个广告系列的详细数据
        @param campaign_id: 广告系列ID
        @param date_range: 可选的日期范围
        @return: 广告系列数据
        """
        fields = [
            "campaign_name",
            "spend",
            "impressions",
            "clicks",
            "reach",
            "frequency",
            "cpc",  # 每次点击成本
            "cpm",  # 千次展示成本
            "ctr",  # 点击率
            "objective",  # 广告目标
            "buying_type",  # 购买类型
            "daily_budget",  # 每日预算
            "lifetime_budget"  # 总预算
        ]
        
        endpoint = f"{self.base_url}/{campaign_id}/insights"
        params = {
            "access_token": self.default_access_token,
            "fields": ",".join(fields),
            "level": "campaign"
        }
        
        if date_range:
            params["time_range"] = json.dumps(date_range)
            
        return self._make_request("GET", endpoint, params)

    def get_adsets(self, campaign_id: str) -> Dict[str, Any]:
        """
        获取广告系列下的广告组
        @param campaign_id: 广告系列ID
        @return: 广告组列表
        """
        fields = [
            "name",
            "status",
            "daily_budget",
            "lifetime_budget",
            "targeting",  # 定向设置
            "bid_strategy",  # 出价策略
            "billing_event",  # 计费事件
            "optimization_goal"  # 优化目标
        ]
        
        endpoint = f"{self.base_url}/{campaign_id}/adsets"
        params = {
            "access_token": self.default_access_token,
            "fields": ",".join(fields)
        }
        
        return self._make_request("GET", endpoint, params)

    def get_ads(self, adset_id: str) -> Dict[str, Any]:
        """
        获取广告组下的广告
        @param adset_id: 广告组ID
        @return: 广告列表
        """
        fields = [
            "name",
            "status",
            "creative",  # 创意信息
            "tracking_specs",  # 跟踪规范
            "bid_amount",  # 出价金额
            "configured_status"  # 配置状态
        ]
        
        endpoint = f"{self.base_url}/{adset_id}/ads"
        params = {
            "access_token": self.default_access_token,
            "fields": ",".join(fields)
        }
        
        return self._make_request("GET", endpoint, params)

    def make_batch_request(self, batch_requests: List[Dict]) -> List[Dict]:
        """
        执行批量请求
        @param batch_requests: 批量请求列表
        @return: 批量响应列表
        """
        endpoint = f"{self.base_url}/"
        
        # 准备批量请求数据
        data = {
            'access_token': self.default_access_token,
            'batch': json.dumps(batch_requests),
            'include_headers': 'false'  # 不包含响应头以提高效率
        }
        
        try:
            print(f"Batch Request URL: {endpoint}")
            print(f"Batch Requests: {json.dumps(batch_requests, indent=2)}")
            
            response = requests.post(
                endpoint,
                data=data,
                timeout=self.timeout,
                proxies=self.proxies
            )
            
            response_data = response.json()
            print(f"Batch Response: {json.dumps(response_data, indent=2)}")
            
            # 处理批量响应
            results = []
            for item in response_data:
                if item is None:
                    results.append({"error": "Request timeout or failed"})
                    continue
                    
                if item.get('code') != 200:
                    results.append(json.loads(item.get('body', '{}')))
                    continue
                    
                results.append(json.loads(item.get('body', '{}')))
            
            return results
            
        except Exception as e:
            print(f"Batch Request Error: {str(e)}")
            return [{"error": str(e)}] * len(batch_requests)

    def get_multiple_insights(self, date_ranges: List[Dict[str, str]]) -> List[Dict]:
        """
        批量获取多个日期范围的广告数据
        @param date_ranges: 日期范围列表，每个元素包含 since 和 until
        @return: 多个日期范围的数据列表
        """
        batch_requests = []
        
        for date_range in date_ranges:
            # 构建单个请求
            request = {
                "method": "GET",
                "relative_url": f"act_{self.default_account_id}/insights"
                               f"?fields=spend,impressions,clicks,reach,inline_link_clicks"
                               f"&time_range={json.dumps(date_range)}"
                               f"&level=account"
            }
            batch_requests.append(request)
        
        return self.make_batch_request(batch_requests)

    def get_account_and_campaign_insights(self) -> Dict[str, Any]:
        """
        同时获取账户和广告系列数据
        @return: 包含账户和广告系列数据的字典
        """
        # 计算日期范围
        end_date = datetime.now() - timedelta(days=2)
        time_range = {
            "since": end_date.strftime("%Y-%m-%d"),
            "until": end_date.strftime("%Y-%m-%d")
        }
        
        # 构建批量请求
        batch_requests = [
            {
                "method": "GET",
                "relative_url": f"act_{self.default_account_id}/insights"
                               f"?fields=spend,impressions,clicks,reach,inline_link_clicks"
                               f"&time_range={json.dumps(time_range)}"
                               f"&level=account"
            },
            {
                "method": "GET",
                "relative_url": f"act_{self.default_account_id}/campaigns"
                               f"?fields=name,objective,status,lifetime_budget"
            }
        ]
        
        results = self.make_batch_request(batch_requests)
        
        return {
            "account_insights": results[0] if not isinstance(results[0], dict) or 'error' not in results[0] else [],
            "campaigns": results[1] if not isinstance(results[1], dict) or 'error' not in results[1] else []
        }

    def get_detailed_insights(self, start_date, end_date, account_id=None):
        """
        获取指定账户的广告数据
        """
        # 使用传入的account_id或默认账户
        current_account_id = account_id or self.default_account_id
        
        # 使用统一的access_token
        access_token = self.default_access_token
        
        endpoint = f"{self.base_url}/act_{current_account_id}/insights"
        
        # 修复字段和时间范围参数的格式
        params = {
            'access_token': access_token,
            'level': 'account',
            'fields': 'spend,impressions,clicks,ctr,cpc,actions,action_values,inline_link_clicks,inline_link_click_ctr',  # 改为逗号分隔的字符串
            'time_range': json.dumps({  # 使用 json.dumps 序列化时间范围
                'since': start_date,
                'until': end_date
            }),
            'time_increment': 1
        }
        
        try:
            print(f"Request URL: {endpoint}")
            print(f"Request params: {params}")  # 添加日志
            
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            print(f"Response: {response.text}")  # 添加日志
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {str(e)}")
            print(f"Response content: {e.response.text if hasattr(e, 'response') else 'No response'}")  # 添加错误响应内容
            raise 