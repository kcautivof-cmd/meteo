#!/usr/bin/env python3
"""fetch_dmc.py — fetches DMC region HTML + external JS files, parses Pronostico.push(...)
   Fallback: parse temperaturas directamente del HTML visible si JS falla.
"""

import json, re, time, datetime, sys, ssl, unicodedata

try:
    import urllib.request as urlreq
    from urllib.error import HTTPError
    from urllib.parse import urljoin, urlparse
except ImportError:
    import urllib2 as urlreq

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
LOC_BY_REG    = {}
for l in LOCALITIES:
    LOC_BY_REG.setdefault(l["reg"], []).append(l)

# Ciudad → indice mapping para parseo HTML directo
CIUDAD_TO_INDICE = {
    l["ciudad"].lower(): l["indice"] for l in LOCALITIES
}
# Variantes adicionales
CIUDAD_ALIASES = {
    "san pedro de atacama": "snpedro",
    "san pedro": "snpedro",
    "san antonio": "snantonio",
    "san fernando": "snfernando",
    "santa cruz": "stacruz",
    "la serena": "serena",
    "los vilos": "vilos",
    "los angeles": "angeles",
    "puerto montt": "pmontt",
    "puerto natales": "natales",
    "punta arenas": "parenas",
    "puerto williams": "pwilliams",
    "juan fernandez": "jfernandez",
    "rapa nui": "rapanui",
    "santiago oriente": "stgoo",
    "santiago centro": "stgoc",
    "santiago norte": "stgon",
    "santiago sur": "stgos",
    "santiago poniente": "stgop",
    "el salvador": "salvador",
    "vina del mar": "vdelmar",
    "viña del mar": "vdelmar",
    "valparaiso": "valpo",
    "valparaíso": "valpo",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-CL,es;q=0.9",
    "Accept-Encoding": "identity",
    "Referer": "https://www.meteochile.gob.cl/",
}

# ── fetch ─────────────────────────────────────────────────────────────────────

def fetch_text(url, timeout=25):
    req = urlreq.Request(url, headers=HEADERS)
    try:
        with urlreq.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
            raw = r.read()
    except HTTPError as e:
        raw = e.read()
    for enc in ("utf-8", "latin-1", "iso-8859-1"):
        try:
            return raw.decode(enc)
        except:
            pass
    return raw.decode("utf-8", errors="replace")

def extract_script_urls(html, base_url):
    urls = []
    seen = set()
    for m in re.finditer(r'<script[^>]+src\s*=\s*["\']([^"\']+)["\']', html, re.I):
        src = m.group(1)
        try:
            full = urljoin(base_url, src)
        except:
            continue
        low = full.lower()
        if re.search(r'pronostic|condicion|tiempo|ciudad|region|portal', low):
            if full not in seen:
                seen.add(full)
                urls.append(full)
    return urls

def extract_inline_scripts(html):
    out = []
    for m in re.finditer(r'<script(?:[^>](?!src))*>(.*?)</script>', html, re.DOTALL | re.I):
        body = m.group(1).strip()
        if body:
            out.append(body)
    return out

# ── HTML visual fallback parser ───────────────────────────────────────────────

def normalize_ciudad(name):
    """Normalize city name for lookup."""
    s = unicodedata.normalize("NFD", name.lower())
    s = re.sub(r"[\u0300-\u036f]", "", s).strip()
    return s

def parse_html_visual(html, reg):
    """
    Parse temperatures directly from the visible HTML map labels.
    Pattern: <div ...>TMIN°</div><div ...>TMAX°</div>...<div ...>Ciudad</div>
    or img alt tags with city names and temperature tooltips.
    """
    found = {}
    base = datetime.date.today()

    # Pattern 1: label blocks like: <div ...>18°</div><div ...>24°</div>...<div>Iquique</div>
    # Try to find temperature+city pairs in the HTML
    
    # Remove HTML tags to get text, then find patterns
    # Look for patterns like: 18° 24° ... Iquique
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text)
    
    # Pattern: NUMBER° NUMBER° CITYNAME
    pattern = re.finditer(
        r'(\d{1,3})°\s+(\d{1,3})°\s+([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü A-ZÁÉÍÓÚÑÜ]{2,30}?)(?=\s+\d|\s*$|\s+[A-Z]{2,})',
        text
    )
    
    locs_in_reg = LOC_BY_REG.get(reg, [])
    
    for m in pattern:
        t1, t2, ciudad_raw = int(m.group(1)), int(m.group(2)), m.group(3).strip()
        tmin, tmax = min(t1, t2), max(t1, t2)
        
        # Lookup city
        ciudad_norm = normalize_ciudad(ciudad_raw)
        indice = CIUDAD_TO_INDICE.get(ciudad_norm) or CIUDAD_ALIASES.get(ciudad_norm)
        
        if not indice:
            # Try partial match within region
            for loc in locs_in_reg:
                loc_norm = normalize_ciudad(loc["ciudad"])
                if loc_norm in ciudad_norm or ciudad_norm in loc_norm:
                    indice = loc["indice"]
                    break
        
        if not indice or indice in found:
            continue
            
        loc = LOC_BY_INDICE.get(indice)
        if not loc:
            continue
        
        # Build a 1-day entry (only today available from HTML)
        daily = {
            "time": [base.isoformat()],
            "temperature_2m_max": [float(tmax)],
            "temperature_2m_min": [float(tmin)],
            "precipitation_sum": [0.0],
            "wind_speed_10m_max": [None],
            "weather_code": [0],
            "__summary_text": [[]],
        }
        found[indice] = {
            "indice": indice, "ciudad": loc["ciudad"],
            "reg": loc["reg"], "lat": loc["lat"], "lon": loc["lon"],
            "daily": daily, "horizon_days": 1
        }
        print(f"  HTML-visual OK {indice} ({ciudad_raw}): {tmin}/{tmax}")
    
    return found

