"""
统一MCP服务测试
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.unified_mcp_service import unified_mcp_service
from app.models.worldview_schemas import (
    UnifiedMCPAction, UnifiedMCPResponse,
    NovelAnalysisRequest, NovelOptimizationRequest
)
from app.models.user import User
from app.models.novel import Novel


class TestUnifiedMCPService:
    """统一MCP服务测试类"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return MagicMock(spec=Session)
    
    @pytest.fixture
    def mock_user(self):
        """模拟用户"""
        user = MagicMock(spec=User)
        user.id = 1
        user.username = "test_user"
        return user
    
    @pytest.fixture
    def mock_novel(self):
        """模拟小说"""
        novel = MagicMock(spec=Novel)
        novel.id = 1
        novel.title = "测试小说"
        novel.user_id = 1
        return novel
    
    @pytest.fixture
    def sample_mcp_action(self):
        """示例MCP操作"""
        return UnifiedMCPAction(
            target_type="character",
            action="analyze",
            novel_id=1,
            parameters={"analysis_depth": "comprehensive"},
            context="测试上下文"
        )
    
    @pytest.mark.asyncio
    async def test_execute_unified_action_success(
        self, mock_db, mock_user, mock_novel, sample_mcp_action
    ):
        """测试统一MCP操作成功执行"""
        # 模拟小说查询
        with patch('app.crud.novel.get_novel_by_id', return_value=mock_novel):
            # 模拟角色MCP服务
            with patch.object(
                unified_mcp_service, '_handle_character', 
                return_value={"target_id": 1, "message": "操作成功"}
            ) as mock_handler:
                
                result = await unified_mcp_service.execute_unified_action(
                    mock_db, sample_mcp_action, mock_user.id
                )
                
                # 验证结果
                assert result.success is True
                assert result.target_type == "character"
                assert result.action == "analyze"
                assert "操作成功" in result.message
                
                # 验证处理器被调用
                mock_handler.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_unified_action_invalid_novel(
        self, mock_db, mock_user, sample_mcp_action
    ):
        """测试无效小说ID的处理"""
        # 模拟小说不存在
        with patch('app.crud.novel.get_novel_by_id', return_value=None):
            
            result = await unified_mcp_service.execute_unified_action(
                mock_db, sample_mcp_action, mock_user.id
            )
            
            # 验证错误处理
            assert result.success is False
            assert "小说不存在或无权访问" in result.message
    
    @pytest.mark.asyncio
    async def test_execute_unified_action_unsupported_target(
        self, mock_db, mock_user, mock_novel
    ):
        """测试不支持的目标类型"""
        # 创建无效目标类型的操作
        invalid_action = UnifiedMCPAction(
            target_type="invalid_type",
            action="analyze",
            novel_id=1
        )
        
        with patch('app.crud.novel.get_novel_by_id', return_value=mock_novel):
            
            result = await unified_mcp_service.execute_unified_action(
                mock_db, invalid_action, mock_user.id
            )
            
            # 验证错误处理
            assert result.success is False
            assert "不支持的目标类型" in result.message
    
    @pytest.mark.asyncio
    async def test_execute_unified_action_unsupported_action(
        self, mock_db, mock_user, mock_novel
    ):
        """测试不支持的操作类型"""
        # 创建无效操作类型的操作
        invalid_action = UnifiedMCPAction(
            target_type="character",
            action="invalid_action",
            novel_id=1
        )
        
        with patch('app.crud.novel.get_novel_by_id', return_value=mock_novel):
            
            result = await unified_mcp_service.execute_unified_action(
                mock_db, invalid_action, mock_user.id
            )
            
            # 验证错误处理
            assert result.success is False
            assert "不支持的操作" in result.message
    
    @pytest.mark.asyncio
    async def test_analyze_novel_comprehensive_success(
        self, mock_db, mock_user, mock_novel
    ):
        """测试全面分析小说成功"""
        analysis_request = NovelAnalysisRequest(
            novel_id=1,
            analysis_scope=["worldview", "character"],
            analysis_depth="comprehensive"
        )
        
        with patch('app.crud.novel.get_novel_by_id', return_value=mock_novel):
            # 模拟分析方法
            with patch.object(
                unified_mcp_service, '_analyze_worldview',
                return_value={"consistency_score": 8.5}
            ):
                with patch.object(
                    unified_mcp_service, '_analyze_characters',
                    return_value={"character_count": 5}
                ):
                    with patch.object(
                        unified_mcp_service, '_generate_overall_assessment',
                        return_value={"overall_score": 8.2}
                    ):
                        
                        result = await unified_mcp_service.analyze_novel_comprehensive(
                            mock_db, analysis_request, mock_user.id
                        )
                        
                        # 验证结果
                        assert result.novel_id == 1
                        assert result.analysis_scope == ["worldview", "character"]
                        assert result.worldview_analysis is not None
                        assert result.character_analysis is not None
                        assert result.overall_score == 8.2
    
    @pytest.mark.asyncio
    async def test_optimize_novel_comprehensive_success(
        self, mock_db, mock_user, mock_novel
    ):
        """测试全面优化小说成功"""
        optimization_request = NovelOptimizationRequest(
            novel_id=1,
            optimization_goals=["提升质量", "增强一致性"],
            target_areas=["worldview", "character"]
        )
        
        with patch('app.crud.novel.get_novel_by_id', return_value=mock_novel):
            # 模拟优化方法
            with patch.object(
                unified_mcp_service, '_optimize_worldview',
                return_value={"optimization_areas": ["魔法体系"]}
            ):
                with patch.object(
                    unified_mcp_service, '_optimize_characters',
                    return_value={"optimization_areas": ["角色深度"]}
                ):
                    with patch.object(
                        unified_mcp_service, '_generate_implementation_plan',
                        return_value={"priority_order": ["角色优化"]}
                    ):
                        
                        result = await unified_mcp_service.optimize_novel_comprehensive(
                            mock_db, optimization_request, mock_user.id
                        )
                        
                        # 验证结果
                        assert result.novel_id == 1
                        assert result.optimization_goals == ["提升质量", "增强一致性"]
                        assert result.worldview_optimizations is not None
                        assert result.character_optimizations is not None
                        assert result.priority_order == ["角色优化"]
    
    @pytest.mark.asyncio
    async def test_handle_character_delegation(
        self, mock_db, mock_user, sample_mcp_action
    ):
        """测试角色处理委托给角色MCP服务"""
        with patch('app.services.character_mcp_service.character_mcp_service.execute_action') as mock_execute:
            # 模拟角色MCP服务返回
            mock_response = MagicMock()
            mock_response.character_id = 1
            mock_response.result = {"character": "test"}
            mock_execute.return_value = mock_response
            
            result = await unified_mcp_service._handle_character(
                mock_db, sample_mcp_action, mock_user.id
            )
            
            # 验证委托调用
            mock_execute.assert_called_once()
            assert result["target_id"] == 1
            assert "角色analyze操作完成" in result["message"]
    
    @pytest.mark.asyncio
    async def test_error_handling_and_logging(
        self, mock_db, mock_user, sample_mcp_action
    ):
        """测试错误处理和日志记录"""
        with patch('app.crud.novel.get_novel_by_id', side_effect=Exception("数据库错误")):
            with patch('loguru.logger.error') as mock_logger:
                
                result = await unified_mcp_service.execute_unified_action(
                    mock_db, sample_mcp_action, mock_user.id
                )
                
                # 验证错误处理
                assert result.success is False
                assert "操作失败" in result.message
                
                # 验证日志记录
                mock_logger.assert_called_once()
    
    def test_supported_actions_completeness(self):
        """测试支持的操作类型完整性"""
        expected_actions = {
            "analyze", "optimize", "create", "update", "delete", 
            "generate", "validate", "sync", "batch_update", 
            "ai_review", "auto_fix", "smart_suggest"
        }
        
        actual_actions = set(unified_mcp_service.supported_actions.keys())
        
        # 验证所有预期操作都被支持
        assert expected_actions.issubset(actual_actions)
    
    def test_target_handlers_completeness(self):
        """测试目标处理器完整性"""
        expected_targets = {
            "worldview", "plot", "timeline", "outline", 
            "style", "character", "novel"
        }
        
        actual_targets = set(unified_mcp_service.target_handlers.keys())
        
        # 验证所有预期目标都有处理器
        assert expected_targets.issubset(actual_targets)


class TestMCPIntegration:
    """MCP集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_character_analysis(self):
        """测试完整的角色分析工作流"""
        # 这里可以添加端到端的集成测试
        # 测试从API调用到服务执行的完整流程
        pass
    
    @pytest.mark.asyncio
    async def test_concurrent_mcp_operations(self):
        """测试并发MCP操作"""
        # 测试多个MCP操作同时执行的情况
        pass
    
    @pytest.mark.asyncio
    async def test_mcp_operation_rollback(self):
        """测试MCP操作回滚"""
        # 测试操作失败时的回滚机制
        pass
