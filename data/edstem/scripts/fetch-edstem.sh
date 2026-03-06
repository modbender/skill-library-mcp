#!/bin/bash
# Fetch EdStem threads for any course
# Usage: ./fetch-edstem.sh <course_id> [output_dir]
#
# Examples:
#   ./fetch-edstem.sh 92041
#   ./fetch-edstem.sh 92041 ./ml-course

if [ $# -lt 1 ]; then
    echo "Usage: $0 <course_id> [output_dir]"
    echo ""
    echo "Examples:"
    echo "  $0 92041"
    echo "  $0 92041 ./ml-course"
    exit 1
fi

COURSE_ID=$1
OUTPUT_DIR=${2:-"./edstem-${COURSE_ID}"}
ED_TOKEN="dptT0u.adkdSAKHoFQpttiLLmuxaJRqxekDmNMIxaYZgLUn"

mkdir -p "$OUTPUT_DIR"

echo "Fetching threads for course $COURSE_ID..."

# Fetch threads
curl -s -H "Authorization: Bearer $ED_TOKEN" \
  "https://us.edstem.org/api/courses/$COURSE_ID/threads?limit=20&sort=new" \
  > "$OUTPUT_DIR/threads.json"

# Extract thread IDs and fetch details
jq -r '.threads[] | "\(.id)|\(.number)|\(.title)"' "$OUTPUT_DIR/threads.json" | while IFS='|' read -r thread_id thread_num title; do
  echo "  Thread #$thread_num: $title"
  
  # Fetch full thread
  curl -s -H "Authorization: Bearer $ED_TOKEN" \
    "https://us.edstem.org/api/threads/$thread_id" \
    > "$OUTPUT_DIR/thread-$thread_num-raw.json"
done

echo "✅ Done! Threads saved to $OUTPUT_DIR/"
echo "Note: For formatted markdown with staff differentiation, use fetch-edstem.py instead"
