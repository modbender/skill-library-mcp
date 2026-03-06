#!/usr/bin/env python3
"""Tests for assemble.py"""

import json
import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from assemble import (
    AGENT_TYPES,
    detect_agent_type,
    create_agent_config,
    create_mission,
    generate_spawn_command,
    generate_send_command,
)


class TestAgentTypes:
    """Test AGENT_TYPES configuration"""
    
    def test_all_agent_types_have_required_fields(self):
        required_fields = {"emoji", "model", "timeout", "keywords"}
        for agent_type, config in AGENT_TYPES.items():
            assert required_fields.issubset(config.keys()), f"{agent_type} missing fields"
    
    def test_agent_types_have_valid_models(self):
        valid_models = {"sonnet", "opus", "haiku"}
        for agent_type, config in AGENT_TYPES.items():
            assert config["model"] in valid_models, f"{agent_type} has invalid model"
    
    def test_agent_types_have_positive_timeout(self):
        for agent_type, config in AGENT_TYPES.items():
            assert config["timeout"] > 0, f"{agent_type} has non-positive timeout"


class TestDetectAgentType:
    """Test agent type detection from subtask description"""
    
    def test_detect_researcher(self):
        assert detect_agent_type("사용자 데이터 조사") == "researcher"
        assert detect_agent_type("경쟁사 리서치") == "researcher"
        assert detect_agent_type("정보 수집하기") == "researcher"
    
    def test_detect_analyst(self):
        assert detect_agent_type("패턴 발견") == "analyst"
        assert detect_agent_type("인사이트 도출") == "analyst"
    
    def test_detect_writer(self):
        assert detect_agent_type("리포트 작성") == "writer"
        assert detect_agent_type("문서 만들기") == "writer"
    
    def test_detect_coder(self):
        assert detect_agent_type("API 개발") == "coder"
        assert detect_agent_type("코드 구현") == "coder"
    
    def test_detect_reviewer(self):
        assert detect_agent_type("품질 검토") == "reviewer"
        assert detect_agent_type("피드백 확인") == "reviewer"
    
    def test_detect_integrator(self):
        assert detect_agent_type("결과 통합") == "integrator"
        assert detect_agent_type("최종 병합") == "integrator"
    
    def test_default_to_researcher(self):
        assert detect_agent_type("알 수 없는 작업") == "researcher"
        assert detect_agent_type("") == "researcher"


class TestCreateAgentConfig:
    """Test agent configuration creation"""
    
    def test_create_basic_config(self):
        subtask = {"description": "데이터 조사하기"}
        config = create_agent_config(subtask, "test_mission", 0)
        
        assert config["id"] == "test_mission_agent_00"
        assert config["type"] == "researcher"
        assert config["status"] == "pending"
        assert config["mode"] == "spawn"
    
    def test_override_type(self):
        subtask = {"description": "무언가 하기", "type": "coder"}
        config = create_agent_config(subtask, "test", 1)
        
        assert config["type"] == "coder"
        assert config["emoji"] == "💻"
    
    def test_override_model(self):
        subtask = {"description": "분석", "model": "haiku"}
        config = create_agent_config(subtask, "test", 0)
        
        assert config["model"] == "haiku"
    
    def test_dependencies(self):
        subtask = {
            "description": "통합",
            "dependencies": ["agent_01", "agent_02"]
        }
        config = create_agent_config(subtask, "test", 3)
        
        assert config["dependencies"] == ["agent_01", "agent_02"]
    
    def test_agent_index_formatting(self):
        config = create_agent_config({"description": "test"}, "m", 5)
        assert config["id"] == "m_agent_05"
        
        config = create_agent_config({"description": "test"}, "m", 99)
        assert config["id"] == "m_agent_99"


class TestCreateMission:
    """Test mission creation"""
    
    def test_create_mission_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["AVENGERS_WORKSPACE"] = tmpdir
            
            # Reload module to pick up new env
            import importlib
            import assemble
            importlib.reload(assemble)
            
            mission = assemble.create_mission("Test task")
            
            assert "id" in mission
            assert "path" in mission
            assert mission["task"] == "Test task"
            assert mission["status"] == "initializing"
            
            # Check directories created
            mission_path = Path(mission["path"])
            assert mission_path.exists()
            assert (mission_path / "agents").exists()
            assert (mission_path / "outputs").exists()
            assert (mission_path / "logs").exists()
            assert (mission_path / "mission.json").exists()


class TestGenerateCommands:
    """Test command generation for agents"""
    
    def test_spawn_command_structure(self):
        agent = {
            "id": "test_agent_01",
            "type": "researcher",
            "emoji": "🔬",
            "model": "sonnet",
            "timeout": 1800,
            "description": "Research competitors",
            "inputs": ["Company A", "Company B"],
            "expected_output": "Comparison report"
        }
        
        cmd = generate_spawn_command(agent, "/tmp/mission")
        
        assert "task" in cmd
        assert cmd["model"] == "sonnet"
        assert cmd["runTimeoutSeconds"] == 1800
        assert cmd["cleanup"] == "keep"
        assert cmd["label"] == "test_agent_01"
        assert "Research competitors" in cmd["task"]
    
    def test_send_command_structure(self):
        agent = {
            "id": "test_agent_01",
            "type": "analyst",
            "description": "Analyze data",
            "inputs": [],
            "expected_output": "Analysis",
            "timeout": 600
        }
        
        cmd = generate_send_command(agent, "watson")
        
        assert cmd["label"] == "watson"
        assert "Analyze data" in cmd["message"]
        assert cmd["timeoutSeconds"] == 600


class TestIntegration:
    """Integration tests"""
    
    def test_full_workflow(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["AVENGERS_WORKSPACE"] = tmpdir
            
            import importlib
            import assemble
            importlib.reload(assemble)
            
            # Create mission
            mission = assemble.create_mission("Competitor analysis")
            
            # Define subtasks
            subtasks = [
                {"description": "조사: Company A", "type": "researcher"},
                {"description": "조사: Company B", "type": "researcher"},
                {"description": "결과 분석", "type": "analyst", "dependencies": []},
                {"description": "리포트 작성", "type": "writer"}
            ]
            
            # Create agent configs
            agents = [
                assemble.create_agent_config(st, mission["id"], i)
                for i, st in enumerate(subtasks)
            ]
            
            assert len(agents) == 4
            assert agents[0]["type"] == "researcher"
            assert agents[2]["type"] == "analyst"
            assert agents[3]["type"] == "writer"
            
            # Save execution plan
            plan_path = assemble.save_execution_plan(mission, agents)
            assert Path(plan_path).exists()
            
            with open(plan_path) as f:
                plan = json.load(f)
            
            assert plan["total_agents"] == 4
            assert len(plan["commands"]) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
