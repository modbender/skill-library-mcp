export const normalizeToken = (input: string) => {
    return (input || '')
        .toLowerCase()
        .replace(/[\s\u3000]/g, '')
        .replace(/[.,!?;:'"()\[\]{}<>，。！？；：“”‘’（）【】《》]/g, '');
};
