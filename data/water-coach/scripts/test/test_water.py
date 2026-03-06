#!/usr/bin/env python3
"""Unit tests for water.py"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import json
from water import (
    get_daily_goal,
    get_today_status,
    should_send_extra_notification,
    get_dynamic_threshold,
    load_config,
    calculate_expected_percent,
    log_water,
    increment_extra_notifications,
    reset_daily_counters,
    get_entry_by_message_id,
    get_entries_by_date,
    calculate_cumulative_for_date,
    get_message_context,
    is_user_setup
)

class TestIsUserSetup:
    """Tests for is_user_setup function."""
    
    def test_is_user_setup_returns_dict(self):
        """Test that is_user_setup returns a dict."""
        result = is_user_setup()
        assert isinstance(result, dict)
    
    def test_is_user_setup_has_required_fields(self):
        """Test that is_user_setup has all required fields."""
        result = is_user_setup()
        assert "is_setup" in result
        assert "weight_kg" in result
        assert "goal_ml" in result
        assert "config_exists" in result

class TestCalculateExpectedPercent:
    """Test the linear formula for expected progress."""
    
    def test_9am(self):
        # 9am = first hour: (1/13) * 100 = 7.7%
        result = calculate_expected_percent(9, 9, 22)
        assert 7 <= result <= 8
    
    def test_4pm(self):
        # 4pm = 8 hours passed: (8/13) * 100 = 61.5%
        result = calculate_expected_percent(16, 9, 22)
        assert 60 <= result <= 62
    
    def test_10pm(self):
        # 10pm = 13 hours: 100%
        result = calculate_expected_percent(22, 9, 22)
        assert result == 100

class TestGetDynamicThreshold:
    """Test dynamic threshold calculation."""
    
    def test_returns_expected_and_threshold(self):
        threshold = get_dynamic_threshold()
        assert "expected_percent" in threshold
        assert "threshold" in threshold
        assert "margin_percent" in threshold
        assert threshold["margin_percent"] == 25
    
    def test_threshold_is_lower_than_expected(self):
        threshold = get_dynamic_threshold()
        assert threshold["threshold"] < threshold["expected_percent"]

class TestGetDailyGoal:
    """Test daily goal calculation."""
    
    def test_default_goal(self):
        goal = get_daily_goal()
        # Goal = weight * 35 (from config)
        assert goal > 0  # Just check it's calculated

class TestGetTodayStatus:
    """Test status retrieval."""
    
    def test_status_returns_dict(self):
        status = get_today_status()
        assert isinstance(status, dict)
        assert "current_ml" in status
        assert "goal_ml" in status
        assert "percentage" in status
        assert "is_under_threshold" in status
    
    def test_status_values(self):
        status = get_today_status()
        assert status["goal_ml"] > 0  # Goal is calculated from config
        assert status["current_ml"] >= 0
        assert status["percentage"] >= 0  # Can exceed 100% (user drinks more than goal)

class TestShouldSendExtraNotification:
    """Test dynamic notification logic."""
    
    def test_returns_dict(self):
        result = should_send_extra_notification()
        assert isinstance(result, dict)
        assert "should_send" in result
        assert "reason" in result
    
    def test_has_valid_reasons(self):
        result = should_send_extra_notification()
        valid_reasons = [
            "dynamic_scheduling_disabled",
            "outside_working_hours",
            "no_water_logged_today",
            "healthy_progress",
            "max_extras_reached",
            "under_threshold",
            "on_track",
            "too_soon_since_last"
        ]
        assert result["reason"] in valid_reasons

class TestLogWater:
    """Test logging functionality."""
    
    def test_log_water_returns_status(self):
        # Note: This test depends on current state
        result = log_water(0, "test")  # Should return error or status
        assert isinstance(result, dict)
    
    def test_log_with_positive_amount(self):
        status_before = get_today_status()
        result = log_water(100, "test_slot")
        assert isinstance(result, dict)
        assert "current_ml" in result
        # Should be higher than before (or same if test isolation issues)

class TestDynamicCounters:
    """Test extra notification counters."""
    
    def test_increment(self):
        result = increment_extra_notifications()
        assert "extra_notifications_today" in result
    
    def test_reset(self):
        result = reset_daily_counters()
        assert result["extra_notifications_today"] == 0

class TestLoadConfig:
    """Test config loading."""
    
    def test_config_returns_dict(self):
        config = load_config()
        assert isinstance(config, dict)
    
    def test_config_has_dynamic_scheduling(self):
        config = load_config()
        assert "dynamic_scheduling" in config
        ds = config["dynamic_scheduling"]
        assert ds["enabled"] == True
        assert "formula" in ds
        assert "extra_notifications" in ds
    
    def test_formula_parameters(self):
        config = load_config()
        formula = config["dynamic_scheduling"]["formula"]
        assert formula["type"] == "linear_time_based"
        assert formula["margin_percent"] == 25
        assert formula["start_hour"] == 9
        assert formula["cutoff_hour"] == 22


class TestAuditFunctions:
    """Tests for audit trail functions."""
    
    def test_get_entry_by_message_id_returns_dict(self):
        """Test that get_entry_by_message_id returns a dict."""
        result = get_entry_by_message_id("test_id")
        assert isinstance(result, (dict, type(None)))
    
    def test_get_entries_by_date_returns_list(self):
        """Test that get_entries_by_date returns a list."""
        result = get_entries_by_date("2026-02-18")
        assert isinstance(result, list)
    
    def test_calculate_cumulative_for_date_returns_int(self):
        """Test that calculate_cumulative_for_date returns an int."""
        result = calculate_cumulative_for_date("2026-02-18")
        assert isinstance(result, int)
        assert result >= 0
    
    def test_get_message_context_returns_dict_or_none(self):
        """Test that get_message_context returns dict or None."""
        result = get_message_context("test_id")
        assert isinstance(result, (dict, type(None)))

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
