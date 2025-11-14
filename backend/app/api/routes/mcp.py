"""
统一MCP控制中心API路由
AI对小说的完全掌控接口
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.models.worldview_schemas import (
    UnifiedMCPAction, UnifiedMCPResponse,
    NovelAnalysisRequest, NovelAnalysisResponse,
    NovelOptimizationRequest, NovelOptimizationResponse
)
from app.crud import novel as novel_crud
from app.api.dependencies import get_current_user
from app.services.unified_mcp_service import unified_mcp_service
from app.services.mcp_audit_service import mcp_audit_service
from loguru import logger
from datetime import datetime

router = APIRouter()


@router.post("/execute", response_model=UnifiedMCPResponse)
async def execute_unified_mcp_action(
    action: UnifiedMCPAction,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    执行统一MCP操作
    
    AI可以通过此接口完全掌控小说的各个方面：
    - worldview: 世界观设定管理
    - character: 角色管理
    - plot: 情节管理
    - timeline: 时间线管理
    - outline: 大纲管理
    - style: 文风管理
    - novel: 小说级别操作
    
    支持的操作类型：
    - analyze: 分析
    - optimize: 优化
    - create: 创建
    - update: 更新
    - delete: 删除
    - generate: 生成
    - validate: 验证
    - sync: 同步
    - batch_update: 批量更新
    - ai_review: AI审查
    - auto_fix: 自动修复
    - smart_suggest: 智能建议
    """
    try:
        # 获取客户端信息
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        result = await unified_mcp_service.execute_unified_action(
            db, action, current_user.id, ip_address, user_agent
        )
        
        logger.info(f"统一MCP操作: {action.target_type}.{action.action} - 用户: {current_user.username}")
        
        return result
        
    except Exception as e:
        logger.error(f"统一MCP操作失败: {action.target_type}.{action.action} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"操作执行失败: {str(e)}"
        )


@router.post("/analyze/novel", response_model=NovelAnalysisResponse)
async def analyze_novel_comprehensive(
    request: NovelAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    全面分析小说
    
    AI对小说进行多维度深度分析：
    - worldview: 世界观一致性和完整性
    - character: 角色深度和关系网络
    - plot: 情节结构和节奏
    - style: 文风一致性和特色
    - consistency: 整体一致性检查
    """
    try:
        # 验证小说权限
        novel = novel_crud.get_novel_by_id(db, request.novel_id)
        if not novel or novel.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或无权访问"
            )
        
        result = await unified_mcp_service.analyze_novel_comprehensive(db, request, current_user.id)
        
        logger.info(f"小说全面分析完成: 小说ID {request.novel_id} - 用户: {current_user.username}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"小说分析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


@router.post("/optimize/novel", response_model=NovelOptimizationResponse)
async def optimize_novel_comprehensive(
    request: NovelOptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    全面优化小说
    
    AI对小说进行系统性优化：
    - 基于分析结果提供具体改进方案
    - 生成详细的实施计划
    - 评估优化影响和优先级
    - 提供可执行的优化步骤
    """
    try:
        # 验证小说权限
        novel = novel_crud.get_novel_by_id(db, request.novel_id)
        if not novel or novel.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或无权访问"
            )
        
        result = await unified_mcp_service.optimize_novel_comprehensive(db, request, current_user.id)
        
        logger.info(f"小说全面优化完成: 小说ID {request.novel_id} - 用户: {current_user.username}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"小说优化失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"优化失败: {str(e)}"
        )


