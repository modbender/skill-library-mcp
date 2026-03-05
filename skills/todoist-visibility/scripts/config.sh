# Todoist 可见性 Skill 配置模板
# 复制此文件为 ~/.todoist_config.sh 并填入实际值

# Todoist API Token
# 获取地址: https://todoist.com/app/settings/integrations/developer
export TODOIST_TOKEN="your-api-token-here"

# 项目 ID（在 Todoist URL 中可以看到，或通过 API 查询）
export TODOIST_PROJECT_ID="your-project-id-here"

# Section IDs（需要在 Todoist 项目中创建对应的 section）
# 🟡 In Progress
export SECTION_IN_PROGRESS="section-id-here"

# 🟠 Waiting
export SECTION_WAITING="section-id-here"

# 🟢 Done
export SECTION_DONE="section-id-here"

# 使用方法:
# 1. 复制此文件: cp config.template.sh ~/.todoist_config.sh
# 2. 编辑 ~/.todoist_config.sh 填入实际值
# 3. 在使用脚本前加载配置: source ~/.todoist_config.sh
