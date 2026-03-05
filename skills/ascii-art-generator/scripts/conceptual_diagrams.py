#!/usr/bin/env python3
"""
Conceptual Diagrams for ASCII Art Generator

Provides functions for creating flowcharts, mind maps, and process diagrams
using ASCII characters.
"""

def create_flowchart(steps, connections=None, direction='vertical'):
    """
    Create a simple flowchart.
    
    Args:
        steps: List of step descriptions
        connections: List of (from_index, to_index, label) tuples
        direction: Flow direction ('vertical' or 'horizontal')
    
    Returns:
        Flowchart as ASCII art
    """
    if connections is None:
        connections = [(i, i+1, '') for i in range(len(steps)-1)]
    
    if direction == 'vertical':
        return _create_vertical_flowchart(steps, connections)
    else:
        return _create_horizontal_flowchart(steps, connections)

def _create_vertical_flowchart(steps, connections):
    """Create vertical flowchart."""
    result = []
    max_width = max(len(step) for step in steps) + 4
    
    for i, step in enumerate(steps):
        # Create step box
        box = _create_step_box(step, max_width)
        result.append(box)
        
        # Add connection if not last step
        if i < len(steps) - 1:
            # Find connection label
            label = ''
            for conn in connections:
                if conn[0] == i and conn[1] == i+1:
                    label = conn[2]
                    break
            
            # Add arrow
            arrow = ' ' * (max_width // 2) + '↓'
            if label:
                arrow += f' {label}'
            result.append(arrow)
    
    return '\n'.join(result)

def _create_horizontal_flowchart(steps, connections):
    """Create horizontal flowchart."""
    result = []
    step_height = 3  # Each step takes 3 lines
    
    # Prepare step boxes
    step_boxes = []
    for step in steps:
        box_lines = _create_step_box(step, len(step) + 4).split('\n')
        step_boxes.append(box_lines)
    
    # Calculate total width needed
    max_box_width = max(len(line) for box in step_boxes for line in box)
    spacing = 4
    
    # Create each row
    for row in range(step_height):
        line = ''
        for i, box in enumerate(step_boxes):
            if row < len(box):
                line += box[row]
            else:
                line += ' ' * max_box_width
            
            # Add connection arrow between boxes
            if i < len(step_boxes) - 1:
                if row == 1:  # Middle row gets arrow
                    line += ' → '
                else:
                    line += '   '
        
        result.append(line)
    
    # Add connection labels below
    for conn in connections:
        if conn[2]:  # Has label
            from_idx, to_idx, label = conn
            # Calculate position for label
            pos = from_idx * (max_box_width + spacing) + max_box_width // 2 + 1
            label_line = ' ' * pos + f'({label})'
            result.append(label_line)
    
    return '\n'.join(result)

def _create_step_box(text, width):
    """Create a box for a flowchart step."""
    padding = width - len(text) - 2
    left_pad = padding // 2
    right_pad = padding - left_pad
    
    top = '┌' + '─' * (width - 2) + '┐'
    middle = '│' + ' ' * left_pad + text + ' ' * right_pad + '│'
    bottom = '└' + '─' * (width - 2) + '┘'
    
    return top + '\n' + middle + '\n' + bottom

def create_mind_map(central_idea, branches):
    """
    Create a mind map.
    
    Args:
        central_idea: Central idea/topic
        branches: List of (branch_label, sub_branches) tuples
    
    Returns:
        Mind map as ASCII art
    """
    result = []
    
    # Central idea
    central_width = len(central_idea) + 4
    result.append(' ' * (central_width // 2) + '○')
    result.append(' ' * (central_width // 2) + '│')
    result.append(' ' * ((central_width - len(central_idea)) // 2) + f'[{central_idea}]')
    
    # Calculate positions for branches
    total_branches = len(branches)
    branch_positions = []
    
    for i, (branch_label, sub_branches) in enumerate(branches):
        # Main branch line
        angle = i * (360 / total_branches)
        if angle < 90 or angle > 270:
            # Right side
            line = '─' * 5 + '╮'
        else:
            # Left side
            line = '╭' + '─' * 5
        
        # Position calculation
        if total_branches == 1:
            pos = central_width // 2
        elif total_branches == 2:
            if i == 0:
                pos = central_width // 2 - 3
                line = '╭' + '─' * 5
            else:
                pos = central_width // 2 + 3
                line = '─' * 5 + '╮'
        else:
            # Simplified positioning for demo
            pos = central_width // 2 + (i - total_branches // 2) * 8
        
        branch_positions.append((pos, line, branch_label, sub_branches))
    
    # Sort by position
    branch_positions.sort(key=lambda x: x[0])
    
    # Draw branches
    for pos, line, label, sub_branches in branch_positions:
        # Find empty line to draw on
        line_index = 0
        while line_index < len(result) and len(result[line_index]) < pos + len(line):
            line_index += 1
        
        # Ensure we have enough lines
        while len(result) <= line_index:
            result.append('')
        
        # Ensure line is long enough
        while len(result[line_index]) < pos + len(line):
            result[line_index] += ' '
        
        # Draw branch line
        result[line_index] = result[line_index][:pos] + line + result[line_index][pos+len(line):]
        
        # Add branch label
        label_line_index = line_index + 1
        while len(result) <= label_line_index:
            result.append('')
        
        while len(result[label_line_index]) < pos + len(line) // 2:
            result[label_line_index] += ' '
        
        result[label_line_index] = result[label_line_index][:pos + len(line) // 2] + label
    
    return '\n'.join(result)

def create_process_diagram(process_name, stages, feedback_loops=None):
    """
    Create a process diagram with stages and optional feedback loops.
    
    Args:
        process_name: Name of the process
        stages: List of stage names
        feedback_loops: List of (from_stage, to_stage, label) tuples
    
    Returns:
        Process diagram as ASCII art
    """
    result = []
    
    # Process title
    result.append(f"Process: {process_name}")
    result.append('=' * (len(process_name) + 9))
    result.append('')
    
    # Create stages
    stage_boxes = []
    max_stage_width = max(len(stage) for stage in stages) + 4
    
    for i, stage in enumerate(stages):
        box = _create_stage_box(stage, i+1, max_stage_width)
        stage_boxes.append(box.split('\n'))
    
    # Arrange stages in a row
    for row in range(5):  # Each box is 5 lines high
        line = ''
        for box in stage_boxes:
            if row < len(box):
                line += box[row]
            else:
                line += ' ' * max_stage_width
            line += '    '  # Spacing between boxes
        
        result.append(line.rstrip())
    
    # Add forward arrows between stages
    arrow_line = ''
    for i in range(len(stages)):
        arrow_line += ' ' * (max_stage_width // 2)
        if i < len(stages) - 1:
            arrow_line += '────→'
        else:
            arrow_line += ' ' * 5
        arrow_line += '    '
    
    result.append(arrow_line.rstrip())
    
    # Add feedback loops if any
    if feedback_loops:
        result.append('')
        result.append('Feedback Loops:')
        
        for from_stage, to_stage, label in feedback_loops:
            if from_stage > to_stage:
                # Backward loop
                loop = f"Stage {to_stage+1} ←── {label} ──→ Stage {from_stage+1}"
            else:
                # Forward loop
                loop = f"Stage {from_stage+1} ──→ {label} ──→ Stage {to_stage+1}"
            
            result.append('  ' + loop)
    
    return '\n'.join(result)

def _create_stage_box(stage_name, stage_num, width):
    """Create a box for a process stage."""
    title = f"Stage {stage_num}"
    content = stage_name
    
    title_padding = width - len(title) - 2
    title_left = title_padding // 2
    title_right = title_padding - title_left
    
    content_padding = width - len(content) - 2
    content_left = content_padding // 2
    content_right = content_padding - content_left
    
    top = '┌' + '─' * (width - 2) + '┐'
    title_line = '│' + ' ' * title_left + title + ' ' * title_right + '│'
    separator = '├' + '─' * (width - 2) + '┤'
    content_line = '│' + ' ' * content_left + content + ' ' * content_right + '│'
    bottom = '└' + '─' * (width - 2) + '┘'
    
    return top + '\n' + title_line + '\n' + separator + '\n' + content_line + '\n' + bottom

def create_timeline(events, dates=None):
    """
    Create a timeline diagram.
    
    Args:
        events: List of event descriptions
        dates: Optional list of dates corresponding to events
    
    Returns:
        Timeline as ASCII art
    """
    result = []
    
    # Timeline axis
    timeline_length = 50
    result.append('─' * timeline_length)
    
    # Add events
    for i, event in enumerate(events):
        position = int((i / max(1, len(events) - 1)) * (timeline_length - 1))
        
        # Create event marker
        marker_line = ' ' * position + '│'
        
        # Add date if available
        if dates and i < len(dates):
            date_str = f" {dates[i]}"
            marker_line += date_str
        
        result.append(marker_line)
        
        # Add event description
        event_line = ' ' * position + '○ ' + event
        result.append(event_line)
        
        # Add spacing
        if i < len(events) - 1:
            result.append('')
    
    return '\n'.join(result)

def create_venn_diagram(sets, labels, overlap_labels=None):
    """
    Create a simple Venn diagram (2 or 3 sets).
    
    Args:
        sets: Number of sets (2 or 3)
        labels: List of set labels
        overlap_labels: Dictionary of overlap region labels
    
    Returns:
        Venn diagram as ASCII art
    """
    if sets == 2:
        return _create_venn_2(labels, overlap_labels)
    elif sets == 3:
        return _create_venn_3(labels, overlap_labels)
    else:
        return "Venn diagrams only support 2 or 3 sets."

def _create_venn_2(labels, overlap_labels):
    """Create 2-set Venn diagram."""
    result = []
    
    # Diagram
    result.append('   ┌──────┐         ┌──────┐')
    result.append('   │      │         │      │')
    result.append('   │  A   │┌──────┐│  B   │')
    result.append('   │      ││  AB  ││      │')
    result.append('   └──────┘└──────┘└──────┘')
    
    # Labels
    if len(labels) >= 2:
        result.append('')
        result.append(f"A = {labels[0]}")
        result.append(f"B = {labels[1]}")
        
        if overlap_labels and 'AB' in overlap_labels:
            result.append(f"AB = {overlap_labels['AB']}")
    
    return '\n'.join(result)

def _create_venn_3(labels, overlap_labels):
    """Create 3-set Venn diagram."""
    result = []
    
    # Diagram
    result.append('   ┌──────┐')
    result.append('   │      │')
    result.append('   │  A   │┌──────┐')
    result.append('   │      ││      │')
    result.append('   └──────┘│  B   │┌──────┐')
    result.append('            │      ││      │')
    result.append('   ┌──────┐│      ││  C   │')
    result.append('   │  ABC │└──────┘│      │')
    result.append('   │      │         └──────┘')
    result.append('   └──────┘')
    
    # Labels
    if len(labels) >= 3:
        result.append('')
        result.append(f"A = {labels[0]}")
        result.append(f"B = {labels[1]}")
        result.append(f"C = {labels[2]}")
        
        if overlap_labels:
            for key, value in overlap_labels.items():
                result.append(f"{key} = {value}")
    
    return '\n'.join(result)

if __name__ == "__main__":
    # Test the functions
    print("Vertical Flowchart:")
    steps = ["Start", "Process Data", "Make Decision", "End"]
    print(create_flowchart(steps, [(0, 1, ''), (1, 2, 'Data ready'), (2, 3, 'Decision made')]))
    print("\n" + "="*60 + "\n")
    
    print("Horizontal Flowchart:")
    print(create_flowchart(steps, direction='horizontal'))
    print("\n" + "="*60 + "\n")
    
    print("Simple Mind Map:")
    branches = [
        ("Ideas", ["Brainstorm", "Research"]),
        ("Plan", ["Schedule", "Resources"]),
        ("Execute", ["Implement", "Test"])
    ]
    print(create_mind_map("Project", branches))
    print("\n" + "="*60 + "\n")
    
    print("Process Diagram:")
    stages = ["Input", "Process", "Output", "Review"]
    feedback = [(3, 1, "Refine")]
    print(create_process_diagram("Data Analysis", stages, feedback))
    print("\n" + "="*60 + "\n")
    
    print("Timeline:")
    events = ["Project Start", "First Milestone", "Testing Phase", "Launch"]
    dates = ["2026-01-01", "2026-02 -15", "2026-03-01", "2026-03-15"]
    print(create_timeline(events, dates))
    print("\n" + "="*60 + "\n")
    
    print("Venn Diagram (2 sets):")
    labels = ["Machine Learning", "Data Science"]
    overlaps = {"AB": "Statistical Models"}
    print(create_venn_diagram(2, labels, overlaps))
    print("\n" + "="*60 + "\n")
    
    print("Venn Diagram (3 sets):")
    labels = ["Art", "Technology", "Philosophy"]
    overlaps = {"AB": "Digital Art", "BC": "AI Ethics", "AC": "Aesthetics", "ABC": "AI Art"}
    print(create_venn_diagram(3, labels, overlaps))