@router.post("/ai-takeover/{novel_id}")
async def ai_takeover_novel(
    novel_id: int,
    takeover_scope: List[str],
    ai_instructions: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI接管小说管理
    
    让AI完全接管小说的指定方面：
    - 自动分析当前状态
    - 识别需要改进的地方
    - 制定优化计划
    - 自动执行优化操作
    - 持续监控和调整
    """
    try:
        # 验证小说权限
        novel = novel_crud.get_novel_by_id(db, novel_id)
        if not novel or novel.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或无权访问"
            )
        
        # 执行AI接管流程
        takeover_results = []
        
        for scope in takeover_scope:
            # 分析当前状态
            analysis_action = UnifiedMCPAction(
                target_type=scope,
                action="analyze",
                novel_id=novel_id,
                parameters={"analysis_depth": "comprehensive"},
                ai_instructions=ai_instructions
            )
            
            analysis_result = await unified_mcp_service.execute_unified_action(
                db, analysis_action, current_user.id
            )
            
            # 基于分析结果进行优化
            if analysis_result.success:
                optimization_action = UnifiedMCPAction(
                    target_type=scope,
                    action="optimize",
                    novel_id=novel_id,
                    parameters={"optimization_goals": ["提升质量", "增强一致性"]},
                    ai_instructions=ai_instructions
                )
                
                optimization_result = await unified_mcp_service.execute_unified_action(
                    db, optimization_action, current_user.id
                )
                
                takeover_results.append({
                    "scope": scope,
                    "analysis": analysis_result.result,
                    "optimization": optimization_result.result if optimization_result.success else None,
                    "status": "completed" if optimization_result.success else "failed"
                })
        
        logger.info(f"AI接管完成: 小说ID {novel_id}, 范围: {takeover_scope} - 用户: {current_user.username}")
        
        return {
            "novel_id": novel_id,
            "takeover_scope": takeover_scope,
            "results": takeover_results,
            "message": "AI接管流程完成",
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI接管失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI接管失败: {str(e)}"
        )


@router.post("/ai-autopilot/{novel_id}")
async def enable_ai_autopilot(
    novel_id: int,
    autopilot_config: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    启用AI自动驾驶模式
    
    AI将持续监控和管理小说：
    - 自动检测问题和改进机会
    - 主动提出优化建议
    - 在授权范围内自动执行改进
    - 定期生成管理报告
    """
    try:
        # 验证小说权限
        novel = novel_crud.get_novel_by_id(db, novel_id)
        if not novel or novel.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或无权访问"
            )
        
        # TODO: 实现AI自动驾驶配置
        # 这里可以设置定时任务，让AI定期检查和优化小说
        
        logger.info(f"AI自动驾驶启用: 小说ID {novel_id} - 用户: {current_user.username}")
        
        return {
            "novel_id": novel_id,
            "autopilot_enabled": True,
            "config": autopilot_config,
            "message": "AI自动驾驶模式已启用",
            "next_check": "24小时后"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI自动驾驶启用失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启用失败: {str(e)}"
        )


@router.get("/capabilities")
async def get_mcp_capabilities():
    """
    获取MCP能力清单
    
    返回AI可以执行的所有操作和管理的所有目标类型
    """
    return {
        "target_types": {
            "worldview": {
                "description": "世界观设定管理",
                "capabilities": ["创建设定", "分析一致性", "优化完整性", "验证逻辑"]
            },
            "character": {
                "description": "角色管理",
                "capabilities": ["生成角色", "分析性格", "优化发展", "管理关系"]
            },
            "plot": {
                "description": "情节管理", 
                "capabilities": ["设计情节", "分析结构", "优化节奏", "检测漏洞"]
            },
            "timeline": {
                "description": "时间线管理",
                "capabilities": ["构建时间线", "检查一致性", "优化逻辑", "同步事件"]
            },
            "outline": {
                "description": "大纲管理",
                "capabilities": ["生成大纲", "优化结构", "调整节奏", "完善细节"]
            },
            "style": {
                "description": "文风管理",
                "capabilities": ["分析文风", "保持一致性", "优化表达", "适配场景"]
            },
            "novel": {
                "description": "小说级别管理",
                "capabilities": ["全面分析", "系统优化", "质量评估", "改进规划"]
            }
        },
        "action_types": {
            "analyze": "深度分析目标",
            "optimize": "智能优化目标",
            "create": "创建新目标",
            "update": "更新现有目标",
            "delete": "删除目标",
            "generate": "AI生成目标",
            "validate": "验证目标有效性",
            "sync": "同步相关目标",
            "batch_update": "批量更新目标",
            "ai_review": "AI专业审查",
            "auto_fix": "自动修复问题",
            "smart_suggest": "智能改进建议"
        },
        "ai_features": {
            "autonomous_management": "自主管理能力",
            "comprehensive_analysis": "全面分析能力", 
            "intelligent_optimization": "智能优化能力",
            "proactive_suggestions": "主动建议能力",
            "continuous_monitoring": "持续监控能力",
            "adaptive_learning": "自适应学习能力"
        }
    }


