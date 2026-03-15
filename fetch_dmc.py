#!/usr/bin/env python3
"""
GitHub Actions: scraping DMC meteochile.gob.cl → dmc_cache.json
Corre cada hora y actualiza el cache en el repo.
"""
import re, json, math, unicodedata
from datetime import datetime, date, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError

DMC_REGIONS = ["01a","01b","02","03","04","05","05m","06","07","08a","08b","09","10a","10b","11","12","ip","jf","an"]

DMC_LOCALITIES = [
  {"indice":"visviri","ciudad":"Visviri","reg":"01a","lat":-17.594,"lon":-69.476},
  {"indice":"arica","ciudad":"Arica","reg":"01a","lat":-18.478,"lon":-70.312},
  {"indice":"putre","ciudad":"Putre","reg":"01a","lat":-18.196,"lon":-69.560},
  {"indice":"colchane","ciudad":"Colchane","reg":"01b","lat":-19.277,"lon":-68.639},
  {"indice":"iquique","ciudad":"Iquique","reg":"01b","lat":-20.216,"lon":-70.153},
  {"indice":"pica","ciudad":"Pica","reg":"01b","lat":-20.491,"lon":-69.329},
  {"indice":"ollague","ciudad":"Ollagüe","reg":"02","lat":-21.225,"lon":-68.254},
  {"indice":"tocopilla","ciudad":"Tocopilla","reg":"02","lat":-22.092,"lon":-70.197},
  {"indice":"calama","ciudad":"Calama","reg":"02","lat":-22.456,"lon":-68.923},
  {"indice":"snpedro","ciudad":"San Pedro de Atacama","reg":"02","lat":-22.911,"lon":-68.201},
  {"indice":"mejillones","ciudad":"Mejillones","reg":"02","lat":-23.100,"lon":-70.450},
  {"indice":"antofagasta","ciudad":"Antofagasta","reg":"02","lat":-23.650,"lon":-70.400},
  {"indice":"taltal","ciudad":"Taltal","reg":"02","lat":-25.408,"lon":-70.485},
  {"indice":"salvador","ciudad":"El Salvador","reg":"03","lat":-26.314,"lon":-69.544},
  {"indice":"chanaral","ciudad":"Chañaral","reg":"03","lat":-26.348,"lon":-70.623},
  {"indice":"caldera","ciudad":"Caldera","reg":"03","lat":-27.067,"lon":-70.825},
  {"indice":"copiapo","ciudad":"Copiapó","reg":"03","lat":-27.366,"lon":-70.332},
  {"indice":"huasco","ciudad":"Huasco","reg":"03","lat":-28.464,"lon":-71.218},
  {"indice":"vallenar","ciudad":"Vallenar","reg":"03","lat":-28.576,"lon":-70.759},
  {"indice":"serena","ciudad":"La Serena","reg":"04","lat":-29.902,"lon":-71.251},
  {"indice":"vicuna","ciudad":"Vicuña","reg":"04","lat":-30.031,"lon":-70.708},
  {"indice":"ovalle","ciudad":"Ovalle","reg":"04","lat":-30.598,"lon":-71.200},
  {"indice":"illapel","ciudad":"Illapel","reg":"04","lat":-31.633,"lon":-71.170},
  {"indice":"vilos","ciudad":"Los Vilos","reg":"04","lat":-31.908,"lon":-71.507},
  {"indice":"papudo","ciudad":"Papudo","reg":"05","lat":-32.507,"lon":-71.441},
  {"indice":"valpo","ciudad":"Valparaíso","reg":"05","lat":-33.047,"lon":-71.613},
  {"indice":"vdelmar","ciudad":"Viña del Mar","reg":"05","lat":-33.024,"lon":-71.552},
  {"indice":"snantonio","ciudad":"San Antonio","reg":"05","lat":-33.593,"lon":-71.607},
  {"indice":"stgoo","ciudad":"Santiago Oriente","reg":"05m","lat":-33.437,"lon":-70.650},
  {"indice":"stgoc","ciudad":"Santiago Centro","reg":"05m","lat":-33.448,"lon":-70.669},
  {"indice":"stgon","ciudad":"Santiago Norte","reg":"05m","lat":-33.366,"lon":-70.676},
  {"indice":"stgos","ciudad":"Santiago Sur","reg":"05m","lat":-33.537,"lon":-70.676},
  {"indice":"stgop","ciudad":"Santiago Poniente","reg":"05m","lat":-33.456,"lon":-70.751},
  {"indice":"melipilla","ciudad":"Melipilla","reg":"05m","lat":-33.690,"lon":-71.215},
  {"indice":"rancagua","ciudad":"Rancagua","reg":"06","lat":-34.170,"lon":-70.740},
  {"indice":"snfernando","ciudad":"San Fernando","reg":"06","lat":-34.586,"lon":-70.989},
  {"indice":"stacruz","ciudad":"Santa Cruz","reg":"06","lat":-34.638,"lon":-71.365},
  {"indice":"pichilemu","ciudad":"Pichilemu","reg":"06","lat":-34.392,"lon":-72.006},
  {"indice":"curico","ciudad":"Curicó","reg":"07","lat":-34.982,"lon":-71.239},
  {"indice":"talca","ciudad":"Talca","reg":"07","lat":-35.426,"lon":-71.655},
  {"indice":"constitucion","ciudad":"Constitución","reg":"07","lat":-35.333,"lon":-72.417},
  {"indice":"linares","ciudad":"Linares","reg":"07","lat":-35.846,"lon":-71.593},
  {"indice":"chillan","ciudad":"Chillán","reg":"08a","lat":-36.606,"lon":-72.103},
  {"indice":"concepcion","ciudad":"Concepción","reg":"08b","lat":-36.827,"lon":-73.050},
  {"indice":"angeles","ciudad":"Los Ángeles","reg":"08b","lat":-37.469,"lon":-72.353},
  {"indice":"angol","ciudad":"Angol","reg":"09","lat":-37.798,"lon":-72.716},
  {"indice":"temuco","ciudad":"Temuco","reg":"09","lat":-38.739,"lon":-72.598},
  {"indice":"villarica","ciudad":"Villarrica","reg":"09","lat":-39.285,"lon":-72.227},
  {"indice":"valdivia","ciudad":"Valdivia","reg":"10a","lat":-39.814,"lon":-73.245},
  {"indice":"osorno","ciudad":"Osorno","reg":"10b","lat":-40.574,"lon":-73.133},
  {"indice":"pmontt","ciudad":"Puerto Montt","reg":"10b","lat":-41.469,"lon":-72.942},
  {"indice":"ancud","ciudad":"Ancud","reg":"10b","lat":-41.870,"lon":-73.820},
  {"indice":"castro","ciudad":"Castro","reg":"10b","lat":-42.482,"lon":-73.764},
  {"indice":"chaiten","ciudad":"Chaitén","reg":"10b","lat":-42.915,"lon":-72.707},
  {"indice":"coyhaique","ciudad":"Coyhaique","reg":"11","lat":-45.571,"lon":-72.068},
  {"indice":"balmaceda","ciudad":"Balmaceda","reg":"11","lat":-45.915,"lon":-71.689},
  {"indice":"cochrane","ciudad":"Cochrane","reg":"11","lat":-47.255,"lon":-72.573},
  {"indice":"natales","ciudad":"Puerto Natales","reg":"12","lat":-51.726,"lon":-72.506},
  {"indice":"parenas","ciudad":"Punta Arenas","reg":"12","lat":-53.163,"lon":-70.917},
  {"indice":"porvenir","ciudad":"Porvenir","reg":"12","lat":-53.296,"lon":-70.366},
  {"indice":"pwilliams","ciudad":"Puerto Williams","reg":"12","lat":-54.935,"lon":-67.605},
  {"indice":"rapanui","ciudad":"Rapa Nui","reg":"ip","lat":-27.112,"lon":-109.349},
  {"indice":"jfernandez","ciudad":"Juan Fernández","reg":"jf","lat":-33.639,"lon":-78.829},
  {"indice":"antartica","ciudad":"Antártica","reg":"an","lat":-62.190,"lon":-58.986},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-CL,es;q=0.9",
    "Referer": "https://www.meteochile.gob.cl/"
}

