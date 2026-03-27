import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as c:
        try:
            r = await c.get("https://api.okx.com/api/v5/public/funding-rate?instType=SWAP", headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
            print("OKX (API):", r.status_code, len(r.json().get("data", [])))
        except Exception as e:
            print("OKX API Error:", e)

if __name__ == "__main__":
    asyncio.run(test())
