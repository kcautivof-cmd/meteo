#!/usr/bin/env python3
import re, json, sys, unicodedata
from datetime import datetime, date, timedelta
from urllib.request import urlopen, Request
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*",
    "Accept-Language": "es-CL,es;q=0.9",
    "Referer": "https://www.meteochile.gob.cl/"
}

DMC_REGIONS = ["01a","01b","02","03","04","05","05m","06","07","08a","08b","09","10a","10b","11","12","ip","jf","an"]

DMC_LOCALITIES = [
  {"indice":"visviri","ciudad":"Visviri","reg":"01a","lat":-17.594,"lon":-69.476},
  {"indice":"arica","ciudad":"Arica","reg":"01a","lat":-18.478,"lon":-70.312},
  {"indice":"putre","ciudad":"Putre","reg":"01a","lat":-18.196,"lon":-69.560},
  {"indice":"colchane","ciudad":"Colchane","reg":"01b","lat":-19.277,"lon":-68.639},
  {"indice":"iquique","ciudad":"Iquique","reg":"01b","lat":-20.216,"lon":-70.153},
  {"indice":"pica","ciudad":"Pica","reg":"01b","lat":-20.491,"lon":-69.329},
  {"indice":"ollague","ciudad":"Ollague","reg":"02","lat":-21.225,"lon":-68.254},
  {"indice":"tocopilla","ciudad":"Tocopilla","reg":"02","lat":-22.092,"lon":-70.197},
  {"indice":"calama","ciudad":"Calama","reg":"02","lat":-22.456,"lon":-68.923},
  {"indice":"snpedro","ciudad":"San Pedro de Atacama","reg":"02","lat":-22.911,"lon":-68.201},
  {"indice":"mejillones","ciudad":"Mejillones","reg":"02","lat":-23.100,"lon":-70.450},
  {"indice":"antofagasta","ciudad":"Antofagasta","reg":"02","lat":-23.650,"lon":-70.400},
  {"indice":"taltal","ciudad":"Taltal","reg":"02","lat":-25.408,"lon":-70.485},
  {"indice":"salvador","ciudad":"El Salvador","reg":"03","lat":-26.314,"lon":-69.544},
  {"indice":"chanaral","ciudad":"Chanaral","reg":"03","lat":-26.348,"lon":-70.623},
  {"indice":"caldera","ciudad":"Caldera","reg":"03","lat":-27.067,"lon":-70.825},
  {"indice":"copiapo","ciudad":"Copiapo","reg":"03","lat":-27.366,"lon":-70.332},
  {"indice":"huasco","ciudad":"Huasco","reg":"03","lat":-28.464,"lon":-71.218},
  {"indice":"vallenar","ciudad":"Vallenar","reg":"03","lat":-28.576,"lon":-70.759},
  {"indice":"serena","ciudad":"La Serena","reg":"04","lat":-29.902,"lon":-71.251},
  {"indice":"vicuna","ciudad":"Vicuna","reg":"04","lat":-30.031,"lon":-70.708},
  {"indice":"ovalle","ciudad":"Ovalle","reg":"04","lat":-30.598,"lon":-71.200},
  {"indice":"illapel","ciudad":"Illapel","reg":"04","lat":-31.633,"lon":-71.170},
  {"indice":"vilos","ciudad":"Los Vilos","reg":"04","lat":-31.908,"lon":-71.507},
  {"indice":"papudo","ciudad":"Papudo","reg":"05","lat":-32.507,"lon":-71.441},
  {"indice":"valpo","ciudad":"Valparaiso","reg":"05","lat":-33.047,"lon":-71.613},
  {"indice":"vdelmar","ciudad":"Vina del Mar","reg":"05","lat":-33.024,"lon":-71.552},
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
  {"indice":"curico","ciudad":"Curico","reg":"07","lat":-34.982,"lon":-71.239},
  {"indice":"talca","ciudad":"Talca","reg":"07","lat":-35.426,"lon":-71.655},
  {"indice":"constitucion","ciudad":"Constitucion","reg":"07","lat":-35.333,"lon":-72.417},
  {"indice":"linares","ciudad":"Linares","reg":"07","lat":-35.846,"lon":-71.593},
  {"indice":"chillan","ciudad":"Chillan","reg":"08a","lat":-36.606,"lon":-72.103},
  {"indice":"concepcion","ciudad":"Concepcion","reg":"08b","lat":-36.827,"lon":-73.050},
  {"indice":"angeles","ciudad":"Los Angeles","reg":"08b","lat":-37.469,"lon":-72.353},
  {"indice":"angol","ciudad":"Angol","reg":"09","lat":-37.798,"lon":-72.716},
  {"indice":"temuco","ciudad":"Temuco","reg":"09","lat":-38.739,"lon":-72.598},
  {"indice":"villarica","ciudad":"Villarrica","reg":"09","lat":-39.285,"lon":-72.227},
  {"indice":"valdivia","ciudad":"Valdivia","reg":"10a","lat":-39.814,"lon":-73.245},
  {"indice":"osorno","ciudad":"Osorno","reg":"10b","lat":-40.574,"lon":-73.133},
  {"indice":"pmontt","ciudad":"Puerto Montt","reg":"10b","lat":-41.469,"lon":-72.942},
  {"indice":"ancud","ciudad":"Ancud","reg":"10b","lat":-41.870,"lon":-73.820},
  {"indice":"castro","ciudad":"Castro","reg":"10b","lat":-42.482,"lon":-73.764},
  {"indice":"chaiten","ciudad":"Chaiten","reg":"10b","lat":-42.915,"lon":-72.707},
  {"indice":"coyhaique","ciudad":"Coyhaique","reg":"11","lat":-45.571,"lon":-72.068},
  {"indice":"balmaceda","ciudad":"Balmaceda","reg":"11","lat":-45.915,"lon":-71.689},
  {"indice":"cochrane","ciudad":"Cochrane","reg":"11","lat":-47.255,"lon":-72.573},
  {"indice":"natales","ciudad":"Puerto Natales","reg":"12","lat":-51.726,"lon":-72.506},
  {"indice":"parenas","ciudad":"Punta Arenas","reg":"12","lat":-53.163,"lon":-70.917},
  {"indice":"porvenir","ciudad":"Porvenir","reg":"12","lat":-53.296,"lon":-70.366},
  {"indice":"pwilliams","ciudad":"Puerto Williams","reg":"12","lat":-54.935,"lon":-67.605},
  {"indice":"rapanui","ciudad":"Rapa Nui","reg":"ip","lat":-27.112,"lon":-109.349},
  {"indice":"jfernandez","ciudad":"Juan Fernandez","reg":"jf","lat":-33.639,"lon":-78.829},
  {"indice":"antartica","ciudad":"Antartica","reg":"an","lat":-62.190,"lon":-58.986},
]
LOC_BY_INDICE = {p["indice"]: p for p in DMC_LOCALITIES}