# ── JS parsing ────────────────────────────────────────────────────────────────

def find_matching_brace(text, start):
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

def extract_pronostico_blocks(js):
    blocks = []
    for m in re.finditer(r'[Pp]ronostico\s*\.push\s*\(\s*\{', js):
        bpos = js.rfind('{', m.start(), m.end())
        block = find_matching_brace(js, bpos)
        if block and len(block) > 30:
            blocks.append(block)
    if blocks:
        print(f"    Format1 (push): {len(blocks)} blocks")
        return blocks

    for m in re.finditer(r'[Pp]ronostico\s*=\s*\[', js):
        i = m.end() - 1
        depth, j = 0, i
        while j < len(js) and j < i + 200000:
            c = js[j]
            if c == '[': depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    inner = js[i+1:j]
                    for bm in re.finditer(r'\{', inner):
                        b = find_matching_brace(inner, bm.start())
                        if b and len(b) > 30:
                            blocks.append(b)
                    break
            j += 1
    if blocks:
        print(f"    Format2 (array): {len(blocks)} blocks")
        return blocks

    for indice in LOC_BY_INDICE:
        for pat in [
            r'(?:var|let|const)\s+' + re.escape(indice) + r'\s*=\s*\{',
            r'\b' + re.escape(indice) + r'\s*=\s*\{',
        ]:
            for m in re.finditer(pat, js, re.I):
                bpos = js.rfind('{', m.start(), m.end())
                block = find_matching_brace(js, bpos)
                if block and len(block) > 30:
                    blocks.append(block)
                    break
    if blocks:
        print(f"    Format3 (var): {len(blocks)} blocks")
    return blocks

def parse_block(block):
    m = re.search(r'indice\s*:\s*["\']?(\w+)["\']?', block, re.I)
    if not m:
        return None
    indice = m.group(1).strip().lower()
    mt = re.search(r'tope\s*:\s*(\d+)', block, re.I)
    tope = min(max(int(mt.group(1)) if mt else 5, 1), 10)

    def get_array(key):
        am = re.search(key + r'\s*:\s*(\[)', block, re.I)
        if not am:
            return None
        depth, i, in_str, sc = 0, am.start(1), False, None
        while i < len(block):
            c = block[i]
            if in_str:
                if c == sc: in_str = False
            else:
                if c in ('"', "'"): in_str, sc = True, c
                elif c == '[': depth += 1
                elif c == ']':
                    depth -= 1
                    if depth == 0: return block[am.start(1):i+1]
            i += 1
        return None

    temp_raw = get_array('temperatura')
    temps = re.findall(r'["\']([^"\']*)["\']', temp_raw) if temp_raw else []
    if not temps and temp_raw:
        temps = re.findall(r'[\d./\-]+', temp_raw)
    fecha_raw = get_array('fecha')
    fechas = re.findall(r'["\']([^"\']*)["\']', fecha_raw) if fecha_raw else []
    texto_raw = get_array('texto')
    texto_days = []
    if texto_raw:
        for dm in re.finditer(r'\[([^\[\]]*)\]', texto_raw):
            texts = re.findall(r'["\']([^"\']*)["\']', dm.group(1))
            if texts: texto_days.append(texts)
    return {"indice": indice, "tope": tope, "temps": temps,
            "fechas": fechas, "texto_days": texto_days}

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
    for m in re.finditer(r"entre\s+(\d+)\s+y\s+(\d+)\s*km", t, re.I):
        v = max(float(m.group(1)), float(m.group(2)))
        if best is None or v > best: best = v
    for m in re.finditer(r"(\d+)\s*km/h", t, re.I):
        v = float(m.group(1))
        if best is None or v > best: best = v
    return best

