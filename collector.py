# -*- coding: utf-8 -*-
import re, time, json, base64, socket, random, html
from concurrent.futures import ThreadPoolExecutor
import requests

TARGET_CONFIGS = 200
CONNECT_TIMEOUT = 4

# لیست کامل کانال‌های تلگرام (پایه + موارد اضافه‌شده)
TG_SOURCES = [
    "SOSkeyNET", "ConfigsHUB", "FarahVPN", "Farah_VPN", "ConfigsHUB2",
    "ConfigX2ray", "v2ray1_ng", "AarazV2ray", "V2rayBaaz", "V2rayEnglish",
    "prrofile_purple", "SimChin_ir", "IRAN_V2RAY1", "Leviko_V2ray",
    "Outline_Vpn", "v2nodes", "SPARTAN_YT", "BigSmoke_Config", "FarazV2ray",
    "v2ray_outlineir", "PrivateVPNs", "V2rayNG_Fast", "FreeV2rays", "DailyV2RY"
]

# لینک لیست کانال‌های تلگرام خارجی
EXTERNAL_TG_LISTS = [
    "https://raw.githubusercontent.com/coldwater-10/V2rayCollector/main/channels.txt"
]

# منابع مستقیم گیت‌هاب و ساب‌لینک‌ها (کامل‌شده با منابع جدید)
GITHUB_SOURCES = [
    "https://raw.githubusercontent.com/noahclanman/free-xray-gcp/main/output/top100.txt",
    "https://raw.githubusercontent.com/noahclanman/free-xray-gcp/main/output/fast/configs.txt",
    "https://raw.githubusercontent.com/noahclanman/free-xray-gcp/main/output/transports/ws_tls.txt",
    "https://raw.githubusercontent.com/mohammadaz2/v2rayConfigsForYou/main/configs.txt",
    "https://raw.githubusercontent.com/mohammadaz2/v2rayConfigsForYou/main/sub/vless.txt",
    "https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/all_servers.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub1.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub2.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Splitted-By-Protocol/vless.txt",
    "https://matinghanbari.github.io/v2ray-configs/index.html",
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
    "https://raw.githubusercontent.com/SoliSpirit/SolVPN/main/Subscribes/sub6.txt",
    "https://raw.githubusercontent.com/SoliSpirit/SolVPN/main/Subscribes/sub7.txt",
    "https://raw.githubusercontent.com/SoliSpirit/SolVPN/main/Subscribes/sub8.txt",
    "https://raw.githubusercontent.com/SoliSpirit/SolVPN/main/Subscribes/sub9.txt",
    "https://raw.githubusercontent.com/SoliSpirit/SolVPN/main/Subscribes/sub10.txt",
    "https://raw.githubusercontent.com/SoliSpirit/SolVPN/main/Protocols/vless.txt",
    "https://raw.githubusercontent.com/SoliSpirit/SolVPN/main/Protocols/vmess.txt",
    "https://raw.githubusercontent.com/SoliSpirit/SolVPN/main/Protocols/shadowsocks.txt",
    "https://raw.githubusercontent.com/SoliSpirit/SolVPN/main/Protocols/trojan.txt",
    "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/super-sub.txt",
    "https://raw.githubusercontent.com/coldwater-10/V2ray-Config-Lite/main/Sub1.txt",
    "https://raw.githubusercontent.com/coldwater-10/V2ray-Config-Lite/main/Sub2.txt",
    "https://raw.githubusercontent.com/ShatakVPN/ConfigForge-V2Ray/main/configs/ir/all.txt",
    "https://raw.githubusercontent.com/ShatakVPN/ConfigForge-V2Ray/main/configs/ir/light.txt",
    "https://raw.githubusercontent.com/FNET00bot/FNET00/Config/Main",
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/refs/heads/main/V2Ray-Config-By-EbraSha.txt",
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/all_extracted_configs.txt",
    "https://raw.githubusercontent.com/expressalaki/ExpressVPN/refs/heads/main/configs2.txt",
    "https://raw.githubusercontent.com/expressalaki/ExpressVPN/refs/heads/main/configs.txt",
    "https://raw.githubusercontent.com/v2FreeHub/v2hub-configs/refs/heads/main/Sub-AutoUpdate",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/refs/heads/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/V2RAYCONFIGSPOOL/V2RAY_SUB/main/all_configs.txt",
    "https://raw.githubusercontent.com/MahanKenway/Freedom-V2Ray/main/configs/mix_sub.txt",
    "https://raw.githubusercontent.com/youfoundamin/V2rayCollector/main/vless_iran.txt",
    "https://raw.githubusercontent.com/youfoundamin/V2rayCollector/main/mixed_iran.txt",
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/xray/normal/vless",
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/xray/normal/reality",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vless",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/reality",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/trojan",
    "https://raw.githubusercontent.com/Kwinwoo/config-v2ray/main/vless.txt",
    "https://raw.githubusercontent.com/Kwinwoo/config-v2ray/main/reality.txt",
    "https://raw.githubusercontent.com/amirhosein-v2ray/Free-V2ray-Config/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/Firmfox/proxify/main/v2ray_configs/subscriptions/subscription-1.txt",
    "https://raw.githubusercontent.com/Firmfox/proxify/main/v2ray_configs/subscriptions/subscription-2.txt",
    "https://raw.githubusercontent.com/Firmfox/proxify/main/v2ray_configs/subscriptions/subscription-3.txt",
    "https://raw.githubusercontent.com/Firmfox/proxify/main/v2ray_configs/subscriptions/subscription-4.txt",
    "https://raw.githubusercontent.com/Firmfox/proxify/main/v2ray_configs/subscriptions/subscription-5.txt",
    "https://raw.githubusercontent.com/Firmfox/proxify/main/v2ray_configs/subscriptions/subscription-6.txt",
    "https://raw.githubusercontent.com/Firmfox/proxify/main/v2ray_configs/subscriptions/subscription-7.txt",
    "https://raw.githubusercontent.com/pog7x/vpn-configs/refs/heads/master/githubmirror/3.txt",
    "https://raw.githubusercontent.com/pog7x/vpn-configs/refs/heads/master/githubmirror/4.txt",
    "https://raw.githubusercontent.com/pog7x/vpn-configs/refs/heads/master/githubmirror/5.txt",
    "https://raw.githubusercontent.com/pog7x/vpn-configs/refs/heads/master/githubmirror/7.txt",
    "https://raw.githubusercontent.com/pog7x/vpn-configs/refs/heads/master/githubmirror/8.txt",
    "https://raw.githubusercontent.com/pog7x/vpn-configs/refs/heads/master/githubmirror/9.txt",
    "https://raw.githubusercontent.com/pog7x/vpn-configs/refs/heads/master/githubmirror/10.txt",
    "https://raw.githubusercontent.com/pog7x/vpn-configs/refs/heads/master/githubmirror/11.txt",
    "https://raw.githubusercontent.com/pog7x/vpn-configs/refs/heads/master/githubmirror/15.txt",
    "https://raw.githubusercontent.com/pog7x/vpn-configs/refs/heads/master/githubmirror/16.txt",
    "https://raw.githubusercontent.com/pog7x/vpn-configs/refs/heads/master/githubmirror/17.txt",
    "https://raw.githubusercontent.com/pog7x/vpn-configs/refs/heads/master/githubmirror/18.txt",
    "https://raw.githubusercontent.com/pog7x/vpn-configs/refs/heads/master/githubmirror/20.txt",
    "https://raw.githubusercontent.com/pog7x/vpn-configs/refs/heads/master/githubmirror/21.txt",
    "https://raw.githubusercontent.com/pog7x/vpn-configs/refs/heads/master/githubmirror/22.txt",
    "https://raw.githubusercontent.com/pog7x/vpn-configs/refs/heads/master/githubmirror/23.txt",
    "https://raw.githubusercontent.com/pog7x/vpn-configs/refs/heads/master/githubmirror/24.txt"
]

