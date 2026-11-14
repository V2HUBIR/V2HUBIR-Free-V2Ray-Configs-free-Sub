# -*- coding: utf-8 -*-
import re, time, json, base64, socket, random, html
from concurrent.futures import ThreadPoolExecutor
import requests

TARGET_CONFIGS = 200
CONNECT_TIMEOUT = 4

# لیست کانال‌های تلگرام پایه
TG_SOURCES = [
    "SOSkeyNET", "ConfigsHUB", "FarahVPN", "Farah_VPN", "ConfigsHUB2",
    "ConfigX2ray", "v2ray1_ng", "AarazV2ray", "V2rayBaaz", "V2rayEnglish",
    "prrofile_purple", "SimChin_ir", "IRAN_V2RAY1", "Leviko_V2ray",
    "Outline_Vpn", "v2nodes", "SPARTAN_YT", "BigSmoke_Config", "FarazV2ray"
]

# لینک لیست کانال‌های تلگرام خارجی (پشتیبانی از لینک معمولی و Raw گیت‌هاب)
EXTERNAL_TG_LISTS = [
    "https://raw.githubusercontent.com/coldwater-10/V2rayCollector/main/channels.txt"
]

# منابع مستقیم گیت‌هاب و ساب‌لینک‌ها
GITHUB_SOURCES = [
    "https://v2freehub-sub.v2freehub.workers.dev/",
    "https://sub.vlessfo.ru/vlessforu/working_configs.txt",
    "https://raw.githubusercontent.com/0xRadikal/Free-v2ray-Configs/main/verified/configs_base64.txt",
    "https://raw.githubusercontent.com/0xRadikal/Free-v2ray-Configs/main/all/configs.txt",
    "https://raw.githubusercontent.com/0xRadikal/Free-v2ray-Configs/main/all_configs.txt",
    "https://raw.githubusercontent.com/SoliSpirit/v2ray-configs/main/all_configs.txt",
    "https://raw.githubusercontent.com/SoliSpirit/SolVPN/main/Subscribes/sub1.txt",
    "https://raw.githubusercontent.com/SoliSpirit/SolVPN/main/Subscribes/sub2.txt",
    "https://raw.githubusercontent.com/SoliSpirit/SolVPN/main/Subscribes/sub3.txt",
    "https://raw.githubusercontent.com/SoliSpirit/SolVPN/main/Subscribes/sub4.txt",
    "https://raw.githubusercontent.com/SoliSpirit/SolVPN/main/Subscribes/sub5.txt",
    "https://raw.githubusercontent.com/SoliSpirit/SolVPN/main/Protocols/vless.txt",
    "https://raw.githubusercontent.com/SoliSpirit/SolVPN/main/Protocols/vmess.txt",
    "https://raw.githubusercontent.com/SoliSpirit/SolVPN/main/Protocols/trojan.txt",
    "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/super-sub.txt",
    "https://raw.githubusercontent.com/coldwater-10/V2ray-Config-Lite/main/Sub1.txt",
    "https://raw.githubusercontent.com/coldwater-10/V2ray-Config-Lite/main/Sub2.txt",
    "https://raw.githubusercontent.com/ShatakVPN/ConfigForge-V2Ray/main/configs/ir/all.txt",
    "https://raw.githubusercontent.com/ShatakVPN/ConfigForge-V2Ray/main/configs/ir/light.txt",
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/refs/heads/main/V2Ray-Config-By-EbraSha.txt",
    "https://raw.githubusercontent.com/expressalaki/ExpressVPN/refs/heads/main/configs2.txt",
    "https://raw.githubusercontent.com/expressalaki/ExpressVPN/refs/heads/main/configs.txt",
    "https://raw.githubusercontent.com/v2FreeHub/v2hub-configs/refs/heads/main/Sub-AutoUpdate",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/refs/heads/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/V2RAYCONFIGSPOOL/V2RAY_SUB/main/all_configs.txt",
    "https://raw.githubusercontent.com/MahanKenway/Freedom-V2Ray/main/configs/mix_sub.txt",
    "https://raw.githubusercontent.com/youfoundamin/V2rayCollector/main/vless_iran.txt",
    "https://raw.githubusercontent.com/youfoundamin/V2rayCollector/main/mixed_iran.txt",
    "https://raw.githubusercontent.com/Firmfox/proxify/main/v2ray_configs/subscriptions/subscription-1.txt",
    "https://raw.githubusercontent.com/Firmfox/proxify/main/v2ray_configs/subscriptions/subscription-2.txt",
    "https://raw.githubusercontent.com/Firmfox/proxify/main/v2ray_configs/subscriptions/subscription-3.txt"
]

