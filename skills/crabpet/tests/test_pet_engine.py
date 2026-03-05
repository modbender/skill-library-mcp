#!/usr/bin/env python3
"""Unit tests for CrabPet Engine."""

import json
import os
import sys
import tempfile
import shutil
import unittest
from datetime import datetime, timedelta, date
from pathlib import Path
from unittest.mock import patch

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import pet_engine


class TestXPCalculation(unittest.TestCase):
    """Tests for XP calculation logic."""

    def test_empty_logs(self):
        self.assertEqual(pet_engine.calculate_xp([]), 0)

    def test_single_day_base_xp(self):
        logs = [{"date": date.today(), "chars": 50, "content_lower": "hello"}]
        # base=10 + content_bonus=0 (50//100=0) + streak_bonus (1*2=2)
        self.assertEqual(pet_engine.calculate_xp(logs), 12)

    def test_content_bonus(self):
        logs = [{"date": date.today(), "chars": 500, "content_lower": "x" * 500}]
        # base=10 + content_bonus=5 (500//100) + streak=2
        self.assertEqual(pet_engine.calculate_xp(logs), 17)

    def test_content_bonus_max_cap(self):
        logs = [{"date": date.today(), "chars": 10000, "content_lower": "x" * 10000}]
        # base=10 + content_bonus=50 (capped) + streak=2
        self.assertEqual(pet_engine.calculate_xp(logs), 62)

    def test_multi_day_xp(self):
        today = date.today()
        logs = [
            {"date": today, "chars": 100, "content_lower": "a" * 100},
            {"date": today - timedelta(days=1), "chars": 200, "content_lower": "b" * 200},
        ]
        # day1: 10+1=11, day2: 10+2=12, streak=2, streak_bonus=4
        self.assertEqual(pet_engine.calculate_xp(logs), 27)


class TestLevelSystem(unittest.TestCase):
    """Tests for level/stage calculations."""

    def test_level_1_at_zero_xp(self):
        self.assertEqual(pet_engine.xp_to_level(0), 1)

    def test_level_at_10_xp(self):
        self.assertEqual(pet_engine.xp_to_level(10), 1)

    def test_level_at_40_xp(self):
        self.assertEqual(pet_engine.xp_to_level(40), 2)

    def test_level_at_1000_xp(self):
        self.assertEqual(pet_engine.xp_to_level(1000), 10)

    def test_stage_baby(self):
        self.assertEqual(pet_engine.level_to_stage(1), "baby")
        self.assertEqual(pet_engine.level_to_stage(5), "baby")

    def test_stage_teen(self):
        self.assertEqual(pet_engine.level_to_stage(6), "teen")
        self.assertEqual(pet_engine.level_to_stage(15), "teen")

    def test_stage_adult(self):
        self.assertEqual(pet_engine.level_to_stage(16), "adult")
        self.assertEqual(pet_engine.level_to_stage(30), "adult")

    def test_stage_legend(self):
        self.assertEqual(pet_engine.level_to_stage(31), "legend")
        self.assertEqual(pet_engine.level_to_stage(100), "legend")


class TestStreak(unittest.TestCase):
    """Tests for streak calculation."""

    def test_no_logs(self):
        self.assertEqual(pet_engine.calculate_streak([]), 0)

    def test_today_only(self):
        logs = [{"date": date.today()}]
        self.assertEqual(pet_engine.calculate_streak(logs), 1)

    def test_consecutive_days(self):
        today = date.today()
        logs = [
            {"date": today},
            {"date": today - timedelta(days=1)},
            {"date": today - timedelta(days=2)},
        ]
        self.assertEqual(pet_engine.calculate_streak(logs), 3)

    def test_broken_streak(self):
        today = date.today()
        logs = [
            {"date": today},
            {"date": today - timedelta(days=1)},
            {"date": today - timedelta(days=3)},  # gap
        ]
        self.assertEqual(pet_engine.calculate_streak(logs), 2)

    def test_old_logs_no_streak(self):
        old = date.today() - timedelta(days=10)
        logs = [{"date": old}]
        self.assertEqual(pet_engine.calculate_streak(logs), 0)


