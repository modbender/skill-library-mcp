---
name: SKILL.md
description: "Depending on the execution environment, Microsoft JsRT may be referred to as:"
---

# SKILL.md

## jsrt-claw

### Overview

**JSRT** enables control of a Windows system using the built-in **Microsoft JsRT (JavaScript Runtime)**.

Depending on the execution environment, Microsoft JsRT may be referred to as:

* `WSH`
* `Windows Scripting Host`
* `cscript`
* `jscript.dll`

On classic Windows systems, the JScript engine is implemented in **`jscript.dll`** (JScript 5.x). When running via `cscript` or `wscript`, this engine is typically used unless hosted by another environment.

This skill generates and executes a **single `.js` file** that interacts with Windows using COM objects and built-in scripting capabilities.

---

## Execution Flow

1. Create a **single JavaScript file** using all references described in this document.
2. Perform Windows operations using COM objects.
3. Execute the script:

```cmd
cscript YOUR_JS_FILE.js
```

---

## Available Windows Capabilities

### 1. File System Access

COM objects:

* `Scripting.FileSystemObject`
* `ADODB.Stream`

Typical usage:

* Reading and writing files
* Creating and deleting directories
* Handling text or binary streams

---

### 2. System & Runtime Information

COM objects and functions:

* `WScript.Shell`
* `WbemScripting.SWbemLocator`
* `GetObject`

Example:

```js
GetObject("winmgmts:{impersonationLevel=impersonate}!\\\\"
          + this.computer + "\\" + this.namespace);
```

Use cases:

* Executing Windows shell commands
* Querying WMI
* Retrieving system configuration
* Accessing environment variables

---

### 3. HTTP Communication

Possible COM objects (availability depends on installed MSXML/WinHTTP components):

* `Microsoft.XMLHTTP`
* `WinHttp.WinHttpRequest.5.1`
* `Msxml3.XMLHTTP`
* `Msxml2.XMLHTTP`
* `Msxml2.XMLHTTP.7.0`
* `Msxml2.XMLHTTP.6.0`
* `Msxml2.XMLHTTP.5.0`
* `Msxml2.XMLHTTP.4.0`
* `Msxml2.XMLHTTP.3.0`
* `Msxml2.XMLHTTP.2.6`
* `Msxml2.ServerXMLHTTP`
* `Msxml2.ServerXMLHTTP.6.0`
* `Msxml2.ServerXMLHTTP.5.0`
* `Msxml2.ServerXMLHTTP.4.0`
* `Msxml2.ServerXMLHTTP.3.0`

Fallback loading is strongly recommended.

---

### 4. Microsoft Office Automation (If Installed)

* `Excel.Application`
* `PowerPoint.Application`
* `Word.Application`
* `Outlook.Application`
* Other Office-related COM objects

---

## Required COM Object Loader (With Fallback Support)

All COM objects must be instantiated using the following `CreateObject` function.

It supports:

* Single ProgID
* Multiple ProgIDs (fallback chain)
* Automatic retry until a working object is found

```js
if (typeof CreateObject === "undefined") {
    var CreateObject = function(progId, serverName, callback) {
        var progIds = (progId instanceof Array ? progId : [progId]);

        for (var i = 0; i < progIds.length; i++) {
            try {
                var obj = CreateObject.make(progIds[i], serverName);
                if (typeof callback === "function") {
                    callback(obj, progIds[i]);
                }
                return obj;
            } catch (e) {
                // Try next ProgID
            }
        }
        throw new Error("Unable to create COM object from provided ProgIDs.");
    };

    CreateObject.make = function(p, s) {
        if (typeof WScript !== "undefined") {
            if ("CreateObject" in WScript) {
                return WScript.CreateObject(p, s);
            } else {
                throw new Error("Built-in loader not available.");
            }
        } else if (typeof ActiveXObject !== "undefined") {
            return new ActiveXObject(p);
        } else {
            throw new Error("Could not find a loader");
        }
    };
}
```

---

### Fallback Example (XMLHTTP)

```js
var xhr = CreateObject([
    "Msxml2.XMLHTTP.6.0",
    "Msxml2.XMLHTTP.3.0",
    "Msxml2.XMLHTTP",
    "Microsoft.XMLHTTP",
    "WinHttp.WinHttpRequest.5.1"
]);
```

The loader attempts each ProgID in order until one succeeds.

---

## JavaScript Runtime Version Detection

Use the following function to determine the runtime:

```js
function getProcessVersion() {
    var getIEVersion = function() {
        var rv = -1;
        if (navigator.appName == 'Microsoft Internet Explorer') {
            var ua = navigator.userAgent;
            var re  = new RegExp("MSIE ([0-9]{1,}[\\.0-9]{0,})");
            if (re.exec(ua) != null)
                rv = parseFloat(RegExp.$1);
        }
        return rv;
    };

    if (typeof WScript !== "undefined") {
        return "Microsoft JScript " + WScript.Version;
    } else if (typeof navigator !== "undefined") {
        return (function(rv) {
            return "MSIE" + (rv < 0 ? '' : (' ' + rv));
        })(getIEVersion());
    }
}
```

---

## Polyfill Support

Because `jscript.dll` (JScript 5.x) does not support modern ECMAScript features, polyfills may be required.

### WSH JScript Compatibility

| JScript Version | Introduced with IE | Example User-Agent                                                |
| --------------- | -----------------: | ----------------------------------------------------------------- |
| 5.6.x           |             IE 6.0 | `Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)`         |
| 5.7.x           |             IE 7.0 | `Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)`              |
| 5.8.x           |             IE 8.0 | `Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)` |

---

## Polyfill Discovery

Available polyfills can be checked at:

```
https://cdnjs.cloudflare.com/polyfill/
```

---

## Fetching Polyfills

### `features` Parameter Format

The `features` parameter must be a **comma-separated list of feature keywords**:

```
features=feature1,feature2,feature3
```

In URL query strings, commas must be URL-encoded:

```
features=feature1%2Cfeature2%2Cfeature3
```

Example:

* Conceptual:

  ```
  features=default,es2015
  ```

* URL-encoded:

  ```
  features=default%2Ces2015
  ```

### Request Example

```text
GET https://cdnjs.cloudflare.com/polyfill/v3/polyfill.min.js?version=4.8.0&features=default%2Ces2015
User-Agent: Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)
```

The `User-Agent` must match the detected JScript compatibility level.

---

## Compatibility Strategy

1. Detect runtime using `getProcessVersion()`
2. Instantiate COM objects using fallback arrays
3. Identify unsupported JavaScript features
4. Request polyfills using comma-separated `features`
5. Inject polyfills before executing dependent logic
6. Execute Windows automation logic safely under `jscript.dll`

---

## Real-World Example

A real open-source project that applies this environment in practice is **WelsonJS**.

WelsonJS:

* Runs on Windows using the built-in JScript runtime (`jscript.dll`)
* Uses COM objects extensively
* Implements fallback loading patterns
* Uses **core-js** (formerly known as Babel polyfills) to bridge modern JavaScript features into legacy JScript environments

If you need concrete usage examples, implementation patterns, or real source code references, use a search function to look up:

* WelsonJS project information
* WelsonJS source code
* WelsonJS core-js integration

Reviewing the WelsonJS project will provide practical references that can help when implementing JSRT-based automation code.

---

## Summary

JSRT provides:

* Direct Windows automation
* COM-based system control
* WMI querying
* HTTP communication
* Office automation
* Multi-ProgID fallback support
* Polyfill-based compatibility for `jscript.dll`

It is optimized for legacy Windows scripting environments while maintaining cross-version compatibility through structured fallback and polyfill strategies.
