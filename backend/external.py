import httpx
from datetime import date

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WX_URL  = "https://api.open-meteo.com/v1/forecast"
GEO_INFO = "https://restcountries.com/v3.1/name/"

async def geocode(loc: str):
    params = {"name": loc, "count": 1}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(GEO_URL, params=params)
        r.raise_for_status()
        js = r.json()
        if js.get("results"):
            it = js["results"][0]
            return {"lat": it["latitude"], "lon": it["longitude"], "name": it["name"], "country": it.get("country")}
    return None


async def country_info(loc: str):
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(f"{GEO_INFO}{loc}", params={"fullText": "true"})
            r.raise_for_status()
            data = r.json()
            if isinstance(data, list) and data:
                return data[0]
            return data
    except httpx.HTTPStatusError as e:
        return None
    except Exception as e:
        return None
