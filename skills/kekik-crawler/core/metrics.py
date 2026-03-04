from collections import Counter


class Metrics:
    def __init__(self):
        self.ok = 0
        self.fail = 0
        self.errors = Counter()
        self.domains = Counter()
        self.domain_ok = Counter()
        self.domain_fail = Counter()

    def add_ok(self, domain: str):
        self.ok += 1
        self.domains[domain] += 1
        self.domain_ok[domain] += 1

    def add_fail(self, domain: str, code: str):
        self.fail += 1
        self.domains[domain] += 1
        self.domain_fail[domain] += 1
        self.errors[code] += 1

    def summary(self):
        total = self.ok + self.fail
        rate = (self.ok / total) if total else 0.0
        health = {}
        for d in self.domains:
            ok = self.domain_ok[d]
            fail = self.domain_fail[d]
            t = ok + fail
            health[d] = {"ok": ok, "fail": fail, "rate": round(ok / t, 3) if t else 0.0}

        return {
            "ok": self.ok,
            "fail": self.fail,
            "success_rate": round(rate, 3),
            "errors": dict(self.errors.most_common(10)),
            "top_domains": dict(self.domains.most_common(15)),
            "domain_health": health,
        }