URI_RE = re.compile(r"(?:vless|vmess|ss|trojan|hysteria2|hy2|hysteria|h2|wireguard|wg|socks5|socks)://[^\s<>\"']+")
GEO_CACHE = {}

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
    bad_words = {"https", "http", "telegram", "channel", "channels", "main", "master"}
    for url in EXTERNAL_TG_LISTS:
        raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        try:
            r = requests.get(raw_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                text = re.sub(r"https?://t\.me/(?:s/)?", " ", r.text)
                tokens = re.findall(r"[a-zA-Z0-9_]{5,32}", text)
                for t in tokens:
                    if t.lower() not in bad_words and not t.isdigit():
                        channels.append(t)
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

def get_location(host):
    if not host:
        return "Unknown", "🌍"
    if host in GEO_CACHE:
        return GEO_CACHE[host]
    try:
        r = requests.get(f"http://ip-api.com/json/{host}", timeout=4).json()
        if r.get("status") == "success":
            country = r.get("country", "Unknown")
            cc = r.get("countryCode", "")
            if cc and len(cc) == 2:
                flag = chr(ord(cc[0].upper()) + 127397) + chr(ord(cc[1].upper()) + 127397)
            else:
                flag = "🌍"
            GEO_CACHE[host] = (country, flag)
            return country, flag
    except Exception:
        pass
    GEO_CACHE[host] = ("Unknown", "🌍")
    return "Unknown", "🌍"

def test_config(uri):
    host, port = parse_host_port(uri)
    if not host or not port: return None
    start = time.time()
    try:
        with socket.create_connection((host, int(port)), timeout=CONNECT_TIMEOUT):
            ping = int((time.time() - start) * 1000)
            return (uri, ping, host)
    except: return None

def rename_uri(uri, idx, flag, country):
    tag = f"{flag} {country} | Telegram: @V2HUBIR #{idx}"
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
    final_list = []
    for idx, (u, _, host) in enumerate(valid_configs[:TARGET_CONFIGS]):
        country, flag = get_location(host)
        final_list.append(rename_uri(u, idx + 1, flag, country))

    plain_text = "\n".join(final_list)
    b64_text = base64.b64encode(plain_text.encode("utf-8")).decode("utf-8")

    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(plain_text)
    with open("sub_base64.txt", "w", encoding="utf-8") as f:
        f.write(b64_text)

    print(f"Successfully saved {len(final_list)} configs.")
