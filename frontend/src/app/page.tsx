'use client';

import { useEffect, useState } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, 
  ScatterChart, Scatter, ZAxis 
} from 'recharts';

export default function Home() {
  const [stats, setStats] = useState<any>(null);
  const [rawData, setRawData] = useState<any[]>([]); // 散布図用の生データ

  useEffect(() => {
    const fetchData = async () => {
      const headers = { 'X-API-KEY': process.env.NEXT_PUBLIC_API_KEY || '' };
      
      try {
        // 1. 既存の統計データ取得
        const statsRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/analysis/stats`, { headers });
        const statsJson = await statsRes.json();
        setStats(statsJson);

        // 2. 新規：散布図用の生データ取得
        const rawRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/analysis/raw`, { headers });
        const rawJson = await rawRes.json();
        
        // 坪単価を計算して追加
        const processedRaw = rawJson.map((item: any) => ({
          ...item,
          tsubo_tanaka: item.area_num > 0 ? (item.total_rent / item.area_num * 3.30578) : 0
        }));
        setRawData(processedRaw);

      } catch (err) {
        console.error("Error fetching data:", err);
      }
    };
    fetchData();
  }, []);

  if (!stats) return <div className="p-10 text-center text-xl font-mono">Loading Estate Data...</div>;

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-6xl">
        <header className="mb-10 text-center md:text-left">
          <h1 className="text-3xl font-bold text-gray-800">EstateLens Dashboard</h1>
          <p className="text-gray-500">本郷台・大船エリア 不動産分析 (データ数: {stats.total_count || 0}件)</p>
        </header>

        {/* 既存のカードセクション */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 transition-transform hover:scale-[1.01]">
            <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider">平均家賃</h2>
            <p className="text-4xl font-bold text-blue-600 mt-2">
              {Number(stats.avg_rent || 0).toFixed(1)}
              <span className="text-xl ml-1">万円</span>
            </p>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 transition-transform hover:scale-[1.01]">
            <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider">1㎡あたりの単価</h2>
            <p className="text-4xl font-bold text-green-600 mt-2">
              ¥{Math.round(Number(stats.avg_unit_price || 0) * 10000).toLocaleString()}
            </p>
          </div>
        </div>

        {/* グラフエリア */}
        <div className="flex flex-col gap-10">
          
          {/* 1. 既存の棒グラフ */}
          <section className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-bold mb-8 text-gray-700">築年数別の家賃・物件数分布</h2>
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.age_dist}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                  <XAxis dataKey="age_group" tick={{fontSize: 12}} />
                  <YAxis yAxisId="left" tick={{fontSize: 12}} />
                  <YAxis yAxisId="right" orientation="right" tick={{fontSize: 12}} />
                  <Tooltip />
                  <Legend verticalAlign="top" align="right" />
                  <Bar yAxisId="left" dataKey="rent" name="平均家賃(万円)" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  <Bar yAxisId="right" dataKey="count" name="物件数" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>

          {/* 2. 新規：坪単価 × 築年数 散布図 */}
          <section className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-bold mb-2 text-gray-700">坪単価 vs 築年数 散布図</h2>
            <p className="text-sm text-gray-400 mb-8">築年数が経過しても資産価値（坪単価）を維持している物件を探す</p>
            <div className="h-96 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    type="number" 
                    dataKey="age_num" 
                    name="築年数" 
                    unit="年" 
                    label={{ value: '築年数', position: 'insideBottom', offset: -10 }} 
                  />
                  <YAxis 
                    type="number" 
                    dataKey="tsubo_tanaka" 
                    name="坪単価" 
                    unit="万" 
                    label={{ value: '坪単価(万円)', angle: -90, position: 'insideLeft' }} 
                  />
                  <ZAxis type="number" range={[60, 60]} /> 
                  <Tooltip 
                    cursor={{ strokeDasharray: '3 3' }}
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const d = payload[0].payload;
                        return (
                          <div className="bg-white p-4 border border-gray-200 shadow-xl rounded-lg text-sm">
                            <p className="font-bold text-gray-800 border-b mb-2 pb-1">{d.title}</p>
                            <p>築年数: <span className="font-semibold">{d.age_num}年</span></p>
                            <p>坪単価: <span className="font-semibold text-blue-600">{d.tsubo_tanaka.toFixed(1)}万円</span></p>
                            <p>家賃計: {d.total_rent}万円 ({d.area_num}㎡)</p>
                            <p className="text-xs text-gray-400 mt-2 truncate w-40">{d.address}</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Scatter name="物件データ" data={rawData} fill="#6366f1" />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </section>

        </div>
      </div>
    </main>
  );
}
