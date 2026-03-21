import os
from playwright.async_api import async_playwright

async def fetch_data():
    target_url = os.getenv("TARGET_URL")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"Accessing: {target_url}")
        all_rooms = []
        
        try:
            await page.goto(target_url, wait_until="networkidle")
            await page.wait_for_selector(".cassetteitem", timeout=10000)
            
            # 物件（カセット）ごとのループ
            items = await page.query_selector_all(".cassetteitem")
            
            for item in items:
                # --- 物件共通情報 ---
                base_info = {
                    "title": await (await item.query_selector(".cassetteitem_content-title")).inner_text() if await item.query_selector(".cassetteitem_content-title") else "N/A",
                    "address": await (await item.query_selector(".cassetteitem_detail-col1")).inner_text() if await item.query_selector(".cassetteitem_detail-col1") else "N/A",
                    "access": await (await item.query_selector(".cassetteitem_detail-col2")).inner_text() if await item.query_selector(".cassetteitem_detail-col2") else "N/A",
                    "age_floor": await (await item.query_selector(".cassetteitem_detail-col3")).inner_text() if await item.query_selector(".cassetteitem_detail-col3") else "N/A",
                }

                # --- 部屋ごとの情報（テーブルの行を取得） ---
                # 各物件カセット内の tbody (部屋のリスト) をループ
                rooms = await item.query_selector_all(".cassetteitem-item tbody")
                
                for room in rooms:
                    # 各カラムを順番に取得（td:nth-child を活用）
                    # 階数 (td:nth-child(3))
                    floor_el = await room.query_selector("td:nth-child(3)")
                    # 賃料 (td:nth-child(4) の li:nth-child(1))
                    rent_el = await room.query_selector("td:nth-child(4) li:nth-child(1) span")
                    # 管理費 (td:nth-child(4) の li:nth-child(2))
                    admin_el = await room.query_selector("td:nth-child(4) li:nth-child(2) span")
                    # 敷金 (td:nth-child(5) の li:nth-child(1))
                    deposit_el = await room.query_selector("td:nth-child(5) li:nth-child(1) span")
                    # 礼金 (td:nth-child(5) の li:nth-child(2))
                    gratuity_el = await room.query_selector("td:nth-child(5) li:nth-child(2) span")
                    # 間取り (td:nth-child(6) の li:nth-child(1))
                    madori_el = await room.query_selector("td:nth-child(6) li:nth-child(1) span")
                    # 面積 (td:nth-child(6) の li:nth-child(2))
                    menseki_el = await room.query_selector("td:nth-child(6) li:nth-child(2) span")
                    # 詳細URL (td.ui-text--midium.ui-text--bold a)
                    url_el = await room.query_selector("td.ui-text--midium.ui-text--bold a")

                    # 物件共通情報と部屋情報を合体
                    room_data = {
                        **base_info,
                        "floor": await floor_el.inner_text() if floor_el else "N/A",
                        "rent": await rent_el.inner_text() if rent_el else "N/A",
                        "admin": await admin_el.inner_text() if admin_el else "N/A",
                        "deposit": await deposit_el.inner_text() if deposit_el else "N/A",
                        "gratuity": await gratuity_el.inner_text() if gratuity_el else "N/A",
                        "madori": await madori_el.inner_text() if madori_el else "N/A",
                        "menseki": await menseki_el.inner_text() if menseki_el else "N/A",
                        "detail_url": "https://suumo.jp" + await url_el.get_attribute("href") if url_el else "N/A"
                    }
                    all_rooms.append(room_data)

            print(f"【取得完了】合計 {len(all_rooms)} 件の部屋データを抽出しました。")
            return all_rooms
                
        except Exception as e:
            print(f"エラー発生: {e}")
            return []
        finally:
            await browser.close()

if __name__ == "__main__":
    import asyncio
    import json

    async def main():
        data = await fetch_data()
        # 最初の5件をインデント付きで表示
        print("\n--- 取得データのサンプル（先頭5件） ---")
        print(json.dumps(data[:5], indent=2, ensure_ascii=False))
        
        # 統計的な確認
        if data:
            print(f"\nTotal items: {len(data)}")
            print(f"Keys available: {data[0].keys()}")

    asyncio.run(main())
    