URI_RE = re.compile(r"(?:vless|vmess|ss|trojan|hysteria2|hy2)://[^\s<>\"']+")

def config_key(uri):
    return uri.split("#", 1)[0].strip().rstrip("/")

def extract(text):
    if not text: return []
    text = html.unescape(text)
    res = URI_RE.findall(text)
    if not res:
        try:
            pad = text.strip() + "=" * (-len(text.strip()) % 4)
            decoded = base64.b64decode(pad.encode()).decode("utf-8", errors="ignore")
            res = URI_RE.findall(html.unescape(decoded))
        except Exception: pass
    return res

def get_all_tg_channels():
    channels = list(TG_SOURCES)
    for url in EXTERNAL_TG_LISTS:
        raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        try:
            r = requests.get(raw_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                for line in r.text.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    line = re.sub(r"^(?:https?://)?t\.me/(?:s/)?", "", line)
                    line = line.lstrip("@").split("/")[0].split("?")[0].strip()
                    if line and re.match(r"^[a-zA-Z0-9_]{4,32}$", line):
                        channels.append(line)
        except Exception:
            pass
    return list(dict.fromkeys(channels))

def fetch_url(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200: return extract(r.text)
    except: pass
    return []

def fetch_tg(ch):
    return fetch_url(f"https://t.me/s/{ch}")

def parse_host_port(uri):
    try:
        scheme, rest = uri.split("://", 1)
        if scheme == "vmess":
            pad = rest.split("#", 1)[0]
            pad += "=" * (-len(pad) % 4)
            j = json.loads(base64.urlsafe_b64decode(pad.encode()).decode("utf-8", errors="ignore"))
            return j.get("add"), int(j.get("port", 0))
        hostpart = rest.split("#", 1)[0].split("@")[-1].split("?")[0].split("/")[0]
        if hostpart.startswith("["): host, port = hostpart[1:hostpart.index("]")], 443
        elif ":" in hostpart: host, port = hostpart.rsplit(":", 1)
        else: host, port = hostpart, 443
        return host, int(port)
    except: return None, None

def test_config(uri):
    host, port = parse_host_port(uri)
    if not host or not port: return None
    start = time.time()
    try:
        with socket.create_connection((host, int(port)), timeout=CONNECT_TIMEOUT):
            ping = int((time.time() - start) * 1000)
            return (uri, ping)
    except: return None

def rename_uri(uri, idx, ping):
    tag = f"⚡ @V2HUBIR | Server {idx} ({ping}ms)"
    try:
        scheme, rest = uri.split("://", 1)
        if scheme == "vmess":
            pad = rest.split("#", 1)[0]
            pad += "=" * (-len(pad) % 4)
            j = json.loads(base64.urlsafe_b64decode(pad.encode()).decode("utf-8", errors="ignore"))
            j["ps"] = tag
            enc = base64.urlsafe_b64encode(json.dumps(j, ensure_ascii=False).encode("utf-8")).decode("utf-8").rstrip("=")
            return f"vmess://{enc}"
        else:
            base = rest.split("#", 1)[0].rstrip("/")
            return f"{scheme}://{base}#{tag.replace(' ', '%20')}"
    except: return uri

if __name__ == "__main__":
    all_tg_channels = get_all_tg_channels()
    print(f"Collecting from {len(all_tg_channels)} Telegram channels and {len(GITHUB_SOURCES)} GitHub sources...")
    
    pool = []
    with ThreadPoolExecutor(max_workers=30) as ex:
        for res in ex.map(fetch_tg, all_tg_channels): pool += res
        for res in ex.map(fetch_url, GITHUB_SOURCES): pool += res

    unique_map = {}
    for c in pool:
        k = config_key(c)
        if k not in unique_map and len(c) < 750:
            unique_map[k] = c

    candidates = list(unique_map.values())
    random.shuffle(candidates)

    valid_configs = []
    with ThreadPoolExecutor(max_workers=60) as ex:
        for i in range(0, len(candidates), 100):
            batch = candidates[i:i+100]
            for res in ex.map(test_config, batch):
                if res:
                    valid_configs.append(res)
                    if len(valid_configs) >= TARGET_CONFIGS: break
            if len(valid_configs) >= TARGET_CONFIGS: break

    valid_configs.sort(key=lambda x: x[1])
    final_list = [rename_uri(u, idx+1, p) for idx, (u, p) in enumerate(valid_configs[:TARGET_CONFIGS])]

    plain_text = "\n".join(final_list)
    b64_text = base64.b64encode(plain_text.encode("utf-8")).decode("utf-8")

    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(plain_text)
    with open("sub_base64.txt", "w", encoding="utf-8") as f:
        f.write(b64_text)

    print(f"Successfully saved {len(final_list)} configs.")
