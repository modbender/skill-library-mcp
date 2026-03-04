import datetime
import re
import os

def get_macronutrient_targets():
    """Read macronutrient targets from USER.md"""
    try:
        with open("/root/clawd/USER.md", "r") as f:
            content = f.read()
        
        protein_match = re.search(r"蛋白质[:：]\s*(\d+)\s*g", content)
        carbs_match = re.search(r"碳水[:：]\s*(\d+)\s*g", content)
        fat_match = re.search(r"脂肪[:：]\s*(\d+)\s*g", content)
        calorie_match = re.search(r"每天[:：]\s*(\d+)\s*大卡", content)
        
        return {
            'protein': int(protein_match.group(1)) if protein_match else None,
            'carbs': int(carbs_match.group(1)) if carbs_match else None,
            'fat': int(fat_match.group(1)) if fat_match else None,
            'calories': int(calorie_match.group(1)) if calorie_match else 1650
        }
    except Exception as e:
        print(f"Error reading targets: {e}")
        return {'protein': None, 'carbs': None, 'fat': None, 'calories': 1650}

def parse_existing_entries(content):
    """Parse existing food entries to calculate totals"""
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    
    # Look for patterns like: 热量: ~100 kcal 或 100 大卡
    calorie_pattern = r'(?:热量|大卡|kcal)[:：]?\s*~?(\d+)\s*(?:kcal|大卡)'
    protein_pattern = r'蛋白质[:：]?\s*~?(\d+(?:\.\d+)?)\s*g'
    carbs_pattern = r'碳水(?:化合物)?[:：]?\s*~?(\d+(?:\.\d+)?)\s*g'
    fat_pattern = r'脂肪[:：]?\s*~?(\d+(?:\.\d+)?)\s*g'
    
    for match in re.finditer(calorie_pattern, content, re.IGNORECASE):
        total_calories += int(match.group(1))
    
    for match in re.finditer(protein_pattern, content, re.IGNORECASE):
        total_protein += float(match.group(1))
    
    for match in re.finditer(carbs_pattern, content, re.IGNORECASE):
        total_carbs += float(match.group(1))
    
    for match in re.finditer(fat_pattern, content, re.IGNORECASE):
        total_fat += float(match.group(1))
    
    return {
        'calories': total_calories,
        'protein': total_protein,
        'carbs': total_carbs,
        'fat': total_fat
    }

def format_meal_entry(meal_name, food_item, nutrition_info, notes=""):
    """Format a meal entry with nutrition information"""
    entry = f"\n## {meal_name}\n\n"
    entry += f"**食物**：{food_item}\n\n"
    entry += "**估算营养**：\n"
    entry += f"- 热量：~{nutrition_info['calories']} kcal\n"
    entry += f"- 蛋白质：{nutrition_info['protein']}g\n"
    entry += f"- 碳水：{nutrition_info['carbs']}g\n"
    entry += f"- 脂肪：{nutrition_info['fat']}g\n"
    if notes:
        entry += f"\n**备注**：{notes}\n"
    return entry

def format_summary(totals, targets):
    """Format the daily summary section"""
    summary = "\n---\n\n## 今日摄入汇总\n\n"
    
    # Calculate remaining
    remaining_calories = targets['calories'] - totals['calories'] if targets['calories'] else None
    remaining_protein = targets['protein'] - totals['protein'] if targets['protein'] else None
    remaining_carbs = targets['carbs'] - totals['carbs'] if targets['carbs'] else None
    remaining_fat = targets['fat'] - totals['fat'] if targets['fat'] else None
    
    # Summary table with targets
    summary += "| 项目 | 目标 | 已摄入 | 剩余 |\n"
    summary += "|------|------|--------|------|\n"
    
    cal_target_str = f"{targets['calories']} kcal" if targets['calories'] else "-"
    cal_remaining_str = f"{remaining_calories:.0f} kcal" if remaining_calories is not None else "-"
    summary += f"| 热量 | {cal_target_str} | {totals['calories']:.0f} kcal | {cal_remaining_str} |\n"
    
    if targets['protein']:
        summary += f"| 蛋白质 | {targets['protein']}g | {totals['protein']:.1f}g | {remaining_protein:.1f}g |\n"
    if targets['carbs']:
        summary += f"| 碳水 | {targets['carbs']}g | {totals['carbs']:.1f}g | {remaining_carbs:.1f}g |\n"
    if targets['fat']:
        summary += f"| 脂肪 | {targets['fat']}g | {totals['fat']:.1f}g | {remaining_fat:.1f}g |\n"
    
    return summary

