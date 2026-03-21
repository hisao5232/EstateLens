import pandas as pd
import re

def clean_properties(raw_data):
    df = pd.DataFrame(raw_data)
    
    # 1. 家賃を数値（万円）に変換
    df['rent_num'] = df['rent'].str.extract(r'(\d+\.?\d*)').astype(float)
    
    # 2. 管理費を数値（万円）に変換
    def parse_admin(x):
        if x == '-' or 'N/A' in x: return 0.0
        val = re.search(r'(\d+)', x)
        return float(val.group(1)) / 10000 if val else 0.0
    df['admin_num'] = df['admin'].apply(parse_admin)
    
    # 3. 築年数を数値に変換（新築=0）
    def parse_age(x):
        if '新築' in x: return 0
        val = re.search(r'築(\d+)年', x)
        return int(val.group(1)) if val else None
    df['age_num'] = df['age_floor'].apply(parse_age)
    
    # 4. 専有面積を数値に変換
    df['area_num'] = df['menseki'].str.extract(r'(\d+\.?\d*)').astype(float)
    
    # 5. 駅徒歩（最短分）を抽出
    def parse_walk(x):
        walk_times = re.findall(r'歩(\d+)分', x)
        if walk_times:
            return min([int(t) for t in walk_times])
        return None
    df['walk_num'] = df['access'].apply(parse_walk)

    # 必要な列だけ抽出
    result_df = df[['title', 'address', 'rent_num', 'admin_num', 'age_num', 'area_num', 'walk_num', 'detail_url']]
    return result_df

# テスト用
if __name__ == "__main__":
    # ここに取得したraw_dataを渡して動作確認可能
    pass
    