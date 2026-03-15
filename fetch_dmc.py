#!/usr/bin/env python3
"""fetch_dmc.py — scrapes DMC Chile WRF forecast and saves dmc_cache.json"""

import json, re, time, datetime, sys
try:
    import urllib.request as urlreq
    from urllib.error import URLError
except ImportError:
    import urllib2 as urlreq

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

# ── helpers ───────────────────────────────────────────────────────────────────

def fetch_html(url, timeout=20):
    req = urlreq.Request(url, headers={"User-Agent": "fetch-dmc/3.0"})
    with urlreq.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    for enc in ("utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except Exception:
            pass
    return raw.decode("utf-8", errors="replace")

def get_field(block, key):
    """Extract a field value from a JS object string using regex (like worker.js does)."""
    m = re.search(
        key + r'\s*:\s*([\[\]"\'\w\s,./\-]+?)(?=\s*,\s*\w+\s*:|\s*\})',
        block
    )
    return m.group(1).strip() if m else None

def get_array_field(block, key):
    """Extract array field (handles nested arrays too)."""
    m = re.search(key + r'\s*:\s*(\[)', block)
    if not m:
        return None
    start = m.start(1)
    depth = 0
    for i in range(start, len(block)):
        if block[i] == '[':
            depth += 1
        elif block[i] == ']':
            depth -= 1
            if depth == 0:
                raw = block[start:i+1]
                return raw
    return None

def parse_js_str_array(raw):
    """Parse JS string array like ["a","b","c"] or ['a','b'] into Python list."""
    if not raw:
        return []
    items = re.findall(r'["\']([^"\']*)["\']', raw)
    return items

def parse_js_int(raw):
    """Parse a simple JS integer."""
    if not raw:
        return None
    m = re.search(r'-?\d+', raw.strip())
    return int(m.group()) if m else None

def parse_temp(raw_str):
    """Split 'min/max' string into (t_min, t_max) as float|None."""
    s = str(raw_str or "").strip()
    if "/" in s:
        left, right = s.split("/", 1)
        def to_f(x):
            x = x.strip()
            try:
                return float(x) if x else None
            except ValueError:
                return None
        return to_f(left), to_f(right)
    try:
        v = float(s)
        return v, v
    except ValueError:
        return None, None

def extract_wind_kmh(texts):
    """Extract wind speed from text like 'viento entre 40 y 60 km/h'."""
    all_text = " ".join(str(t) for t in texts if t)
    best = None
    for m in re.finditer(r'entre\s+(\d+)\s+y\s+(\d+)\s*km', all_text, re.I):
        val = max(float(m.group(1)), float(m.group(2)))
        if best is None or val > best:
            best = val
    for m in re.finditer(r'(\d+)\s*km/h', all_text, re.I):
        val = float(m.group(1))
        if best is None or val > best:
            best = val
    return best

def text_to_weather_code(texts):
    s = " ".join(str(t) for t in texts if t).lower()
    if re.search(r'torment|tronad', s): return 95
    if re.search(r'nieve|agua nieve', s): return 71
    if re.search(r'lluvi|chubasc|precipit', s): return 61
    if re.search(r'niebla|neblina|bruma', s): return 45
    if re.search(r'cubierto|nublado', s): return 3
    if re.search(r'parcial|nubosidad', s): return 2
    if re.search(r'despejado|soleado', s): return 0
    return 0

# ── main scraper ──────────────────────────────────────────────────────────────

def scrape_region(reg):
    url = BASE_URL + reg
    try:
        html = fetch_html(url)
    except Exception as e:
        print(f"[{reg}] fetch err: {e}")
        return {}

    print(f"[{reg}] HTML={len(html)} chars")

    # Count debug indicators (like the old version did)
    print(f"[{reg}] push(: {html.count('push(')}")
    print(f"[{reg}] temperatura: {html.count('temperatura')}")

    # Find all Pronostico.push({...}) blocks using same approach as worker.js
    push_re = re.compile(
        r'[Pp]ronostico\s*\.\s*push\s*\(\s*\{',
        re.DOTALL
    )

    results = {}
    for pm in push_re.finditer(html):
        # Find the opening brace
        brace_start = html.index('{', pm.start())
        # Walk to find matching closing brace
        depth = 0
        i = brace_start
        while i < len(html):
            c = html[i]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    block = html[brace_start:i+1]
                    break
            i += 1
        else:
            continue

        # Extract indice
        m_ind = re.search(r'indice\s*:\s*["\']?(\w+)["\']?', block)
        if not m_ind:
            continue
        indice = m_ind.group(1).strip().lower()
        if indice not in LOC_BY_INDICE:
            continue

        loc = LOC_BY_INDICE[indice]

        # Extract tope (number of forecast days)
        m_tope = re.search(r'tope\s*:\s*(\d+)', block)
        tope = int(m_tope.group(1)) if m_tope else 5
        tope = min(max(tope, 1), 10)

        # Extract temperatura array: ["13/26","14/28",...]
        temp_raw = get_array_field(block, 'temperatura')
        temps = parse_js_str_array(temp_raw) if temp_raw else []

        # Extract texto array of arrays
        texto_raw = get_array_field(block, 'texto')

        # Extract fecha array
        fecha_raw = get_array_field(block, 'fecha')
        fechas = parse_js_str_array(fecha_raw) if fecha_raw else []

        # Parse texto into list of period-text lists
        texto_days = []
        if texto_raw:
            # Each day is a sub-array: [["texto1","texto2","texto3","texto4"],...]
            day_re = re.compile(r'\[([^\[\]]*)\]')
            # Remove outer bracket
            inner = texto_raw.strip()
            if inner.startswith('['):
                inner = inner[1:]
            if inner.endswith(']'):
                inner = inner[:-1]
            for dm in day_re.finditer(inner):
                texts = re.findall(r'["\']([^"\']*)["\']', dm.group(1))
                texto_days.append(texts)

        base = datetime.date.today()
        daily = {
            "time": [],
            "temperature_2m_max": [],
            "temperature_2m_min": [],
            "precipitation_sum": [],
            "wind_speed_10m_max": [],
            "weather_code": [],
            "summarytext": [],
        }

        for i in range(tope):
            # date
            raw_date = fechas[i] if i < len(fechas) else None
            if raw_date and re.match(r'\d{4}-\d{2}-\d{2}', str(raw_date)):
                date_str = str(raw_date)[:10]
            else:
                date_str = (base + datetime.timedelta(days=i)).isoformat()
            daily["time"].append(date_str)

            # ── TEMPERATURE FIX: split "min/max" correctly ──
            temp_str = temps[i] if i < len(temps) else ""
            t_min, t_max = parse_temp(temp_str)
            daily["temperature_2m_min"].append(t_min)
            daily["temperature_2m_max"].append(t_max)

            # periods text for this day
            period_texts = texto_days[i] if i < len(texto_days) else []
            if not isinstance(period_texts, list):
                period_texts = [period_texts]

            all_text = " ".join(str(t) for t in period_texts if t).lower()

            # precipitation
            precip = 0.0
            if re.search(r'lluvi|chubasc|precipit', all_text):
                precip = 2.0
            elif re.search(r'llovizna', all_text):
                precip = 0.5
            daily["precipitation_sum"].append(precip)

            # wind
            daily["wind_speed_10m_max"].append(extract_wind_kmh(period_texts))

            # weather code
            daily["weather_code"].append(text_to_weather_code(period_texts))

            # summary text (raw period list for frontend formatting)
            daily["summarytext"].append(period_texts)

        results[indice] = {
            "indice": indice,
            "ciudad": loc["ciudad"],
            "reg": loc["reg"],
            "lat": loc["lat"],
            "lon": loc["lon"],
            "daily": daily,
            "horizon_days": tope,
        }
        t_max_preview = daily["temperature_2m_max"][:3]
        t_min_preview = daily["temperature_2m_min"][:3]
        print(f"  OK {indice}: {tope}d | tmax={t_max_preview} tmin={t_min_preview}")

    return results

# ── entry point ───────────────────────────────────────────────────────────────

def main():
    all_localities = {}
    ok_count = fail_count = 0
    for reg in REGIONS:
        try:
            res = scrape_region(reg)
            all_localities.update(res)
            ok_count += len(res)
        except Exception as e:
            print(f"[{reg}] ERROR: {e}")
            fail_count += 1
        time.sleep(0.3)

    print(f"\nTOTAL: {ok_count} localidades, {fail_count} fallos de region")

    cache = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "localities": all_localities,
    }
    with open("dmc_cache.json", "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    print("dmc_cache.json saved.")

if __name__ == "__main__":
    main()
