#!/usr/bin/env python3
"""Tests for cron_builder."""

import os
import re
import sys
import unittest

# Add parent scripts dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from cron_builder import parse, build_command, _parse_time, _parse_frequency, _parse_channel


class TestTimeParsing(unittest.TestCase):
    def test_simple_am(self):
        self.assertEqual(_parse_time('at 8am'), (8, 0))

    def test_simple_pm(self):
        self.assertEqual(_parse_time('at 3pm'), (15, 0))

    def test_with_minutes_am(self):
        self.assertEqual(_parse_time('at 8:45am'), (8, 45))

    def test_with_minutes_pm(self):
        self.assertEqual(_parse_time('at 8:45pm'), (20, 45))

    def test_noon(self):
        self.assertEqual(_parse_time('at noon'), (12, 0))

    def test_midnight(self):
        self.assertEqual(_parse_time('at midnight'), (0, 0))

    def test_24h(self):
        self.assertEqual(_parse_time('at 14:30'), (14, 30))

    def test_12am(self):
        self.assertEqual(_parse_time('at 12am'), (0, 0))

    def test_12pm(self):
        self.assertEqual(_parse_time('at 12pm'), (12, 0))

    def test_dot_separator(self):
        self.assertEqual(_parse_time('at 8.45am'), (8, 45))

    def test_no_time(self):
        self.assertIsNone(_parse_time('remind me to do something'))


class TestFrequencyParsing(unittest.TestCase):
    def test_daily(self):
        self.assertEqual(_parse_frequency('daily reminder'), ('daily', None))

    def test_every_day(self):
        self.assertEqual(_parse_frequency('every day at 8am'), ('daily', None))

    def test_every_2_hours(self):
        self.assertEqual(_parse_frequency('every 2 hours'), ('every_n_hours', 2))

    def test_hourly(self):
        self.assertEqual(_parse_frequency('hourly check'), ('hourly', None))

    def test_mondays(self):
        self.assertEqual(_parse_frequency('on Mondays'), ('monday', None))

    def test_weekdays(self):
        self.assertEqual(_parse_frequency('weekdays at 9am'), ('weekdays', None))

    def test_weekly(self):
        self.assertEqual(_parse_frequency('weekly review'), ('weekly', None))

    def test_monthly(self):
        self.assertEqual(_parse_frequency('monthly report'), ('monthly', None))

    def test_in_minutes(self):
        self.assertEqual(_parse_frequency('in 20 minutes'), ('in_minutes', 20))

    def test_in_minutes_short(self):
        self.assertEqual(_parse_frequency('in 5m'), ('in_minutes', 5))

    def test_weekly_on_mondays(self):
        # "weekly check-in on Mondays" should resolve to monday, not weekly
        self.assertEqual(_parse_frequency('weekly check-in on Mondays'), ('monday', None))

    def test_default_no_keyword(self):
        self.assertEqual(_parse_frequency('reminder at 8am'), ('default', None))

    def test_default_no_keyword_no_time(self):
        self.assertEqual(_parse_frequency('remind me about something'), ('default', None))


class TestChannelDetection(unittest.TestCase):
    def test_telegram(self):
        self.assertEqual(_parse_channel('send on telegram'), 'telegram')

    def test_whatsapp(self):
        self.assertEqual(_parse_channel('on whatsapp please'), 'whatsapp')

    def test_slack(self):
        self.assertEqual(_parse_channel('post on slack'), 'slack')

    def test_discord(self):
        self.assertEqual(_parse_channel('on discord'), 'discord')

    def test_default_telegram(self):
        self.assertEqual(_parse_channel('just remind me'), 'telegram')

    def test_env_override(self):
        os.environ['CRON_DEFAULT_CHANNEL'] = 'whatsapp'
        try:
            self.assertEqual(_parse_channel('just remind me'), 'whatsapp')
        finally:
            del os.environ['CRON_DEFAULT_CHANNEL']


class TestOneShotCommand(unittest.TestCase):
    def test_in_minutes_produces_at_flag(self):
        parsed = parse('Remind me in 20 minutes on telegram')
        self.assertTrue(parsed['one_shot'])
        cmd = build_command(parsed)
        self.assertIn('--at "20m"', cmd)
        self.assertIn('--delete-after-run', cmd)
        self.assertIn('--session isolated', cmd)
        self.assertIn('--deliver', cmd)

    def test_one_shot_no_cron(self):
        parsed = parse('Remind me in 5 minutes')
        cmd = build_command(parsed)
        self.assertNotIn('--cron', cmd)
        self.assertIn('--at "5m"', cmd)


