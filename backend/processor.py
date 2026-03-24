import pandas as pd
import re

def clean_properties(raw_data):
    if not raw_data:
        return pd.DataFrame()
        
    df = pd.DataFrame(raw_data)
    
    # 1. 家賃を数値（万円）に変換 "9.4万円" -> 9.4
    df['rent_num'] = df['rent'].str.extract(r'(\d+\.?\d*)').astype(float)
    
    # 2. 管理費を数値（万円）に変換 "5000円" -> 0.5 / "-" -> 0.0
    def parse_admin(x):
        if x == '-' or 'N/A' in str(x): return 0.0
        val = re.search(r'(\d+)', str(x))
        return float(val.group(1)) / 10000 if val else 0.0
    df['admin_num'] = df['admin'].apply(parse_admin)
    
    # 3. 築年数を数値に変換 "築20年" -> 20 / "新築" -> 0
    def parse_age(x):
        if '新築' in str(x): return 0
        val = re.search(r'築(\d+)年', str(x))
        return int(val.group(1)) if val else 0 # Noneではなく0かデフォルト値を入れておくと計算が楽です
    df['age_num'] = df['age_floor'].apply(parse_age)
    
    # 4. 専有面積を数値に変換 "52.55m2" -> 52.55
    df['area_num'] = df['menseki'].str.extract(r'(\d+\.?\d*)').astype(float)
    
    # 5. 駅徒歩（最短分）を抽出 "歩14分" -> 14
    def parse_walk(x):
        walk_times = re.findall(r'歩(\d+)分', str(x))
        if walk_times:
            return min([int(t) for t in walk_times])
        return 0
    df['walk_num'] = df['access'].apply(parse_walk)

    # --- 必要な列だけ抽出して整理 ---
    # layout を追加。計算不要な項目はそのままパススルーさせます
    cols = [
        'title', 'rent_num', 'admin_num', 'age_num', 
        'area_num', 'walk_num', 'address', 'detail_url', 'layout'
    ]
    
    # 念のためカラムが存在するかチェックして抽出
    result_df = df[[c for c in cols if c in df.columns]]
    return result_df
    