def update_memory(meal_name, food_item, nutrition_info, notes=""):
    """Update the daily memory file with meal information"""
    # Get the current date
    now = datetime.datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    filename = f"/root/clawd/memory/{date_string}.md"
    obsidian_filename = f"/root/clawd/obsidian-vault/memory/{date_string}.md"

    # Get targets
    targets = get_macronutrient_targets()

    # Read the file (if it exists)
    try:
        with open(filename, "r") as f:
            content = f.read()
    except FileNotFoundError:
        content = f"# {date_string} 饮食记录\n"

    # Remove existing summary if present
    summary_start = content.find("\n---\n\n## 今日摄入汇总")
    if summary_start != -1:
        content = content[:summary_start]

    # Add the new meal entry
    meal_entry = format_meal_entry(meal_name, food_item, nutrition_info, notes)
    content += meal_entry

    # Calculate totals including the new meal
    totals = parse_existing_entries(content)
    
    # Add new meal to totals
    totals['calories'] += nutrition_info.get('calories', 0)
    totals['protein'] += nutrition_info.get('protein', 0)
    totals['carbs'] += nutrition_info.get('carbs', 0)
    totals['fat'] += nutrition_info.get('fat', 0)

    # Add summary
    summary = format_summary(totals, targets)
    content += summary

    # Write the updated content back to the file
    try:
        with open(filename, "w") as f:
            f.write(content)
        print(f"Successfully added '{food_item}' to {filename}")
        print(f"\n今日累计: 热量 {totals['calories']:.0f} kcal | 蛋白质 {totals['protein']:.1f}g | 碳水 {totals['carbs']:.1f}g | 脂肪 {totals['fat']:.1f}g")
        
        # Show remaining
        if targets['calories']:
            remaining_cal = targets['calories'] - totals['calories']
            print(f"剩余额度: {remaining_cal:.0f} kcal")
        
        # Copy to Obsidian vault
        try:
            import shutil
            shutil.copy2(filename, obsidian_filename)
            print(f"✅ 已同步到 Obsidian: {obsidian_filename}")
        except Exception as e:
            print(f"⚠️ Obsidian 同步失败: {e}")
        
        # Push to GitHub
        try:
            import subprocess
            obsidian_dir = "/root/clawd/obsidian-vault"
            date_str = now.strftime("%Y-%m-%d")
            
            # Git add, commit, push
            subprocess.run(["git", "-C", obsidian_dir, "add", "-A"], check=True, capture_output=True)
            subprocess.run(["git", "-C", obsidian_dir, "commit", "-m", f"Update diet log for {date_str}", "--allow-empty"], check=False, capture_output=True)
            result = subprocess.run(["git", "-C", obsidian_dir, "push", "origin", "master"], check=False, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ 已推送到 GitHub")
            else:
                # Try pull and push again
                subprocess.run(["git", "-C", obsidian_dir, "pull", "origin", "master", "--rebase"], check=False, capture_output=True)
                subprocess.run(["git", "-C", obsidian_dir, "push", "origin", "master"], check=False, capture_output=True)
                print(f"✅ 已推送到 GitHub (after rebase)")
        except Exception as e:
            print(f"⚠️ GitHub 推送失败: {e}")
    except Exception as e:
        print(f"Error writing to file: {e}")

if __name__ == '__main__':
    meal_name = input("Enter meal name (e.g., 早餐/午餐/晚餐): ")
    food_item = input("Enter food item: ")
    nutrition_info = {
        "calories": int(input("Calories: ")),
        "protein": float(input("Protein (g): ")),
        "carbs": float(input("Carbs (g): ")),
        "fat": float(input("Fat (g): "))
    }
    notes = input("Notes (optional): ")
    update_memory(meal_name, food_item, nutrition_info, notes)