class TestMood(unittest.TestCase):
    """Tests for mood calculation."""

    def test_no_logs_frozen(self):
        mood, days = pet_engine.calculate_mood([])
        self.assertEqual(mood, "frozen")
        self.assertEqual(days, 999)

    def test_today_energetic(self):
        logs = [{"date": date.today()}]
        mood, days = pet_engine.calculate_mood(logs)
        self.assertEqual(mood, "energetic")
        self.assertEqual(days, 0)

    def test_bored(self):
        logs = [{"date": date.today() - timedelta(days=2)}]
        mood, _ = pet_engine.calculate_mood(logs)
        self.assertEqual(mood, "bored")

    def test_slacking(self):
        logs = [{"date": date.today() - timedelta(days=5)}]
        mood, _ = pet_engine.calculate_mood(logs)
        self.assertEqual(mood, "slacking")

    def test_hibernating(self):
        logs = [{"date": date.today() - timedelta(days=10)}]
        mood, _ = pet_engine.calculate_mood(logs)
        self.assertEqual(mood, "hibernating")

    def test_dusty(self):
        logs = [{"date": date.today() - timedelta(days=20)}]
        mood, _ = pet_engine.calculate_mood(logs)
        self.assertEqual(mood, "dusty")

    def test_frozen(self):
        logs = [{"date": date.today() - timedelta(days=60)}]
        mood, _ = pet_engine.calculate_mood(logs)
        self.assertEqual(mood, "frozen")


class TestPersonality(unittest.TestCase):
    """Tests for personality calculation."""

    def test_empty_logs(self):
        result = pet_engine.calculate_personality([])
        self.assertTrue(all(v == 0.0 for v in result.values()))

    def test_coder_dominance(self):
        # Spread across multiple days (chronological order, oldest first) to lower hustle score
        today = date.today()
        logs = [
            {"date": today - timedelta(days=9 - i), "chars": 500,
             "content_lower": " ".join(["code", "debug", "git", "python", "function",
                                        "class", "import", "test", "fix", "script",
                                        "deploy", "bash", "error", "api", "npm"] * 3)}
            for i in range(10)
        ]
        result = pet_engine.calculate_personality(logs)
        self.assertEqual(pet_engine.get_primary_personality(result), "coder")

    def test_writer_dominance(self):
        today = date.today()
        logs = [
            {"date": today - timedelta(days=9 - i), "chars": 500,
             "content_lower": " ".join(["write", "article", "blog", "draft", "edit",
                                        "post", "story", "essay", "narrative", "content",
                                        "summary", "publish", "headline", "tone"] * 3)}
            for i in range(10)
        ]
        result = pet_engine.calculate_personality(logs)
        self.assertEqual(pet_engine.get_primary_personality(result), "writer")

    def test_neutral_when_no_keywords(self):
        logs = [{
            "date": date.today(),
            "chars": 100,
            "content_lower": "hello world how are you today"
        }]
        result = pet_engine.calculate_personality(logs)
        primary = pet_engine.get_primary_personality(result)
        # With no keyword matches, hustle might dominate from usage rate
        self.assertIn(primary, ["neutral", "hustle"])


class TestAccessories(unittest.TestCase):
    """Tests for accessory assignment."""

    def test_baby_no_accessories(self):
        pers = {"coder": 1.0, "writer": 0, "analyst": 0, "creative": 0, "hustle": 0}
        result = pet_engine.get_accessories(pers, "baby")
        self.assertEqual(result, [])

    def test_teen_coder_accessories(self):
        pers = {"coder": 1.0, "writer": 0, "analyst": 0, "creative": 0, "hustle": 0}
        result = pet_engine.get_accessories(pers, "teen")
        self.assertEqual(result, ["glasses", "tiny_laptop"])

    def test_legend_golden_aura(self):
        pers = {"coder": 1.0, "writer": 0, "analyst": 0, "creative": 0, "hustle": 0}
        result = pet_engine.get_accessories(pers, "legend")
        self.assertIn("golden_aura", result)


