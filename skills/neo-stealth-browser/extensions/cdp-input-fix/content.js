// Patch MouseEvent and PointerEvent constructors so that CDP-dispatched
// clicks carry realistic screenX / screenY values.
//
// Chromium bug (crbug.com/40280325): Input.dispatchMouseEvent sets
// screenX/screenY equal to clientX/clientY, which makes screenY < 100
// in most cases. Cloudflare Turnstile checks for this inside its iframe.
//
// Fix: override the constructors to compute screen coordinates from the
// window's position on the physical display.

(function () {
  'use strict';

  function patchedInit(OriginalClass) {
    const Original = OriginalClass;
    function Patched(type, init) {
      if (init && typeof init === 'object') {
        const clientX = init.clientX || 0;
        const clientY = init.clientY || 0;

        // Chrome exposes window.screenX/screenY for the browser window's
        // position on the monitor. outerWidth - innerWidth gives the chrome
        // (dev-tools, scrollbar, etc.) offset on the X axis; similarly for Y
        // with outerHeight - innerHeight (which includes the tab bar / URL bar).
        let offsetX = window.screenX + (window.outerWidth - window.innerWidth);
        let offsetY = window.screenY + (window.outerHeight - window.innerHeight);

        // Fallback for headless or environments where screenX/screenY are 0
        if (window.screenX === 0 && window.screenY === 0) {
          offsetX = 100;
          offsetY = 200;
        }

        // Only patch if screenX/screenY were not explicitly set to a
        // realistic value by the caller.
        if (!('screenX' in init) || init.screenX === init.clientX) {
          init.screenX = offsetX + clientX;
        }
        if (!('screenY' in init) || init.screenY === init.clientY) {
          init.screenY = offsetY + clientY;
        }
      }
      return new Original(type, init);
    }

    Patched.prototype = Original.prototype;
    Object.defineProperty(Patched, 'name', { value: Original.name });

    // Preserve static properties / constants
    for (const key of Object.getOwnPropertyNames(Original)) {
      if (['prototype', 'length', 'name'].includes(key)) continue;
      try {
        const desc = Object.getOwnPropertyDescriptor(Original, key);
        if (desc) Object.defineProperty(Patched, desc.configurable ? key : key, desc);
      } catch (_) { /* skip non-configurable */ }
    }

    return Patched;
  }

  try {
    window.MouseEvent = patchedInit(window.MouseEvent);
  } catch (_) {}

  try {
    window.PointerEvent = patchedInit(window.PointerEvent);
  } catch (_) {}
})();
