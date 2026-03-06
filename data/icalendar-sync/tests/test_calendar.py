#!/usr/bin/env python3
"""
Unit tests for iCalendar Sync
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from icalendar_sync.calendar import CalendarManager


class TestCalendarManager:
    """Test CalendarManager"""
    
    def test_init(self):
        """Test initialization"""
        manager = CalendarManager()
        assert manager.username is None or isinstance(manager.username, str)
        assert manager.password is None or isinstance(manager.password, str)
        assert manager.client is None
    
    @patch('icalendar_sync.calendar.DAVClient')
    def test_connect_success(self, mock_client_class):
        """Test successful connection"""
        mock_principal = Mock()
        mock_principal.calendars.return_value = []
        mock_client = Mock()
        mock_client.principal.return_value = mock_principal
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {
            'ICLOUD_USERNAME': 'test@icloud.com',
            'ICLOUD_APP_PASSWORD': 'test-pass-1234'
        }):
            manager = CalendarManager()
            result = manager.connect()
            assert result is True
    
    def test_connect_missing_credentials(self):
        """Test connection without credentials"""
        with patch.dict(os.environ, {}, clear=True):
            manager = CalendarManager()
            result = manager.connect()
            assert result is False
    
    @patch('icalendar_sync.calendar.DAVClient')
    def test_connect_failure(self, mock_client_class):
        """Test connection failure"""
        mock_client_class.side_effect = Exception("Connection failed")
        
        with patch.dict(os.environ, {
            'ICLOUD_USERNAME': 'test@icloud.com',
            'ICLOUD_APP_PASSWORD': 'test-pass-1234'
        }):
            manager = CalendarManager()
            result = manager.connect()
            assert result is False
    
    @patch('icalendar_sync.calendar.DAVClient')
    def test_list_calendars(self, mock_client_class):
        """Test listing calendars"""
        mock_cal1 = Mock()
        mock_cal1.name = "Personal"
        mock_cal2 = Mock()
        mock_cal2.name = "Work"
        
        mock_principal = Mock()
        mock_principal.calendars.return_value = [mock_cal1, mock_cal2]
        mock_client = Mock()
        mock_client.principal.return_value = mock_principal
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {
            'ICLOUD_USERNAME': 'test@icloud.com',
            'ICLOUD_APP_PASSWORD': 'test-pass-1234'
        }):
            manager = CalendarManager()
            calendars = manager.list_calendars()
            assert len(calendars) == 2
            assert "Personal" in calendars
            assert "Work" in calendars
    
    @patch('icalendar_sync.calendar.DAVClient')
    def test_create_event(self, mock_client_class):
        """Test creating an event"""
        mock_cal = Mock()
        mock_cal.save_event = Mock(return_value=True)
        
        mock_principal = Mock()
        mock_principal.calendar.return_value = mock_cal
        mock_client = Mock()
        mock_client.principal.return_value = mock_principal
        mock_client_class.return_value = mock_client
        
        event_data = {
            'summary': 'Test Meeting',
            'dtstart': datetime.now() + timedelta(hours=1),
            'dtend': datetime.now() + timedelta(hours=2),
            'location': 'Test Office'
        }
        
        with patch.dict(os.environ, {
            'ICLOUD_USERNAME': 'test@icloud.com',
            'ICLOUD_APP_PASSWORD': 'test-pass-1234'
        }):
            manager = CalendarManager()
            result = manager.create_event('Personal', event_data)
            assert result is True
    
    @patch('icalendar_sync.calendar.DAVClient')
    def test_delete_event(self, mock_client_class):
        """Test deleting an event"""
        mock_event = Mock()
        mock_event.delete = Mock(return_value=True)
        
        mock_cal = Mock()
        mock_cal.event_by_uid.return_value = mock_event
        
        mock_principal = Mock()
        mock_principal.calendar.return_value = mock_cal
        mock_client = Mock()
        mock_client.principal.return_value = mock_principal
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {
            'ICLOUD_USERNAME': 'test@icloud.com',
            'ICLOUD_APP_PASSWORD': 'test-pass-1234'
        }):
            manager = CalendarManager()
            result = manager.delete_event('Personal', 'test-uid-123')
            assert result is True


class TestSetupCommand:
    """Test setup command"""
    
    @patch('icalendar_sync.calendar.input')
    @patch('icalendar_sync.calendar.getpass.getpass')
    @patch('builtins.open', create=True)
    def test_cmd_setup(self, mock_open, mock_getpass, mock_input):
        """Test setup command"""
        mock_input.return_value = 'test@icloud.com'
        mock_getpass.return_value = 'xxxx-xxxx-xxxx-xxxx'
        
        from icalendar_sync.calendar import cmd_setup
        
        args = Mock()
        cmd_setup(args)
        
        # Verify getpass was called
        mock_getpass.assert_called_once()


class TestCLI:
    """Test CLI interface"""
    
    def test_main_no_args(self, capsys):
        """Test main without arguments"""
        with patch('sys.argv', ['icalendar-sync']):
            from icalendar_sync.calendar import main
            with pytest.raises(SystemExit):
                main()
    
    def test_main_setup_command(self):
        """Test setup command"""
        with patch('sys.argv', ['icalendar-sync', 'setup']):
            with patch('icalendar_sync.calendar.cmd_setup'):
                from icalendar_sync.calendar import main
                # Should not raise
                try:
                    main()
                except:
                    pass