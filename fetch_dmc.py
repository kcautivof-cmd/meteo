#!/usr/bin/env python3
"""fetch_dmc.py — scrapes DMC Chile WRF forecast and saves dmc_cache.json"""

import json, re, time, datetime, sys, ssl

try:
    import urllib.request as urlreq
    from urllib.error import URLError, HTTPError
except ImportError:
    import urllib2 as urlreq

# SSL context que ignora verificación de certificado (común en CI/CD)
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

REGIONS = ["01a","01b","02","03","04","05","05m","06","07",
           "08a","08b","09","10a","10b","11","12","ip","jf","an"]

BASE_URL = "https://archivos.meteochile.gob.cl/portaldmc/pronosticos/pronosticoRegion.php?reg="

LOCALITIES = [
    {"indice":"visviri",    "ciudad":"Visviri",              "reg":"an",  "lat":-17.594,"lon":-69.476},
    {"indice":"arica",      "ciudad":"Arica",                "reg":"01a", "lat":-18.478,"lon":-70.312},
    {"indice":"putre",      "ciudad":"Putre",                "reg":"01a", "lat":-18.196,"lon":-69.560},
    {"indice":"colchane",   "ciudad":"Colchane",             "reg":"01b", "lat":-19.277,"lon":-68.639},
    {"indice":"iquique",    "ciudad":"Iquique",              "reg":"01b", "lat":-20.216,"lon":-70.153},
    {"indice":"pica",       "ciudad":"Pica",                 "reg":"01b", "lat":-20.491,"lon":-69.329},
    {"indice":"ollague",    "ciudad":"Ollague",              "reg":"02",  "lat":-21.225,"lon":-68.254},
    {"indice":"tocopilla",  "ciudad":"Tocopilla",            "reg":"02",  "lat":-22.092,"lon":-70.197},
    {"indice":"calama",     "ciudad":"Calama",               "reg":"02",  "lat":-22.456,"lon":-68.923},
    {"indice":"snpedro",    "ciudad":"San Pedro de Atacama", "reg":"02",  "lat":-22.911,"lon":-68.201},
    {"indice":"mejillones", "ciudad":"Mejillones",           "reg":"02",  "lat":-23.100,"lon":-70.450},
    {"indice":"antofagasta","ciudad":"Antofagasta",          "reg":"02",  "lat":-23.650,"lon":-70.400},
    {"indice":"taltal",     "ciudad":"Taltal",               "reg":"02",  "lat":-25.408,"lon":-70.485},
    {"indice":"salvador",   "ciudad":"El Salvador",          "reg":"03",  "lat":-26.314,"lon":-69.544},
    {"indice":"chanaral",   "ciudad":"Chanaral",             "reg":"03",  "lat":-26.348,"lon":-70.623},
    {"indice":"caldera",    "ciudad":"Caldera",              "reg":"03",  "lat":-27.067,"lon":-70.825},
    {"indice":"copiapo",    "ciudad":"Copiapo",              "reg":"03",  "lat":-27.366,"lon":-70.332},
    {"indice":"huasco",     "ciudad":"Huasco",               "reg":"03",  "lat":-28.464,"lon":-71.218},
    {"indice":"vallenar",   "ciudad":"Vallenar",             "reg":"03",  "lat":-28.576,"lon":-70.759},
    {"indice":"serena",     "ciudad":"La Serena",            "reg":"04",  "lat":-29.902,"lon":-71.251},
    {"indice":"vicuna",     "ciudad":"Vicuna",               "reg":"04",  "lat":-30.031,"lon":-70.708},
    {"indice":"ovalle",     "ciudad":"Ovalle",               "reg":"04",  "lat":-30.598,"lon":-71.200},
    {"indice":"illapel",    "ciudad":"Illapel",              "reg":"04",  "lat":-31.633,"lon":-71.170},
    {"indice":"vilos",      "ciudad":"Los Vilos",            "reg":"04",  "lat":-31.908,"lon":-71.507},
    {"indice":"papudo",     "ciudad":"Papudo",               "reg":"05",  "lat":-32.507,"lon":-71.441},
    {"indice":"valpo",      "ciudad":"Valparaiso",           "reg":"05",  "lat":-33.047,"lon":-71.613},
    {"indice":"vdelmar",    "ciudad":"Vina del Mar",         "reg":"05",  "lat":-33.024,"lon":-71.552},
    {"indice":"snantonio",  "ciudad":"San Antonio",          "reg":"05",  "lat":-33.593,"lon":-71.607},
    {"indice":"stgoo",      "ciudad":"Santiago Oriente",     "reg":"05m", "lat":-33.437,"lon":-70.650},
    {"indice":"stgoc",      "ciudad":"Santiago Centro",      "reg":"05m", "lat":-33.448,"lon":-70.669},
    {"indice":"stgon",      "ciudad":"Santiago Norte",       "reg":"05m", "lat":-33.366,"lon":-70.676},
    {"indice":"stgos",      "ciudad":"Santiago Sur",         "reg":"05m", "lat":-33.537,"lon":-70.676},
    {"indice":"stgop",      "ciudad":"Santiago Poniente",    "reg":"05m", "lat":-33.456,"lon":-70.751},
    {"indice":"melipilla",  "ciudad":"Melipilla",            "reg":"05m", "lat":-33.690,"lon":-71.215},
    {"indice":"rancagua",   "ciudad":"Rancagua",             "reg":"06",  "lat":-34.170,"lon":-70.740},
    {"indice":"snfernando", "ciudad":"San Fernando",         "reg":"06",  "lat":-34.586,"lon":-70.989},
    {"indice":"stacruz",    "ciudad":"Santa Cruz",           "reg":"06",  "lat":-34.638,"lon":-71.365},
    {"indice":"pichilemu",  "ciudad":"Pichilemu",            "reg":"06",  "lat":-34.392,"lon":-72.006},
    {"indice":"curico",     "ciudad":"Curico",               "reg":"07",  "lat":-34.982,"lon":-71.239},
    {"indice":"talca",      "ciudad":"Talca",                "reg":"07",  "lat":-35.426,"lon":-71.655},
    {"indice":"constitucion","ciudad":"Constitucion",        "reg":"07",  "lat":-35.333,"lon":-72.417},
    {"indice":"linares",    "ciudad":"Linares",              "reg":"07",  "lat":-35.846,"lon":-71.593},
    {"indice":"chillan",    "ciudad":"Chillan",              "reg":"08a", "lat":-36.606,"lon":-72.103},
    {"indice":"concepcion", "ciudad":"Concepcion",           "reg":"08b", "lat":-36.827,"lon":-73.050},
    {"indice":"angeles",    "ciudad":"Los Angeles",          "reg":"08b", "lat":-37.469,"lon":-72.353},
    {"indice":"angol",      "ciudad":"Angol",                "reg":"09",  "lat":-37.798,"lon":-72.716},
    {"indice":"temuco",     "ciudad":"Temuco",               "reg":"09",  "lat":-38.739,"lon":-72.598},
    {"indice":"villarica",  "ciudad":"Villarrica",           "reg":"09",  "lat":-39.285,"lon":-72.227},
    {"indice":"valdivia",   "ciudad":"Valdivia",             "reg":"10a", "lat":-39.814,"lon":-73.245},
    {"indice":"osorno",     "ciudad":"Osorno",               "reg":"10b", "lat":-40.574,"lon":-73.133},
    {"indice":"pmontt",     "ciudad":"Puerto Montt",         "reg":"10b", "lat":-41.469,"lon":-72.942},
    {"indice":"ancud",      "ciudad":"Ancud",                "reg":"10b", "lat":-41.870,"lon":-73.820},
    {"indice":"castro",     "ciudad":"Castro",               "reg":"10b", "lat":-42.482,"lon":-73.764},
    {"indice":"chaiten",    "ciudad":"Chaiten",              "reg":"10b", "lat":-42.915,"lon":-72.707},
    {"indice":"coyhaique",  "ciudad":"Coyhaique",            "reg":"11",  "lat":-45.571,"lon":-72.068},
    {"indice":"balmaceda",  "ciudad":"Balmaceda",            "reg":"11",  "lat":-45.915,"lon":-71.689},
    {"indice":"cochrane",   "ciudad":"Cochrane",             "reg":"11",  "lat":-47.255,"lon":-72.573},
    {"indice":"natales",    "ciudad":"Puerto Natales",       "reg":"12",  "lat":-51.726,"lon":-72.506},
    {"indice":"parenas",    "ciudad":"Punta Arenas",         "reg":"12",  "lat":-53.163,"lon":-70.917},
    {"indice":"porvenir",   "ciudad":"Porvenir",             "reg":"12",  "lat":-53.296,"lon":-70.366},
    {"indice":"pwilliams",  "ciudad":"Puerto Williams",      "reg":"12",  "lat":-54.935,"lon":-67.605},
    {"indice":"rapanui",    "ciudad":"Rapa Nui",             "reg":"ip",  "lat":-27.112,"lon":-109.349},
    {"indice":"jfernandez", "ciudad":"Juan Fernandez",       "reg":"jf",  "lat":-33.639,"lon":-78.829},
    {"indice":"antartica",  "ciudad":"Antartica",            "reg":"an",  "lat":-62.190,"lon":-58.986},
]
LOC_BY_INDICE = {l["indice"]: l for l in LOCALITIES}

