#!/usr/bin/env python3
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

SRC_URL = "https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/refs/heads/master/accelerated-domains.china.conf"
OUT_PATH = "output/alidns_accelerated_domains_cn.module"
DNS = "https://dns.alidns.com/dns-query"

# dnsmasq-china-list 典型行：
# server=/example.com/114.114.114.114
PAT = re.compile(r"^\s*server\s*=\s*/([^/]+)/")

def fetch(url: str) -> str:
    with urllib.request.urlopen(url, timeout=45) as r:
        return r.read().decode("utf-8", errors="replace")

def is_domain(s: str) -> bool:
    # 允许 punycode / 常规域名
    return bool(re.fullmatch(r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}", s)) and ".." not in s and not s.startswith("-")

def main() -> int:
    text = fetch(SRC_URL)

    domains = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = PAT.match(line)
        if not m:
            continue
        d = m.group(1).strip().lower().rstrip(".")
        if is_domain(d):
            domains.add(d)

    # 输出：同时包含根域与子域通配，避免 root 漏掉
    lines_out = []
    for d in sorted(domains):
        lines_out.append(f"{d} = server:{DNS}")
        lines_out.append(f"*.{d} = server:{DNS}")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    os.makedirs("output", exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("#!name=AliDNS for accelerated-domains.china.conf\n")
        f.write("#!desc=Auto-generated from felixonmars/dnsmasq-china-list accelerated-domains.china.conf\n")
        f.write(f"#!updated={now}\n\n")
        f.write("[Host]\n")
        f.write("\n".join(lines_out))
        f.write("\n")

    print(f"wrote {OUT_PATH} domains={len(domains)} host_lines={len(lines_out)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
