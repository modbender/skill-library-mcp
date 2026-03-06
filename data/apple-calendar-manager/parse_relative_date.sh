#!/bin/bash

RELATIVE_DATE="$1"
TIME_HHMM="$2"  # Format HH:MM

# Извлекаем часы и минуты из TIME_HHMM
HOUR=${TIME_HHMM%:*}
MINUTE=${TIME_HHMM#*:}

# Получаем текущую дату
CURRENT_DATE_UNIX=$(date +%s)

# Определяем целевую дату
if [ "$RELATIVE_DATE" == "today" ]; then
    TARGET_DATE_UNIX=$CURRENT_DATE_UNIX
elif [ "$RELATIVE_DATE" == "tomorrow" ]; then
    TARGET_DATE_UNIX=$(date -v+1d +%s)
elif [ "$RELATIVE_DATE" == "day after tomorrow" ]; then
    TARGET_DATE_UNIX=$(date -v+2d +%s)
else
    # Если RELATIVE_DATE - это конкретный день недели, например "понедельник"
    # Для MacOS `date` поддерживает -v (adjust date by amount) и `next weekday`
    if [[ "$RELATIVE_DATE" =~ ^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$ ]]; then
        # Переводим на английский, чтобы date понимал
        RELATIVE_DATE_EN=$(echo "$RELATIVE_DATE" | sed 's/понедельник/monday/' | \
                                                     sed 's/вторник/tuesday/' | \
                                                     sed 's/среда/wednesday/' | \
                                                     sed 's/четверг/thursday/' | \
                                                     sed 's/пятница/friday/' | \
                                                     sed 's/суббота/saturday/' | \
                                                     sed 's/воскресенье/sunday/')
        TARGET_DATE_UNIX=$(date -v"next $RELATIVE_DATE_EN" +%s)
    else
        echo "Error: Unknown relative date or invalid format: $RELATIVE_DATE" >&2
        exit 1
    fi
fi

# Формируем дату с учетом времени
# `date` умеет комбинировать, но удобнее это делать в несколько этапов
# Сначала получаем целевую дату в YYYY-MM-DD
TARGET_DATE_YYYYMMDD=$(date -r "$TARGET_DATE_UNIX" "+%Y%m%d")

# Собираем полную строку YYYYMMDDHHMMSS
echo "${TARGET_DATE_YYYYMMDD}${HOUR}${MINUTE}00"