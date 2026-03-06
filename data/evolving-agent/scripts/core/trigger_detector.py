#!/usr/bin/env python3
"""
Evolution Trigger Detector

Determines when to trigger skill evolution based on session context.
"""


def extract_session_summary(context: str) -> dict:
    """
    Extract session summary from conversation context.

    Args:
        context: Full conversation text

    Returns:
        dict with attempts, success, feedback
    """
    summary = {
        'attempts': 1,
        'success': False,
        'feedback': None
    }

    context_lower = context.lower()

    # Count attempts (look for "attempt", "try", "失败", "错误")
    attempt_keywords = ['attempt', 'try', '尝试', 'fail', '错误', 'error']
    attempts = sum(context_lower.count(keyword) for keyword in attempt_keywords)
    if attempts > 0:
        summary['attempts'] = attempts + 1  # +1 for initial attempt

    # Detect success (look for "成功", "完成", "done", "success", "完成")
    success_keywords = ['success', '成功', '完成', 'done', 'work', 'working']
    if any(keyword in context_lower for keyword in success_keywords):
        summary['success'] = True

    # Extract user feedback (look for user statements with keywords)
    feedback_keywords = ['记住', '以后', '保存', '重要', 'remember', 'save', 'important']
    for line in context.split('\n'):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in feedback_keywords):
            # Remove "用户:" prefix if present
            feedback = line.strip()
            if feedback.startswith('用户:') or feedback.startswith('user:'):
                feedback = feedback.split(':', 1)[1].strip()
            summary['feedback'] = feedback
            break

    return summary


def should_trigger_evolution(session_summary: dict) -> bool:
    """
    Determine if evolution should be triggered based on session summary.

    Args:
        session_summary: dict with keys:
            - attempts: number of fix attempts made
            - success: whether the task was completed successfully
            - feedback: user's explicit feedback (optional)

    Returns:
        bool: True if evolution should be triggered
    """
    # Condition 1: Complex bug fix (multiple attempts)
    if session_summary.get('attempts', 1) > 1:
        return True

    # Condition 2: User explicit feedback
    feedback = session_summary.get('feedback', '')
    if feedback and any(keyword in feedback.lower() for keyword in ['记住', '以后', '保存', '重要', 'remember', 'save', 'important']):
        return True

    # Condition 3: Successful completion with specific indicators
    if session_summary.get('success', False):
        # Could add more sophisticated conditions here
        pass

    return False


if __name__ == "__main__":
    import json

    # Test extract_session_summary
    print("Testing extract_session_summary():")
    context = '''
用户: 帮我修复这个 bug
助手: 让我看看...第一次尝试失败
用户: 还是不行
助手: 让我换个方法...第二次尝试失败
用户: 再试试
助手: 这次成功了！
用户: 太好了，记住这个解决方案
'''
    summary = extract_session_summary(context)
    print(f"  Extracted: {summary}")
    print()

    # Test should_trigger_evolution
    print("Testing should_trigger_evolution():")
    test_cases = [
        ({'attempts': 3, 'success': True}, True),
        ({'attempts': 1, 'success': True}, False),
        ({'attempts': 1, 'success': True, 'feedback': '记住这个'}, True),
        ({'attempts': 1, 'success': True, 'feedback': '很好'}, False),
    ]

    for test_summary, expected in test_cases:
        result = should_trigger_evolution(test_summary)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {test_summary} -> {result} (expected: {expected})")
