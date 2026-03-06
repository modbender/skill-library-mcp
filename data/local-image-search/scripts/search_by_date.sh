#!/bin/bash
# Search images by date
# Usage: search_by_date.sh <today|week|month> [directory]

PERIOD="$1"
DIR="${2:-$HOME/Pictures}"

if [ -z "$PERIOD" ]; then
    echo "Usage: $0 <today|week|month> [directory]"
    echo "Example: $0 week ~/Pictures"
    exit 1
fi

case "$PERIOD" in
    today)
        mdfind -onlyin "$DIR" "kMDItemContentTypeTree == 'public.image' && kMDItemFSContentChangeDate > $time.today()"
        ;;
    week)
        mdfind -onlyin "$DIR" "kMDItemContentTypeTree == 'public.image' && kMDItemFSContentChangeDate > $time.now(-604800)"
        ;;
    month)
        mdfind -onlyin "$DIR" "kMDItemContentTypeTree == 'public.image' && kMDItemFSContentChangeDate > $time.this_month()"
        ;;
    year)
        mdfind -onlyin "$DIR" "kMDItemContentTypeTree == 'public.image' && kMDItemFSContentChangeDate > $time.this_year()"
        ;;
    *)
        echo "Unknown period: $PERIOD"
        echo "Use: today, week, month, or year"
        exit 1
        ;;
esac
