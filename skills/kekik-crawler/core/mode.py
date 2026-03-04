def apply_mode_limits(mode: str, max_pages: int, per_domain_delay: float):
    if mode == "deep":
        return max(max_pages, 180), max(per_domain_delay, 0.45)
    if mode == "wide":
        return max(max_pages, 120), max(per_domain_delay, 0.20)
    return max_pages, per_domain_delay


def link_limit_for_mode(mode: str) -> int:
    if mode == "deep":
        return 40
    if mode == "wide":
        return 120
    return 80
