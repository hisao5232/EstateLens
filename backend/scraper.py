import os
import asyncio
from playwright.async_api import async_playwright

async def fetch_data(): # 引数なし（全件）
    target_url = os.getenv("TARGET_URL")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"Starting Scraper. Target: {target_url}")
        all_rooms = []
        current_page = 0
        
        try:
            await page.goto(target_url, wait_until="networkidle")
            
            while True: # 無限ループで「次へ」がなくなるまで回す
                current_page += 1
                print(f"--- Processing Page {current_page} ---")
                
                # 物件リストの待機
                try:
                    await page.wait_for_selector(".cassetteitem", timeout=10000)
                except:
                    print(f"Page {current_page}: No cassette items found. Ending.")
                    break
                
                # --- 現在のページのスクレイピング処理 ---
                items = await page.query_selector_all(".cassetteitem")
                for item in items:
                    # 物件共通情報
                    base_info = {
                        "title": await (await item.query_selector(".cassetteitem_content-title")).inner_text() if await item.query_selector(".cassetteitem_content-title") else "N/A",
                        "address": await (await item.query_selector(".cassetteitem_detail-col1")).inner_text() if await item.query_selector(".cassetteitem_detail-col1") else "N/A",
                        "access": await (await item.query_selector(".cassetteitem_detail-col2")).inner_text() if await item.query_selector(".cassetteitem_detail-col2") else "N/A",
                        "age_floor": await (await item.query_selector(".cassetteitem_detail-col3")).inner_text() if await item.query_selector(".cassetteitem_detail-col3") else "N/A",
                    }

                    # 部屋情報
                    rooms = await item.query_selector_all(".cassetteitem-item tbody")
                    for room in rooms:
                        floor_el = await room.query_selector("td:nth-child(3)")
                        rent_el = await room.query_selector("td:nth-child(4) li:nth-child(1) span")
                        admin_el = await room.query_selector("td:nth-child(4) li:nth-child(2) span")
                        url_el = await room.query_selector("td.ui-text--midium.ui-text--bold a")
                        # --- 【追加・修正】間取りと面積のセレクター ---
                        # 6番目のtdの、1番目のliが「間取り」、2番目が「面積」
                        layout_el = await room.query_selector("td:nth-child(6) li:nth-child(1) span")
                        menseki_el = await room.query_selector("td:nth-child(6) li:nth-child(2) span")

                        all_rooms.append({
                            **base_info,
                            "floor": await floor_el.inner_text() if floor_el else "N/A",
                            "rent": await rent_el.inner_text() if rent_el else "N/A",
                            "admin": await admin_el.inner_text() if admin_el else "N/A",
                            "layout": await layout_el.inner_text() if layout_el else "N/A", # ← 【追加】
                            "detail_url": "https://suumo.jp" + await url_el.get_attribute("href") if url_el else "N/A",
                            "menseki": await menseki_el.inner_text() if menseki_el else "0m2"
                        })

                print(f"Page {current_page} done. Total rooms so far: {len(all_rooms)}")

                # --- 「次へ」ボタンの判定 ---
                next_button = await page.query_selector("text='次へ'")
                if next_button:
                    await next_button.click()
                    await page.wait_for_load_state("networkidle")
                    await asyncio.sleep(2) # 負荷軽減のために少し長めに待機
                else:
                    print("Reached the last page.")
                    break

            print(f"【取得完了】全 {current_page} ページから合計 {len(all_rooms)} 件抽出しました。")
            return all_rooms
                
        except Exception as e:
            print(f"エラー発生: {e}")
            return all_rooms
        finally:
            await browser.close()
