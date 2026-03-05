#!/usr/bin/env bash
# Usage: ./generate_sop.sh "Task Name" "Step1" "Step2" ...

TASK_NAME=$1
shift
mkdir -p SOPs
FILE="SOPs/${TASK_NAME// /_}.md"

echo "# SOP: $TASK_NAME" > "$FILE"
echo "Generated on: $(date)" >> "$FILE"
echo -e "\n## Workflow Steps\n" >> "$FILE"

COUNT=1
for step in "$@"; do
  echo "$COUNT. $step" >> "$FILE"
  ((COUNT++))
done

echo -e "\n## Success Criteria\n- Task completed as described above.\n- Result verified by agent." >> "$FILE"
echo "✅ SOP created at: $FILE"