# ── fetch ─────────────────────────────────────────────────────────────────────

def fetch_html(url, timeout=30):
    """Fetch URL with browser-like headers and SSL bypass."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-CL,es;q=0.9",
        "Accept-Encoding": "identity",
        "Referer": "https://www.meteochile.gob.cl/",
        "Cache-Control": "no-cache",
    }
    req = urlreq.Request(url, headers=headers)
    try:
        with urlreq.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
            status = r.getcode()
            raw = r.read()
            print(f"  HTTP {status}, bytes={len(raw)}")
    except HTTPError as e:
        print(f"  HTTP ERROR {e.code}: {e.reason}")
        # Try to read body anyway
        try:
            raw = e.read()
        except:
            raise
    for enc in ("utf-8", "latin-1", "iso-8859-1"):
        try:
            return raw.decode(enc)
        except Exception:
            pass
    return raw.decode("utf-8", errors="replace")

# ── parsing helpers ───────────────────────────────────────────────────────────

def parse_temp(s):
    s = str(s or "").strip()
    if "/" in s:
        a, b = s.split("/", 1)
        def f(x):
            try: return float(x.strip()) if x.strip() else None
            except: return None
        return f(a), f(b)
    try: v = float(s); return v, v
    except: return None, None

def extract_wind(texts):
    t = " ".join(str(x) for x in texts if x)
    best = None
    for m in re.finditer(r'entre\s+(\d+)\s+y\s+(\d+)\s*km', t, re.I):
        v = max(float(m.group(1)), float(m.group(2)))
        if best is None or v > best: best = v
    for m in re.finditer(r'(\d+)\s*km/h', t, re.I):
        v = float(m.group(1))
        if best is None or v > best: best = v
    return best

def wmo_from_text(texts):
    s = " ".join(str(x) for x in texts if x).lower()
    if re.search(r'torment|tronad', s): return 95
    if re.search(r'nieve', s): return 71
    if re.search(r'lluvi|chubasc|precipit', s): return 61
    if re.search(r'niebla|neblina', s): return 45
    if re.search(r'cubierto|nublado', s): return 3
    if re.search(r'parcial|nubosidad', s): return 2
    return 0

def find_brace_end(text, start):
    depth, i, in_str, sc, esc = 0, start, False, None, False
    while i < len(text):
        c = text[i]
        if in_str:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == sc: in_str = False
        else:
            if c in ('"', "'"): in_str, sc = True, c
            elif c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0: return text[start:i+1]
        i += 1
    return None

# ── extraction strategies ─────────────────────────────────────────────────────

def get_blocks(html):
    """Try multiple patterns to find Pronostico push blocks."""
    blocks = []
    seen = set()

    # Strategy A: standard Pronostico.push({
    for m in re.finditer(r'[Pp]ronostico\s*\.push\s*\(\s*\{', html, re.DOTALL):
        bpos = m.end() - 1
        b = find_brace_end(html, bpos)
        if b and id(b) not in seen:
            seen.add(id(b)); blocks.append(b)

    # Strategy B: array-style var Pronostico = [{...},{...}]
    for m in re.finditer(r'[Pp]ronostico\s*=\s*\[', html):
        i = m.end() - 1
        depth = 0
        j = i
        while j < len(html) and j < i + 500000:
            c = html[j]
            if c == '[': depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    inner = html[i+1:j]
                    for bm in re.finditer(r'\{', inner):
                        b = find_brace_end(inner, bm.start())
                        if b and len(b) > 30: blocks.append(b)
                    break
            j += 1

    # Strategy C: per-indice context (most robust)
    for indice in LOC_BY_INDICE:
        for pat in [
            r'indice\s*:\s*["\']' + re.escape(indice) + r'["\']',
            r'"indice"\s*:\s*"' + re.escape(indice) + r'"',
            re.escape(indice),
        ]:
            for m in re.finditer(pat, html, re.I):
                chunk = html[max(0, m.start()-100): m.start()+4000]
                blocks.append(chunk)
                break

    print(f"  blocks found: A+B+C = {len(blocks)}")
    return blocks

def parse_block(block):
    m = re.search(r'indice\s*:\s*["\']?(\w+)["\']?', block, re.I)
    if not m: return None
    indice = m.group(1).strip().lower()

    mt = re.search(r'tope\s*:\s*(\d+)', block, re.I)
    tope = min(max(int(mt.group(1)) if mt else 5, 1), 10)

    tr = re.search(r'temperatura\s*:\s*(\[[^\]]*\])', block, re.I)
    temps = re.findall(r'["\']([^"\']*)["\']', tr.group(1)) if tr else []
    if not temps and tr:
        temps = re.findall(r'[\d./\-]+', tr.group(1))

    fr = re.search(r'fecha\s*:\s*(\[[^\]]*\])', block, re.I)
    fechas = re.findall(r'["\']([^"\']*)["\']', fr.group(1)) if fr else []

    texto_days = []
    txm = re.search(r'texto\s*:\s*\[', block, re.I)
    if txm:
        sub = block[txm.end()-1:]
        for dm in re.finditer(r'\[([^\[\]]*)\]', sub):
            texts = re.findall(r'["\']([^"\']*)["\']', dm.group(1))
            if texts: texto_days.append(texts)

    return {"indice": indice, "tope": tope, "temps": temps, "fechas": fechas, "texto_days": texto_days}

# ── build daily ───────────────────────────────────────────────────────────────

def build_daily(p, loc):
    base = datetime.date.today()
    daily = {"time":[], "temperature_2m_max":[], "temperature_2m_min":[],
             "precipitation_sum":[], "wind_speed_10m_max":[], "weather_code":[], "__summary_text":[]}
    for i in range(p["tope"]):
        fd = p["fechas"][i] if i < len(p["fechas"]) else None
        ds = str(fd)[:10] if fd and re.match(r'\d{4}-\d{2}-\d{2}', str(fd)) else (base + datetime.timedelta(days=i)).isoformat()
        daily["time"].append(ds)
        ts = p["temps"][i] if i < len(p["temps"]) else ""
        tmin, tmax = parse_temp(ts)
        daily["temperature_2m_min"].append(tmin)
        daily["temperature_2m_max"].append(tmax)
        pt = p["texto_days"][i] if i < len(p["texto_days"]) else []
        at = " ".join(str(x) for x in pt if x).lower()
        daily["precipitation_sum"].append(2.0 if re.search(r'lluvi|chubasc|precipit', at) else 0.5 if "llovizna" in at else 0.0)
        daily["wind_speed_10m_max"].append(extract_wind(pt))
        daily["weather_code"].append(wmo_from_text(pt))
        daily["__summary_text"].append(pt)
    return {"indice": p["indice"], "ciudad": loc["ciudad"], "reg": loc["reg"],
            "lat": loc["lat"], "lon": loc["lon"], "daily": daily, "horizon_days": p["tope"]}

# ── main ──────────────────────────────────────────────────────────────────────

def scrape_region(reg):
    url = BASE_URL + reg
    try:
        html = fetch_html(url)
    except Exception as e:
        print(f"[{reg}] FETCH ERROR: {type(e).__name__}: {e}")
        return {}

    # Diagnostic
    has_prono = html.count("Pronostico") + html.count("pronostico")
    has_temp  = html.count("temperatura")
    has_push  = html.count("push(")
    has_ind   = html.count("indice")
    print(f"[{reg}] len={len(html)} pronostico={has_prono} temperatura={has_temp} push={has_push} indice={has_ind}")
    if has_ind == 0:
        print(f"  [WARN] No 'indice' found. HTML snippet: {repr(html[:400])}")

    blocks = get_blocks(html)
    found = {}
    for block in blocks:
        p = parse_block(block)
        if not p or p["indice"] not in LOC_BY_INDICE or p["indice"] in found:
            continue
        loc = LOC_BY_INDICE[p["indice"]]
        result = build_daily(p, loc)
        found[p["indice"]] = result
        print(f"  OK {p['indice']}: {p['tope']}d tmax={result['daily']['temperature_2m_max'][:3]} tmin={result['daily']['temperature_2m_min'][:3]}")

    if not found:
        print(f"  [!] 0 localities for [{reg}]")
    return found

def main():
    all_loc = {}
    total = 0
    for reg in REGIONS:
        try:
            res = scrape_region(reg)
            all_loc.update(res)
            total += len(res)
        except Exception as e:
            print(f"[{reg}] UNHANDLED: {e}")
        time.sleep(0.5)
    print(f"\nTOTAL: {total} localities")
    with open("dmc_cache.json", "w", encoding="utf-8") as f:
        json.dump({"generated_at": datetime.datetime.utcnow().isoformat()+"Z", "localities": all_loc}, f, ensure_ascii=False, indent=2)
    print("Saved dmc_cache.json")

if __name__ == "__main__":
    main()