def wmo_from_text(texts):
    s = " ".join(str(t) for t in texts if t).lower()
    if re.search(r"torment|tronad", s): return 95
    if re.search(r"nieve", s): return 71
    if re.search(r"lluvi|chubasc|precipit", s): return 61
    if re.search(r"niebla|neblina", s): return 45
    if re.search(r"cubierto|nublado", s): return 3
    if re.search(r"parcial|nubosidad", s): return 2
    return 0

def summarize(texts):
    seen, out = set(), []
    for t in (texts or []):
        c = unicodedata.normalize("NFD", str(t).lower())
        c = re.sub(r"[\u0300-\u036f]", "", c).strip()
        if c and c not in seen:
            seen.add(c)
            out.append(str(t).strip().upper())
    return out

def build_daily(p, loc):
    base = datetime.date.today()
    daily = {"time":[], "temperature_2m_max":[], "temperature_2m_min":[],
             "precipitation_sum":[], "wind_speed_10m_max":[], "weather_code":[],
             "__summary_text":[]}
    for i in range(p["tope"]):
        fd = p["fechas"][i] if i < len(p["fechas"]) else None
        ds = str(fd)[:10] if fd and re.match(r'\d{4}-\d{2}-\d{2}', str(fd)) \
             else (base + datetime.timedelta(days=i)).isoformat()
        daily["time"].append(ds)
        ts = p["temps"][i] if i < len(p["temps"]) else ""
        t_min, t_max = parse_temp(ts)
        daily["temperature_2m_min"].append(t_min)
        daily["temperature_2m_max"].append(t_max)
        pt = p["texto_days"][i] if i < len(p["texto_days"]) else []
        at = " ".join(t for t in pt if t).lower()
        daily["precipitation_sum"].append(2.0 if re.search(r"lluvi|chubasc|precipit", at)
                                          else 0.5 if "llovizna" in at else 0.0)
        daily["wind_speed_10m_max"].append(extract_wind(pt))
        daily["weather_code"].append(wmo_from_text(pt))
        daily["__summary_text"].append(summarize(pt))
    return {"indice": loc["indice"], "ciudad": loc["ciudad"], "reg": loc["reg"],
            "lat": loc["lat"], "lon": loc["lon"], "daily": daily,
            "horizon_days": p["tope"]}

# ── main scraper ──────────────────────────────────────────────────────────────

def scrape_region(reg):
    url = BASE_URL + reg
    try:
        html = fetch_text(url)
    except Exception as e:
        print(f"[{reg}] FETCH ERROR: {e}")
        return {}

    print(f"[{reg}] HTML={len(html)} push={html.count('push(')} temperatura={html.count('temperatura')}")

    inline = extract_inline_scripts(html)
    script_urls = extract_script_urls(html, url)
    print(f"  inline_scripts={len(inline)} external_scripts={len(script_urls)}")

    merged = html + "\n".join(inline)
    for su in script_urls:
        print(f"  fetching: {su}")
        try:
            js = fetch_text(su)
            merged += f"\n// SRC:{su}\n" + js
            print(f"    loaded {len(js)} chars")
        except Exception as e:
            print(f"    FAIL {su}: {e}")

    # Try JS parsing first
    blocks = extract_pronostico_blocks(merged)
    print(f"  pronostico blocks: {len(blocks)}")

    found = {}
    for block in blocks:
        p = parse_block(block)
        if not p or p["indice"] not in LOC_BY_INDICE or p["indice"] in found:
            continue
        loc = LOC_BY_INDICE[p["indice"]]
        result = build_daily(p, loc)
        found[p["indice"]] = result
        tmax = result["daily"]["temperature_2m_max"][:3]
        tmin = result["daily"]["temperature_2m_min"][:3]
        print(f"  OK {p['indice']}: {p['tope']}d tmax={tmax} tmin={tmin}")

    # Fallback: parse HTML visual if JS parsing missed any localities in this region
    locs_in_reg = LOC_BY_REG.get(reg, [])
    missing = [l for l in locs_in_reg if l["indice"] not in found]
    if missing:
        print(f"  [fallback HTML-visual] missing: {[l['indice'] for l in missing]}")
        html_found = parse_html_visual(html, reg)
        for indice, data in html_found.items():
            if indice not in found:
                found[indice] = data

    # Still missing after fallback
    still_missing = [l["indice"] for l in locs_in_reg if l["indice"] not in found]
    if still_missing:
        print(f"  [!] still missing after fallback: {still_missing}")

    return found

def main():
    all_loc = {}
    for reg in REGIONS:
        try:
            res = scrape_region(reg)
            all_loc.update(res)
        except Exception as e:
            print(f"[{reg}] ERROR: {e}")
        time.sleep(0.5)
    print(f"\nTOTAL: {len(all_loc)} localities")
    with open("dmc_cache.json", "w", encoding="utf-8") as f:
        json.dump({"generated_at": datetime.datetime.utcnow().isoformat()+"Z",
                   "localities": all_loc}, f, ensure_ascii=False, indent=2)
    print("Saved dmc_cache.json")

if __name__ == "__main__":
    main()