TEXT_TO_CODE = {
    "despejado": 0, "soleado": 1, "mayormente despejado": 1, "mayormente soleado": 1,
    "parcialmente nublado": 2, "nublado": 3, "cubierto": 3,
    "niebla": 45, "neblina": 45, "lluvia debil": 61, "lluvia ligera": 61,
    "lluvia": 63, "lluvia intensa": 65, "llovizna": 51,
    "chubascos": 80, "chubascos aislados": 80, "nieve": 73, "tormenta": 95,
}

def normalize(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", " ", s).strip()

def text_to_wcode(text):
    n = normalize(text)
    for k, v in TEXT_TO_CODE.items():
        if k in n:
            return v
    return 1

def extract_minmax(text):
    nums = re.findall(r"-?\d+(?:[.,]\d+)?", str(text).replace("\xa0",""))
    vals = [float(x.replace(",",".")) for x in nums]
    if not vals:
        return None, None
    if len(vals) == 1:
        return vals[0], vals[0]
    return min(vals[0], vals[1]), max(vals[0], vals[1])

def clean_html(s):
    s = re.sub(r"<[^>]+>", " ", str(s))
    s = re.sub(r"&[a-z]+;", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def fetch_html(url):
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=20) as r:
        raw = r.read()
    for enc in ("utf-8", "latin-1", "iso-8859-1"):
        try:
            return raw.decode(enc)
        except:
            pass
    return raw.decode("latin-1", errors="replace")

def parse_forecast_table(html):
    """Extrae filas de tabla DMC con columnas Madrugada/Mañana/Tarde/Noche."""
    rows = []
    table_match = re.search(r"<table[^>]*>([\s\S]*?)</table>", html, re.IGNORECASE)
    if not table_match:
        return rows
    table = table_match.group(0)
    if not re.search(r"(Madrugada|Ma[ñn]ana|Tarde|Noche)", table, re.IGNORECASE):
        return rows
    tr_list = re.findall(r"<tr[^>]*>([\s\S]*?)</tr>", table, re.IGNORECASE)
    for tr in tr_list:
        cells = re.findall(r"<t[dh][^>]*>([\s\S]*?)</t[dh]>", tr, re.IGNORECASE)
        if len(cells) < 5:
            continue
        day_text = clean_html(cells[0])
        minmax_text = clean_html(cells[1])
        if not re.search(r"\d", day_text) or not re.search(r"-?\d", minmax_text):
            continue
        day_num = re.search(r"\d+", day_text)
        if not day_num:
            continue
        tmin, tmax = extract_minmax(minmax_text)
        periods = [clean_html(c) for c in cells[2:6]]
        all_text = " ".join(periods)
        wind_match = re.search(r"(\d+)\s*(?:a|-)\s*(\d+)\s*km", all_text, re.IGNORECASE)
        wind_max = None
        if wind_match:
            wind_max = max(int(wind_match.group(1)), int(wind_match.group(2)))
        else:
            wm = re.search(r"(\d+)\s*km", all_text, re.IGNORECASE)
            if wm:
                wind_max = int(wm.group(1))
        precip = 0.0
        pm = re.search(r"(\d+(?:[.,]\d+)?)\s*mm", all_text, re.IGNORECASE)
        if pm:
            precip = float(pm.group(1).replace(",","."))
        rows.append({
            "day_number": int(day_num.group()),
            "tmin": tmin,
            "tmax": tmax,
            "text": periods,
            "all_text": all_text,
            "wind_max_kmh": wind_max,
            "precip_mm": precip,
        })
    return rows

def infer_dates(rows):
    today = date.today()
    dates = []
    prev = None
    for r in rows:
        dn = r["day_number"]
        if prev is None:
            candidate = today.replace(day=dn) if dn >= today.day else (today + timedelta(days=30)).replace(day=dn)
            try:
                candidate = today.replace(day=dn)
                if candidate < today - timedelta(days=1):
                    m = today.month + 1 if today.month < 12 else 1
                    y = today.year if today.month < 12 else today.year + 1
                    candidate = date(y, m, dn)
            except:
                candidate = today
        else:
            candidate = prev + timedelta(days=1)
            if abs(candidate.day - dn) > 2:
                candidate = prev + timedelta(days=1)
        prev = candidate
        dates.append(candidate.isoformat())
    return dates

def parse_region_html(html, reg):
    """Extrae datos de todas las localidades en una página de región DMC."""
    results = {}
    # Buscar múltiples tablas en la página
    tables = list(re.finditer(r"<table[^>]*>[\s\S]*?</table>", html, re.IGNORECASE))
    loc_map = {p["indice"]: p for p in DMC_LOCALITIES if p["reg"] == reg}

    for m in tables:
        table_html = m.group(0)
        if not re.search(r"(Madrugada|Ma[ñn]ana|Tarde|Noche)", table_html, re.IGNORECASE):
            continue
        # Buscar ciudad antes de la tabla
        pre = html[:m.start()]
        h_match = re.findall(r"<(?:h[1-4]|strong|b)[^>]*>([^<]{3,60})</(?:h[1-4]|strong|b)>", pre[-3000:], re.IGNORECASE)
        city_hint = normalize(h_match[-1]) if h_match else ""

        # Intentar matchear con una localidad conocida
        best_indice = None
        best_score = 0
        for indice, loc in loc_map.items():
            score = 0
            city_norm = normalize(loc["ciudad"])
            if city_norm in city_hint:
                score = len(city_norm) + 100
            elif indice in city_hint:
                score = len(indice) + 80
            elif any(w in city_hint for w in city_norm.split() if len(w) > 3):
                score = 30
            if score > best_score:
                best_score = score
                best_indice = indice

        rows = parse_forecast_table(table_html)
        if not rows:
            continue

        target_indice = best_indice
        if target_indice is None:
            # Si solo hay una localidad en la región, usarla
            if len(loc_map) == 1:
                target_indice = list(loc_map.keys())[0]
            else:
                continue

        dates = infer_dates(rows)
        daily = {
            "time": dates,
            "temperature_2m_max": [r["tmax"] for r in rows],
            "temperature_2m_min": [r["tmin"] for r in rows],
            "precipitation_sum": [r["precip_mm"] for r in rows],
            "wind_speed_10m_max": [r["wind_max_kmh"] for r in rows],
            "weather_code": [text_to_wcode(r["all_text"]) for r in rows],
            "summary_text": [" / ".join(t for t in r["text"] if t) for r in rows],
        }
        results[target_indice] = {
            "indice": target_indice,
            "ciudad": loc_map[target_indice]["ciudad"],
            "reg": reg,
            "lat": loc_map[target_indice]["lat"],
            "lon": loc_map[target_indice]["lon"],
            "daily": daily,
            "horizon_days": len(rows),
        }
    return results

def main():
    cache = {"generated_at": datetime.utcnow().isoformat() + "Z", "localities": {}}
    fetched_regs = set()
    ok_count = 0
    fail_count = 0

    for reg in DMC_REGIONS:
        url = f"https://archivos.meteochile.gob.cl/portaldmc/pronosticos/pronosticoRegion.php?reg={reg}"
        try:
            html = fetch_html(url)
            data = parse_region_html(html, reg)
            cache["localities"].update(data)
            ok_count += len(data)
            fetched_regs.add(reg)
            print(f"  OK {reg}: {len(data)} localidades")
        except Exception as e:
            fail_count += 1
            print(f"  FAIL {reg}: {e}")

    cache["stats"] = {
        "ok_localities": ok_count,
        "fail_regions": fail_count,
        "fetched_regions": list(fetched_regs),
    }
    with open("dmc_cache.json", "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    print(f"\ndmc_cache.json guardado: {ok_count} localidades, {fail_count} fallos")

if __name__ == "__main__":
    main()
