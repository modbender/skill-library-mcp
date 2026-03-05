---
slug: solvecaptcha
display_name: XEvil Captcha Solver
version: 1.0.2
tags: [captcha, xevil, automation, solver]
---
# XEvil Auto-Solver / Авто-Решатель Капчи

## Description / Описание
**[EN]**
This skill integrates an available high-speed XEvil instance to solve various types of CAPTCHAs automatically. It supports standard image CAPTCHAs, ReCaptcha V2/V3, and HCaptcha. Use this skill when you encounter a challenge on a website that requires human verification.

**[RU]**
Этот навык (скилл) интегрирует доступный сервер XEvil для автоматического решения капчи через AI агентов. Поддерживает обычные картинки, ReCaptcha V2/V3 и HCaptcha. Используйте этот навык, когда сталкиваетесь с проверкой "я не робот" или текстовыми картинками на сайтах.

---

## Configuration / Конфигурация
*   **Server / Сервер:** `91.84.99.54`
*   **Port / Порт:** `80`
*   **Protocol:** HTTP (2Captcha Emulation API)

## Capabilities / Возможности
1.  **Image Recognition (Распознавание картинок):**
    *   [EN] Solves alphanumeric text captchas via Base64 upload.
    *   [RU] Решает текстовые/числовые капчи, загруженные в формате Base64.
2.  **Token Solvers (Токенизированные капчи):**
    *   [EN] Solves complex grid/checkbox captchas (ReCaptcha, HCaptcha) by proxying through the XEvil engine.
    *   [RU] Решает сложные задачи (галочки, сетки) проксируя запросы через движок XEvil.

## Usage / Использование

### Step 1: Upload / Шаг 1: Загрузка
**[EN]** Call `uploadCaptcha` with the image (base64) or sitekey. The server returns a Captcha ID.
**[RU]** Вызовите `uploadCaptcha` с картинкой (base64) или sitekey. Сервер вернет ID капчи.

### Step 2: Poll Result / Шаг 2: Проверка
**[EN]** Poll `getCaptchaResult` using the ID until the status is 1 and the solution is returned.
**[RU]** Периодически опрашивайте `getCaptchaResult` используя полученный ID, пока статус не станет 1 и не вернется текст решения.

### Example Prompt for AI / Пример Промпта
> "I have encountered a captcha on this website. Please solve it using the XEvil tool. Here is the sitekey: [SITEKEY] and the URL: [URL]."
>
> "Я наткнулся на капчу на этом сайте. Реши её через XEvil. Вот sitekey: [SITEKEY] и ссылка: [URL]."