class TestRepeatingCommand(unittest.TestCase):
    def test_daily_produces_cron(self):
        parsed = parse('Create a daily reminder at 8am')
        self.assertFalse(parsed['one_shot'])
        cmd = build_command(parsed)
        self.assertIn('--cron "0 8 * * *"', cmd)
        self.assertIn('--tz "America/New_York"', cmd)
        self.assertNotIn('--delete-after-run', cmd)
        self.assertIn('--session isolated', cmd)
        self.assertIn('--deliver', cmd)

    def test_every_2_hours_produces_every(self):
        parsed = parse('Remind me to drink water every 2 hours')
        cmd = build_command(parsed)
        self.assertIn('--every "2h"', cmd)
        self.assertNotIn('--cron', cmd)

    def test_weekdays(self):
        parsed = parse('Weekday standup at 9am')
        cmd = build_command(parsed)
        self.assertIn('--cron "0 9 * * 1-5"', cmd)

    def test_monday(self):
        parsed = parse('Weekly check-in on Mondays at 9am')
        cmd = build_command(parsed)
        self.assertIn('--cron "0 9 * * 1"', cmd)

    def test_monthly(self):
        parsed = parse('Monthly report at noon')
        cmd = build_command(parsed)
        self.assertIn('--cron "0 12 1 * *"', cmd)

    def test_hourly_produces_every(self):
        parsed = parse('Hourly water reminder')
        cmd = build_command(parsed)
        self.assertIn('--every "1h"', cmd)


class TestEdgeCases(unittest.TestCase):
    def test_no_time_for_repeating(self):
        parsed = parse('daily reminder to stretch')
        # Should still succeed — defaults to 9:00
        self.assertTrue('errors' not in parsed)
        cmd = build_command(parsed)
        self.assertIn('--cron "0 9 * * *"', cmd)

    def test_channel_in_message(self):
        parsed = parse('Send me a quote on discord at 8am')
        self.assertEqual(parsed['channel'], 'discord')

    def test_message_passthrough_drink_water(self):
        parsed = parse('remind me to drink water every 2 hours')
        self.assertEqual(parsed['message'], 'drink water')

    def test_message_passthrough_strip_time(self):
        parsed = parse('at 3pm take the dog out')
        self.assertEqual(parsed['message'], 'take the dog out')

    def test_message_passthrough_strip_all(self):
        parsed = parse('daily standup on slack at 9am')
        self.assertEqual(parsed['message'], 'standup')

    def test_message_fallback_reminder(self):
        parsed = parse('at 3pm')
        self.assertEqual(parsed['message'], 'Reminder')

    def test_command_has_all_required_flags(self):
        parsed = parse('Daily reminder at 8am on telegram')
        cmd = build_command(parsed)
        for flag in ['--session isolated', '--deliver', '--channel', '--to', '--name']:
            self.assertIn(flag, cmd, f'Missing required flag: {flag}')


class TestAtClockOneShot(unittest.TestCase):
    def test_at_3pm_is_one_shot(self):
        parsed = parse('at 3pm')
        self.assertTrue(parsed['one_shot'])
        self.assertEqual(parsed['freq_type'], 'at_clock')
        cmd = build_command(parsed)
        self.assertIn('--at', cmd)
        self.assertIn('--delete-after-run', cmd)
        self.assertNotIn('--cron', cmd)
        # Verify ISO timestamp format in --at value
        self.assertRegex(cmd, r'--at \S*T15:00:00')

    def test_at_noon_is_one_shot(self):
        parsed = parse('at noon')
        self.assertTrue(parsed['one_shot'])
        self.assertEqual(parsed['freq_type'], 'at_clock')
        cmd = build_command(parsed)
        self.assertIn('--at', cmd)
        self.assertIn('--delete-after-run', cmd)
        self.assertRegex(cmd, r'--at \S*T12:00:00')

    def test_daily_at_3pm_still_repeating(self):
        parsed = parse('daily at 3pm')
        self.assertFalse(parsed['one_shot'])
        self.assertEqual(parsed['freq_type'], 'daily')
        cmd = build_command(parsed)
        self.assertIn('--cron "0 15 * * *"', cmd)
        self.assertNotIn('--delete-after-run', cmd)

    def test_no_time_no_keyword_falls_back_to_daily(self):
        parsed = parse('remind me about something')
        self.assertEqual(parsed['freq_type'], 'daily')
        self.assertFalse(parsed['one_shot'])


class TestShellEscaping(unittest.TestCase):
    def test_name_with_semicolon(self):
        parsed = parse('daily reminder at 8am')
        parsed['name'] = 'test; rm -rf /'
        cmd = build_command(parsed)
        # shlex.quote wraps in single quotes — semicolon is safely quoted
        self.assertIn("'test; rm -rf /'", cmd)
        # Verify it's passed as --name value (not bare)
        self.assertIn("--name 'test; rm -rf /'", cmd)

    def test_name_with_single_quote(self):
        parsed = parse('daily reminder at 8am')
        parsed['name'] = "it's a test"
        cmd = build_command(parsed)
        # shlex.quote escapes single quotes
        self.assertNotIn("it's", cmd.replace("it'\\''s", ''))

    def test_destination_with_special_chars(self):
        parsed = parse('daily reminder at 8am')
        parsed['destination'] = '$(whoami)'
        cmd = build_command(parsed)
        # Must be quoted, not bare
        self.assertIn("'$(whoami)'", cmd)

    def test_channel_is_quoted(self):
        parsed = parse('daily reminder at 8am on telegram')
        cmd = build_command(parsed)
        # Channel value should be shell-quoted
        self.assertRegex(cmd, r'--channel \S+')

    def test_message_is_quoted(self):
        parsed = parse('daily reminder at 8am')
        cmd = build_command(parsed)
        self.assertIn('--message', cmd)
        # Message should be a single shell token after --message
        # (shlex.quote wraps in single quotes)
        self.assertRegex(cmd, r"--message '")


if __name__ == '__main__':
    unittest.main()
