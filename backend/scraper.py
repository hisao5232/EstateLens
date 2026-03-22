import os
import asyncio
from playwright.async_api import async_playwright

async def fetch_data(max_pages=5): # 最大ページ数を引数で指定可能に
    target_url = os.getenv("TARGET_URL")
    
    async with async_playwright() as p:
        # 安定性を高めるため、少しゆっくり動かす設定（slow_mo）
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"Starting Scraper. Target: {target_url}")
        all_rooms = []
        
        try:
            await page.goto(target_url, wait_until="networkidle")
            
            for current_page in range(1, max_pages + 1):
                print(f"--- Processing Page {current_page} ---")
                
                # 物件リストが表示されるまで待機
                await page.wait_for_selector(".cassetteitem", timeout=10000)
                
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
                        # (必要に応じて他の項目も追加してください)

                        room_data = {
                            **base_info,
                            "floor": await floor_el.inner_text() if floor_el else "N/A",
                            "rent": await rent_el.inner_text() if rent_el else "N/A",
                            "admin": await admin_el.inner_text() if admin_el else "N/A",
                            "detail_url": "https://suumo.jp" + await url_el.get_attribute("href") if url_el else "N/A"
                            # 以前の processor.py が期待する形式に合わせる
                            , "menseki": await (await room.query_selector("td:nth-child(6) li:nth-child(2) span")).inner_text() if await room.query_selector("td:nth-child(6) li:nth-child(2) span") else "0m2"
                        }
                        all_rooms.append(room_data)

                print(f"Page {current_page} done. Total rooms so far: {len(all_rooms)}")

                # --- 次のページへの遷移処理 ---
                if current_page < max_pages:
                    # 「次へ」ボタンを探す
                    next_button = await page.query_selector("text='次へ'")
                    if next_button:
                        await next_button.click()
                        # ページ遷移を待つ
                        await page.wait_for_load_state("networkidle")
                        # 負荷軽減のための待機
                        await asyncio.sleep(1) 
                    else:
                        print("No more pages found.")
                        break

            print(f"【取得完了】全 {current_page} ページから合計 {len(all_rooms)} 件抽出しました。")
            return all_rooms
                
        except Exception as e:
            print(f"エラー発生: {e}")
            return all_rooms # エラーが起きてもそこまでの分を返す
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
    