TEXT_TO_CODE = {
    "despejado":0,"soleado":1,"mayormente despejado":1,"mayormente soleado":1,
    "parcialmente nublado":2,"nublado":3,"cubierto":3,"mayormente nublado":3,
    "niebla":45,"neblina":45,"lluvia debil":61,"lluvia ligera":61,
    "lluvia":63,"lluvia intensa":65,"llovizna":51,
    "chubascos":80,"nieve":73,"tormenta":95,
}

def nrm(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip()

def text_to_wcode(t):
    n = nrm(t)
    for k, v in sorted(TEXT_TO_CODE.items(), key=lambda x: -len(x[0])):
        if k in n: return v
    return 1

def fetch_text(url):
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=25) as r:
        raw = r.read()
    for enc in ("utf-8", "latin-1", "iso-8859-1"):
        try: return raw.decode(enc)
        except Exception: pass
    return raw.decode("latin-1", errors="replace")

def get_all_js(html, base_url):
    merged = html
    pat_inline = re.compile(r"<script[^>]*>([\s\S]*?)</script>", re.IGNORECASE)
    for m in pat_inline.finditer(html):
        merged += "\n" + m.group(1)
    pat_src = re.compile(r'<script[^>]+src="([^"]+)"')
    for m in pat_src.finditer(html):
        src = m.group(1)
        if not src.startswith("http"):
            p = urlparse(base_url)
            src = (p.scheme+"://"+p.netloc+src) if src.startswith("/") else (base_url.rsplit("/",1)[0]+"/"+src)
        try: merged += "\n" + fetch_text(src)
        except Exception: pass
    return merged

def parse_temp(val):
    if not isinstance(val, list) or not val: return [], []
    if isinstance(val[0], list):
        return [v[0] if v else None for v in val], [v[1] if len(v)>1 else None for v in val]
    if len(val) >= 2 and len(val) % 2 == 0:
        return [val[i] for i in range(0,len(val),2)], [val[i] for i in range(1,len(val),2)]
    return val, val

def pad(arr, n, d=None):
    arr = list(arr) if arr else []
    return (arr + [d]*n)[:n]

def infer_dates(tope, fecha=None):
    today = date.today()
    if fecha and len(fecha) >= tope:
        out = []
        for i, f in enumerate(fecha[:tope]):
            try:
                day = int(re.search(r"\d+", str(f)).group())
                if not out:
                    c = today.replace(day=day)
                    if c < today - timedelta(days=1):
                        m2 = today.month+1 if today.month < 12 else 1
                        y2 = today.year if today.month < 12 else today.year+1
                        c = date(y2, m2, day)
                else:
                    c = date.fromisoformat(out[-1]) + timedelta(days=1)
                out.append(c.isoformat())
            except Exception:
                out.append((today+timedelta(days=i)).isoformat())
        return out
    return [(today+timedelta(days=i)).isoformat() for i in range(tope)]

