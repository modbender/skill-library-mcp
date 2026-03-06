def classify_status(status: int) -> str:
    if status in (401,):
        return "unauthorized"
    if status in (403,):
        return "forbidden"
    if status in (404,):
        return "not_found"
    if status in (429,):
        return "rate_limited"
    if status >= 500:
        return "server_error"
    return f"http_{status}"


def classify_error(exc: Exception) -> str:
    s = str(exc).lower()
    if "timeout" in s:
        return "timeout"
    if "certificate" in s or "ssl" in s:
        return "ssl_error"
    if "name or service not known" in s or "dns" in s:
        return "dns_error"
    if "403" in s:
        return "forbidden"
    if "429" in s:
        return "rate_limited"
    if "5" in s and "error" in s:
        return "server_error"
    if "login" in s or "sign in" in s:
        return "login_required"
    return "unknown_error"