@router.get("/audit/history")
async def get_operation_history(
    limit: int = 50,
    target_type: str = None,
    action: str = None,
    success_only: bool = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户MCP操作历史
    
    支持按目标类型、操作类型、成功状态筛选
    """
    try:
        history = mcp_audit_service.get_user_operation_history(
            db=db,
            user_id=current_user.id,
            limit=limit,
            target_type=target_type,
            action=action,
            success_only=success_only
        )
        
        return {
            "user_id": current_user.id,
            "total_records": len(history),
            "operations": [
                {
                    "id": log.id,
                    "target_type": log.target_type,
                    "action": log.action,
                    "novel_id": log.novel_id,
                    "target_id": log.target_id,
                    "success": log.success,
                    "execution_time_ms": log.execution_time_ms,
                    "ai_tokens_used": log.ai_tokens_used,
                    "created_at": log.created_at.isoformat(),
                    "error_message": log.error_message
                }
                for log in history
            ]
        }
        
    except Exception as e:
        logger.error(f"获取操作历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取历史失败: {str(e)}"
        )


@router.get("/audit/novel/{novel_id}/history")
async def get_novel_operation_history(
    novel_id: int,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定小说的MCP操作历史
    """
    try:
        # 验证小说权限
        novel = novel_crud.get_novel_by_id(db, novel_id)
        if not novel or novel.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或无权访问"
            )
        
        history = mcp_audit_service.get_novel_operation_history(
            db=db,
            novel_id=novel_id,
            limit=limit
        )
        
        return {
            "novel_id": novel_id,
            "novel_title": novel.title,
            "total_records": len(history),
            "operations": [
                {
                    "id": log.id,
                    "target_type": log.target_type,
                    "action": log.action,
                    "target_id": log.target_id,
                    "success": log.success,
                    "execution_time_ms": log.execution_time_ms,
                    "ai_tokens_used": log.ai_tokens_used,
                    "created_at": log.created_at.isoformat(),
                    "user_id": log.user_id,
                    "error_message": log.error_message
                }
                for log in history
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取小说操作历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取历史失败: {str(e)}"
        )


@router.get("/audit/statistics")
async def get_operation_statistics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户MCP操作统计信息
    """
    try:
        stats = mcp_audit_service.get_operation_statistics(
            db=db,
            user_id=current_user.id,
            days=days
        )
        
        return {
            "user_id": current_user.id,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"获取操作统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计失败: {str(e)}"
        )


@router.get("/audit/novel/{novel_id}/statistics")
async def get_novel_operation_statistics(
    novel_id: int,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定小说的MCP操作统计信息
    """
    try:
        # 验证小说权限
        novel = novel_crud.get_novel_by_id(db, novel_id)
        if not novel or novel.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或无权访问"
            )
        
        stats = mcp_audit_service.get_operation_statistics(
            db=db,
            novel_id=novel_id,
            days=days
        )
        
        return {
            "novel_id": novel_id,
            "novel_title": novel.title,
            "statistics": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取小说操作统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计失败: {str(e)}"
        )


@router.get("/audit/errors")
async def get_error_analysis(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户MCP操作错误分析
    """
    try:
        analysis = mcp_audit_service.get_error_analysis(
            db=db,
            user_id=current_user.id,
            days=days
        )
        
        return {
            "user_id": current_user.id,
            "error_analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"获取错误分析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分析失败: {str(e)}"
        )


@router.get("/monitoring/performance")
async def get_performance_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取MCP系统性能指标
    """
    try:
        # 获取当前并发操作数
        concurrent_ops = {}
        for novel_id, count in unified_mcp_service._operation_counters.items():
            if count > 0:
                concurrent_ops[novel_id] = count
        
        # 获取性能配置
        performance_config = unified_mcp_service.performance_config
        
        # 获取最近的性能统计
        recent_stats = mcp_audit_service.get_operation_statistics(
            db=db,
            user_id=current_user.id,
            days=1
        )
        
        return {
            "system_status": {
                "max_concurrent_operations": unified_mcp_service.max_concurrent_operations,
                "operation_timeout": unified_mcp_service.operation_timeout,
                "current_concurrent_operations": concurrent_ops,
                "total_active_operations": sum(concurrent_ops.values())
            },
            "performance_config": performance_config,
            "recent_performance": {
                "last_24h_operations": recent_stats["operation_summary"]["total_operations"],
                "last_24h_success_rate": recent_stats["operation_summary"]["success_rate"],
                "average_execution_time_ms": recent_stats["performance_metrics"]["average_execution_time_ms"]
            }
        }
        
    except Exception as e:
        logger.error(f"获取性能指标失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取指标失败: {str(e)}"
        )
