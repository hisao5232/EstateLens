'use client';

import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function Home() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/analysis/stats`, {
          headers: { 'X-API-KEY': process.env.NEXT_PUBLIC_API_KEY || '' },
        });
        const data = await res.json();
        setStats(data);
      } catch (err) {
        console.error("Error fetching stats:", err);
      }
    };
    fetchStats();
  }, []);

  if (!stats) return <div className="p-10 text-center text-xl">Loading Data...</div>;

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-6xl">
        <header className="mb-10 text-center md:text-left">
          <h1 className="text-3xl font-bold text-gray-800">EstateLens Dashboard</h1>
          <p className="text-gray-500">本郷台・大船エリア 不動産分析 (データ数: {stats.total_count || 0}件)</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
          {/* 平均家賃カード：データがすでに「万円」単位なのでそのまま表示 */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 transition-transform hover:scale-[1.02]">
            <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider">平均家賃</h2>
            <p className="text-4xl font-bold text-blue-600 mt-2">
              {Number(stats.avg_rent || 0).toFixed(1)}
              <span className="text-xl ml-1">万円</span>
            </p>
          </div>

          {/* 1㎡あたりの単価：0.225...万円を円単位（2,254円）に変換して表示 */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 transition-transform hover:scale-[1.02]">
            <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider">1㎡あたりの単価</h2>
            <p className="text-4xl font-bold text-green-600 mt-2">
              ¥{Math.round(Number(stats.avg_unit_price || 0) * 10000).toLocaleString()}
            </p>
          </div>
        </div>

        {/* グラフセクション */}
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
          <h2 className="text-xl font-bold mb-8 text-gray-700">築年数別の家賃・物件数分布</h2>
          <div className="h-100 w-full min-h-100">
            {stats.age_dist && stats.age_dist.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.age_dist} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="age_group" 
                    label={{ value: '築年数(年)', position: 'insideBottom', offset: -10 }}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis 
                    yAxisId="left" 
                    label={{ value: '家賃(万円)', angle: -90, position: 'insideLeft', offset: 10 }}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis 
                    yAxisId="right" 
                    orientation="right" 
                    label={{ value: '物件数(件)', angle: 90, position: 'insideRight', offset: 10 }}
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip 
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  />
                  <Legend verticalAlign="top" align="right" height={36}/>
                  <Bar yAxisId="left" dataKey="rent" name="平均家賃(万円)" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={40} />
                  <Bar yAxisId="right" dataKey="count" name="物件数" fill="#10b981" radius={[4, 4, 0, 0]} barSize={40} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-gray-400">
                表示できるデータがありません
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
