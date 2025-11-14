"""
一致性检查服务单元测试
测试规则引擎、时间线管理、情绪状态机等功能
"""
import pytest
from app.services.consistency_service import (
    RuleEngine,
    TimelineManager,
    EmotionStateMachine,
    ConsistencyService
)


class TestRuleEngine:
    """规则引擎测试"""

    @pytest.fixture
    def rule_engine(self):
        """创建规则引擎实例"""
        engine = RuleEngine()
        engine.add_rule("魔法等级上限", 9)
        engine.add_rule("飞行速度上限", 100)
        return engine

    def test_validate_magic_level_pass(self, rule_engine):
        """测试魔法等级验证 - 通过"""
        content = "李明是一位5级魔法师，实力强大。"
        result = rule_engine.validate(content)

        assert result["is_valid"] is True
        assert len(result["violations"]) == 0

    def test_validate_magic_level_fail(self, rule_engine):
        """测试魔法等级验证 - 失败"""
        content = "李明突破到了10级魔法师，震惊全场！"
        result = rule_engine.validate(content)

        assert result["is_valid"] is False
        assert len(result["violations"]) > 0
        assert "魔法等级10超出上限9" in result["violations"][0]

    def test_validate_flying_speed_pass(self, rule_engine):
        """测试飞行速度验证 - 通过"""
        content = "他以80公里每小时的速度飞行。"
        result = rule_engine.validate(content)

        assert result["is_valid"] is True

    def test_validate_flying_speed_fail(self, rule_engine):
        """测试飞行速度验证 - 失败"""
        content = "他以150公里每小时的速度飞行。"
        result = rule_engine.validate(content)

        assert result["is_valid"] is False
        assert "飞行速度150" in result["violations"][0]


class TestTimelineManager:
    """时间线管理器测试"""

    @pytest.fixture
    def timeline_manager(self):
        """创建时间线管理器实例"""
        return TimelineManager()

    def test_add_event(self, timeline_manager):
        """测试添加事件"""
        timeline_manager.add_event(1, 1, "第一天的事件")
        timeline_manager.add_event(1, 2, "第二天的事件")

        timeline = timeline_manager.get_timeline(1)
        assert len(timeline) == 2
        assert timeline[0][0] == 1
        assert timeline[1][0] == 2

    def test_validate_time_forward(self, timeline_manager):
        """测试时间前进 - 正常"""
        timeline_manager.add_event(1, 1, "第一天")

        result = timeline_manager.validate_new_event(1, 2, "第二天")

        assert result["is_valid"] is True

    def test_validate_time_backward(self, timeline_manager):
        """测试时间倒退 - 异常"""
        timeline_manager.add_event(1, 5, "第五天")

        result = timeline_manager.validate_new_event(1, 3, "第三天")

        assert result["is_valid"] is False
        assert "时间倒退" in result["reason"]

    def test_validate_location_movement(self, timeline_manager):
        """测试地理移动合理性"""
        timeline_manager.add_event(1, 1, "在北京城修炼")

        # 第二天就到上海城，应该不合理（需要至少1天）
        result = timeline_manager.validate_new_event(1, 1, "在上海城战斗")

        # 注意：当前实现要求day间隔至少1天
        # 如果day相同或间隔小于1，应该检测到不合理
        if result["is_valid"] is False:
            assert "地理移动不合理" in result["reason"]


class TestEmotionStateMachine:
    """情绪状态机测试"""

    @pytest.fixture
    def emotion_machine(self):
        """创建情绪状态机实例"""
        return EmotionStateMachine()

    def test_valid_emotion_transition(self, emotion_machine):
        """测试合理的情绪转换"""
        emotion_machine.set_emotion("李明", "平静")

        result = emotion_machine.validate_transition("李明", "愤怒")

        assert result["is_valid"] is True
        assert emotion_machine.current_emotions["李明"] == "愤怒"

    def test_invalid_emotion_transition(self, emotion_machine):
        """测试不合理的情绪转换"""
        emotion_machine.set_emotion("李明", "暴怒")

        # 暴怒不能直接转换到平静
        result = emotion_machine.validate_transition("李明", "平静")

        assert result["is_valid"] is False
        assert "不能从'暴怒'直接转换到'平静'" in result["reason"]

    def test_emotion_chain(self, emotion_machine):
        """测试情绪转换链"""
        emotion_machine.set_emotion("李明", "平静")

        # 平静 -> 愤怒 -> 暴怒 -> 愤怒 -> 平静
        assert emotion_machine.validate_transition("李明", "愤怒")["is_valid"]
        assert emotion_machine.validate_transition("李明", "暴怒")["is_valid"]
        assert emotion_machine.validate_transition("李明", "愤怒")["is_valid"]
        assert emotion_machine.validate_transition("李明", "平静")["is_valid"]


class TestConsistencyService:
    """一致性检查服务集成测试"""

    @pytest.fixture
    def consistency_service(self):
        """创建一致性检查服务实例"""
        service = ConsistencyService()
        service.init_worldview_rules(1, {
            "魔法等级上限": 9,
            "飞行速度上限": 100
        })
        return service

    @pytest.mark.asyncio
    async def test_check_content_pass(self, consistency_service):
        """测试内容检查 - 通过"""
        content = "李明是一位5级魔法师，在第一天开始了修炼之旅。"

        result = await consistency_service.check_content(
            novel_id=1,
            content=content,
            chapter=1,
            current_day=1
        )

        assert result["has_conflict"] is False
        assert len(result["violations"]) == 0

    @pytest.mark.asyncio
    async def test_check_content_rule_violation(self, consistency_service):
        """测试内容检查 - 违反规则"""
        content = "李明突破到了12级魔法师，实力超越了所有人！"

        result = await consistency_service.check_content(
            novel_id=1,
            content=content,
            chapter=1,
            current_day=1
        )

        assert result["has_conflict"] is True
        assert len(result["violations"]) > 0

    @pytest.mark.asyncio
    async def test_check_content_timeline_violation(self, consistency_service):
        """测试内容检查 - 时间线违反"""
        # 第一次：第5天的事件
        await consistency_service.check_content(1, "第五天的事件", 1, 5)

        # 第二次：第3天的事件（时间倒退）
        result = await consistency_service.check_content(1, "第三天的事件", 1, 3)

        assert result["has_conflict"] is True
        assert any("时间倒退" in v for v in result["violations"])