def item_to_entry(item, reg):
    indice = str(item.get("indice","")).lower().strip()
    if not indice or indice not in LOC_BY_INDICE: return None
    tope = int(item.get("tope", 0))
    if tope <= 0: tope = len(item.get("fecha", item.get("texto", [])))
    if tope <= 0: return None
    loc = LOC_BY_INDICE[indice]
    fecha = item.get("fecha", item.get("date", []))
    texto = item.get("texto", item.get("text", []))
    temp  = item.get("temperatura", item.get("temperature", item.get("temp", [])))
    viento = item.get("viento", item.get("wind", []))
    precip = item.get("precipitacion", item.get("precip", []))
    mins, maxs = parse_temp(temp)
    dates = infer_dates(tope, fecha)
    texts = pad(texto, tope, "")
    tmins = pad(mins, tope)
    tmaxs = pad(maxs, tope)
    wind_max = []
    for w in pad(viento, tope):
        if w is None: wind_max.append(None)
        elif isinstance(w, (int, float)): wind_max.append(float(w))
        else:
            nums = re.findall(r"\d+", str(w))
            wind_max.append(max(int(x) for x in nums) if nums else None)
    prec_arr = []
    for p2 in pad(precip, tope, 0):
        try: prec_arr.append(float(p2) if p2 else 0.0)
        except Exception: prec_arr.append(0.0)
    return {
        "indice": indice, "ciudad": loc["ciudad"], "reg": reg,
        "lat": loc["lat"], "lon": loc["lon"],
        "daily": {
            "time": dates,
            "temperature_2m_max": tmaxs,
            "temperature_2m_min": tmins,
            "precipitation_sum": prec_arr,
            "wind_speed_10m_max": wind_max,
            "weather_code": [text_to_wcode(t) for t in texts],
            "summary_text": texts,
        },
        "horizon_days": tope,
    }

def extract_items(js):
    items = []
    for vname in ["Pronostico","pronostico","datos","Datos","forecast","data"]:
        m = re.search(vname + r"\s*=\s*(\[[\s\S]*?\])\s*;", js)
        if m:
            try:
                raw = re.sub(r",\s*([\}\]])", r"\1", m.group(1))
                arr = json.loads(raw)
                if isinstance(arr, list) and arr:
                    print("  var "+vname+": "+str(len(arr))+" items")
                    return arr
            except Exception as e:
                print("  parse err "+vname+": "+str(e)[:80])
    for m in re.finditer(r"[Pp]ronostico\.push\s*\(\s*\{", js):
        start = m.end()-1
        depth,i = 0, start
        while i < len(js) and i < start+8000:
            c = js[i]
            if c == "{": depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    try:
                        raw = re.sub(r",\s*([\}\]])", r"\1", js[start:i+1])
                        items.append(json.loads(raw))
                    except Exception: pass
                    break
            i += 1
    if items: print("  push(): "+str(len(items))+" items")
    return items

def process_region(reg):
    url = "https://archivos.meteochile.gob.cl/portaldmc/pronosticos/pronosticoRegion.php?reg="+reg
    html = fetch_text(url)
    if reg == "05m":
        print("[DEBUG 05m] HTML="+str(len(html))+" chars")
        for kw in ["Pronostico","pronostico","temperatura","stgoc","push(","JSON"]:
            print("[DEBUG 05m] "+kw+": "+str(html.count(kw)))
        print("[DEBUG 05m] HTML inicio:")
        print(html[:1200])
    js = get_all_js(html, url)
    if reg == "05m":
        print("[DEBUG 05m] JS total="+str(len(js)))
    items = extract_items(js)
    results = {}
    for item in items:
        if isinstance(item, dict):
            entry = item_to_entry(item, reg)
            if entry: results[entry["indice"]] = entry
    return results

def main():
    cache = {"generated_at": datetime.utcnow().isoformat()+"Z", "localities": {}}
    ok, fail = 0, 0
    for reg in DMC_REGIONS:
        try:
            data = process_region(reg)
            cache["localities"].update(data)
            ok += len(data)
            print("OK "+reg+": "+str(len(data)))
        except Exception as e:
            fail += 1
            print("FAIL "+reg+": "+str(e))
    cache["stats"] = {"ok_localities": ok, "fail_regions": fail}
    with open("dmc_cache.json", "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    print("TOTAL: "+str(ok)+" localidades, "+str(fail)+" fallos")

if __name__ == "__main__":
    main()
