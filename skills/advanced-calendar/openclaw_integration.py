#!/home/ubuntu/.openclaw/workspace/skills/calendar/venv/bin/python3
"""
OpenClaw integration for calendar skill
Handles incoming messages and processes calendar-related intents
"""

import sys
import json
import os
from pathlib import Path

# Add the workspace to the path
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace')

def process_message(user_input):
    """
    Process incoming message and determine if it's a calendar-related request
    """
    # Import our intent handler
    from intent_handler import detect_calendar_intent, handle_calendar_intent
    
    # Detect intent
    intent, confidence = detect_calendar_intent(user_input)
    
    if intent and confidence > 0.6:
        if intent == 'create':
            # For create intent, we might need more info, so return a request for details
            from intent_handler import parse_datetime_from_text, parse_duration_from_text, extract_location_from_text
            date, time = parse_datetime_from_text(user_input)
            duration = parse_duration_from_text(user_input)
            location = extract_location_from_text(user_input)
            
            # Use the rest of the text as title/description
            title_candidates = [word.strip() for word in user_input.split() if len(word.strip()) > 2 and not word.strip().isdigit()]
            title = title_candidates[0] if title_candidates else user_input[:50]
            
            # Check if we have enough information or if we need to ask for more
            if not date or not time:
                return {
                    "response": "我检测到您想创建一个日历事件。请告诉我事件的时间（日期和具体时间）。",
                    "need_details": ["date", "time"],
                    "partial_info": {
                        "title": title,
                        "location": location,
                        "duration": duration
                    }
                }
            else:
                # We have date and time, check if we need reminder info
                from intent_handler import parse_reminder_from_text
                reminder = parse_reminder_from_text(user_input)
                
                if reminder is None:
                    # Ask for reminder preference
                    return {
                        "response": f"我将为您创建事件：{title}\n时间：{date} {time}\n持续：{duration}分钟\n地点：{location}\n\n您希望提前多久收到提醒？（例如：5分钟、1小时、1天等）",
                        "need_details": ["reminder"],
                        "event_data": {
                            "title": title,
                            "date": date,
                            "time": time,
                            "duration": duration,
                            "location": location,
                            "description": user_input
                        }
                    }
                else:
                    # Create the event directly
                    from intent_handler import create_calendar_event
                    result = create_calendar_event(title, date, time, duration, location, user_input, reminder)
                    if result["success"]:
                        return {
                            "response": f"✅ {result['message']}\n{result['details']}",
                            "completed": True
                        }
                    else:
                        return {
                            "response": f"❌ 创建事件失败：{result['error']}",
                            "error": True
                        }
        elif intent == 'list':
            from intent_handler import list_calendar_events
            result = list_calendar_events()
            if result["success"]:
                return {
                    "response": f"📅 您的日历事件：\n{result['events']}",
                    "completed": True
                }
            else:
                return {
                    "response": f"❌ 获取事件列表失败：{result['error']}",
                    "error": True
                }
        elif intent == 'daily_summary':
            from intent_handler import get_daily_summary
            result = get_daily_summary()
            if result["success"]:
                return {
                    "response": result['summary'],
                    "completed": True
                }
            else:
                return {
                    "response": f"❌ 获取今日日程失败：{result['error']}",
                    "error": True
                }
        else:
            # For other intents, return a message saying it's detected but not fully implemented
            return {
                "response": f"我检测到您想进行日历{intent}操作，此功能正在开发中...",
                "intent": intent
            }
    else:
        # Not a calendar-related message
        return {
            "response": None,
            "is_calendar_related": False
        }

def handle_followup(user_input, context):
    """
    Handle follow-up responses when the system was waiting for more information
    """
    if "event_data" in context:
        from intent_handler import parse_reminder_from_text
        
        # User is responding with reminder information
        reminder = parse_reminder_from_text(f"提前{user_input}") or parse_reminder_from_text(user_input)
        
        if reminder is None:
            # Try to interpret the input as a direct time amount
            try:
                if "分钟" in user_input or "min" in user_input.lower():
                    reminder = int(''.join(filter(str.isdigit, user_input)))
                elif "小时" in user_input or "hour" in user_input.lower():
                    hours = int(''.join(filter(str.isdigit, user_input)))
                    reminder = hours * 60
                elif "天" in user_input or "day" in user_input.lower():
                    days = int(''.join(filter(str.isdigit, user_input)))
                    reminder = days * 24 * 60
                else:
                    # Default interpretation - treat as minutes if it's just a number
                    numeric_part = ''.join(filter(str.isdigit, user_input))
                    if numeric_part:
                        reminder = int(numeric_part)
                    else:
                        reminder = 30  # Default to 30 minutes
            except ValueError:
                reminder = 30  # Default to 30 minutes if parsing fails
        
        # Create the event with the provided reminder
        event_data = context["event_data"]
        from intent_handler import create_calendar_event
        result = create_calendar_event(
            event_data["title"],
            event_data["date"],
            event_data["time"],
            event_data["duration"],
            event_data["location"],
            event_data["description"],
            reminder
        )
        
        if result["success"]:
            return {
                "response": f"✅ {result['message']}\n{result['details']}",
                "completed": True
            }
        else:
            return {
                "response": f"❌ 创建事件失败：{result['error']}",
                "error": True
            }
    
    # Check if user is acknowledging a reminder
    user_input_lower = user_input.lower()
    ack_indicators = ['知道了', 'ok', '收到', 'okay', 'ack', 'acknowledged', 'yes', '确认', '确定', '已知悉']
    
    if any(indicator.lower() in user_input_lower for indicator in ack_indicators):
        # Run the acknowledgment processor
        import subprocess
        import os
        script_path = "/home/ubuntu/.openclaw/workspace/calendar_app/process_acknowledgment.py"
        result = subprocess.run([sys.executable, script_path, user_input], capture_output=True, text=True)
        print(f"Acknowledgment processed: {result.stdout.strip()}")
        
        return {
            "response": "✅ 好的，已确认您收到了提醒",
            "acknowledged": True
        }
    
    return {"response": "抱歉，我不清楚您这条消息的上下文。"}

def main():
    """
    Main entry point for OpenClaw integration
    """
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: openclaw_integration.py <message> [context]"}))
        return
    
    user_input = sys.argv[1]
    
    # Check if we have context (for follow-up messages)
    context = {}
    if len(sys.argv) > 2:
        try:
            context = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            context = {}
    
    if context:
        # This is a follow-up message
        result = handle_followup(user_input, context)
    else:
        # This is a new message
        result = process_message(user_input)
    
    # Print result as JSON for OpenClaw to consume
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()