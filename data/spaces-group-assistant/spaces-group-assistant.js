// Spaces Group Assistant skill for OpenClaw: отвечает на все обращения в спецгруппе (для любого пользователя), но календарь блокирует

const FULL_POWER_GROUPS = new Set([-4842304105]);
const CALENDAR_KEYWORDS = ["календар", "calendar", "встреч", "meeting", "gcalcli", "расписание"];

function isCalendarQuery(text) {
    if (!text) return false;
    const lc = text.toLowerCase();
    return CALENDAR_KEYWORDS.some(key => lc.includes(key));
}

module.exports = async function spacesGroupAssistant(event, params, tools) {
    const chat_id = event.chat && event.chat.id ? event.chat.id : undefined;
    const is_private = (event.chat && event.chat.type === 'private');
    const text = (event.text || "").toString();

    // Блокируем календарь везде, кроме приватного чата
    if (isCalendarQuery(text)) {
        if (!is_private) {
            return {text: "⛔️ Календарь доступен только в приватном чате. Обратись ко мне лично для информации о встречах или напоминаниях."};
        }
        // В личке — ОК
        return null;
    }

    // Полный доступ — групповой ассистент для указанного chat_id и лички
    if (FULL_POWER_GROUPS.has(chat_id) || is_private) {
        // Нет фильтра по user — реагируем на всех (group assistant mode)
        return null;   // Пусть ядро обработает как обычный ассистент (workspace, KB, memory, логи и т.д.)
    } else {
        // Остальные группы — только публичная информация, web-поиск, help, безопасная заглушка
        return {text: "У меня нет доступа к приватным заметкам, файлам памяти и логам в этом чате. Попробуй задать вопрос в личке или в спецгруппе."};
    }
}
