"""
@file: routes.py
@description: API路由定义
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from facebook_api import FacebookAdsAPI

router = APIRouter()
api = FacebookAdsAPI()

@router.get("/insights")
async def get_insights() -> Dict[str, Any]:
    """获取广告数据洞察"""
    try:
        data = api.get_campaign_insights()
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/account")
async def get_account_details() -> Dict[str, Any]:
    """获取账户详情"""
    try:
        data = api.get_ad_account_details()
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 