class TestAchievements(unittest.TestCase):
    """Tests for achievement checks."""

    def test_first_chat_always_unlocked(self):
        state = {"achievements": [], "personality": {}}
        result = pet_engine.check_achievements(state, [], 0)
        self.assertIn("first_chat", result)

    def test_streak_achievements(self):
        state = {"achievements": [], "personality": {}}
        result = pet_engine.check_achievements(state, [], 7)
        self.assertIn("day_3", result)
        self.assertIn("day_7", result)
        self.assertNotIn("day_30", result)

    def test_personality_achievement(self):
        state = {"achievements": [], "personality": {"coder": 0.9}}
        result = pet_engine.check_achievements(state, [], 0)
        self.assertIn("code_master", result)

    def test_chatterbox_achievement(self):
        state = {"achievements": [], "personality": {}}
        logs = [{"date": date.today(), "content_lower": "x"} for _ in range(500)]
        result = pet_engine.check_achievements(state, logs, 0)
        self.assertIn("chatterbox", result)


class TestComebackMessage(unittest.TestCase):
    """Tests for comeback message logic."""

    def test_no_comeback_when_active(self):
        result = pet_engine.get_comeback_message(0, 0)
        self.assertIsNone(result)

    def test_short_comeback(self):
        result = pet_engine.get_comeback_message(2, 0)
        self.assertEqual(result, pet_engine.COMEBACK_MESSAGES["short"])

    def test_medium_comeback(self):
        result = pet_engine.get_comeback_message(5, 0)
        self.assertEqual(result, pet_engine.COMEBACK_MESSAGES["medium"])

    def test_long_comeback(self):
        result = pet_engine.get_comeback_message(14, 0)
        self.assertEqual(result, pet_engine.COMEBACK_MESSAGES["long"])

    def test_no_comeback_still_absent(self):
        result = pet_engine.get_comeback_message(5, 5)
        self.assertIsNone(result)


class TestInitCommand(unittest.TestCase):
    """Tests for init command."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.orig_data_dir = pet_engine.DATA_DIR
        self.orig_output_dir = pet_engine.OUTPUT_DIR
        self.orig_state_file = pet_engine.STATE_FILE
        pet_engine.DATA_DIR = Path(self.tmpdir) / "data"
        pet_engine.OUTPUT_DIR = Path(self.tmpdir) / "output"
        pet_engine.STATE_FILE = pet_engine.DATA_DIR / "pet_state.json"

    def tearDown(self):
        pet_engine.DATA_DIR = self.orig_data_dir
        pet_engine.OUTPUT_DIR = self.orig_output_dir
        pet_engine.STATE_FILE = self.orig_state_file
        shutil.rmtree(self.tmpdir)

    def test_init_creates_state(self):
        pet_engine.cmd_init("TestCrab")
        self.assertTrue(pet_engine.STATE_FILE.exists())
        state = json.loads(pet_engine.STATE_FILE.read_text())
        self.assertEqual(state["name"], "TestCrab")
        self.assertEqual(state["level"], 1)
        self.assertIn("first_chat", state["achievements"])

    def test_init_default_name(self):
        pet_engine.cmd_init()
        state = json.loads(pet_engine.STATE_FILE.read_text())
        self.assertEqual(state["name"], "CrabPet")


class TestLoadSprite(unittest.TestCase):
    """Tests for sprite loading."""

    def test_load_existing_sprite(self):
        sprite = pet_engine.load_sprite("body", "baby")
        if sprite is not None:
            self.assertEqual(sprite["name"], "baby")
            self.assertIn("pixels", sprite)

    def test_load_nonexistent_sprite(self):
        result = pet_engine.load_sprite("body", "nonexistent")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
