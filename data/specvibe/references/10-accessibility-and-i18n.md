# Reference: 10 - Accessibility (a11y) and Internationalization (i18n)

Building for a global audience means ensuring everyone can use your application, regardless of ability or language.

## 1. Accessibility (a11y)

Accessibility is the practice of making your web applications usable by as many people as possible. It is a legal and ethical requirement in many countries.

- **Standard**: Adhere to the **Web Content Accessibility Guidelines (WCAG) 2.1**, aiming for Level AA compliance.
- **Semantic HTML**: Use HTML elements for their correct purpose. Use `<nav>`, `<main>`, `<aside>`, `<header>`, `<footer>`, and `<button>`, not just `<div>` and `<span>`.
- **Keyboard Navigation**: Ensure all interactive elements (links, buttons, form inputs) are focusable and usable with only a keyboard.
- **Alternative Text**: Provide descriptive `alt` text for all images.
- **ARIA Roles**: Use Accessible Rich Internet Applications (ARIA) roles and attributes where necessary to provide additional context to screen readers, but prioritize using correct semantic HTML first.
- **Automated Testing**: Use tools like **axe** in your CI/CD pipeline to automatically catch common accessibility violations.

## 2. Internationalization (i18n)

Internationalization is the process of designing your application so that it can be adapted to various languages and regions without engineering changes.

- **Use a Library**: Use a dedicated i18n library for your frontend framework (e.g., `react-i18next` for React).
- **Extract All Strings**: Do not hardcode any user-visible strings in your code. Store them in locale-specific JSON files.

    ```javascript
    // Bad: Hardcoded string
    return <button>Submit</button>;

    // Good: Using i18n library
    import { useTranslation } from 'react-i18next';
    const { t } = useTranslation();
    return <button>{t('common.submit')}</button>;
    ```

    ```json
    // public/locales/en/common.json
    {
      "submit": "Submit"
    }

    // public/locales/es/common.json
    {
      "submit": "Enviar"
    }
    ```

- **Formatting**: Use the `Intl` object in JavaScript for formatting dates, times, numbers, and currencies according to the user's locale.
