"use client";

import Link from "next/link";
import type { AnalysisSummary } from "@/lib/api";

interface Props {
  items: AnalysisSummary[];
}

export default function AnalysisHistoryTable({ items }: Props) {
  if (items.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No analyses yet. <Link href="/analyze" className="text-emerald-400 hover:underline">Analyze a stock</Link>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-800 text-gray-400 text-left">
            <th className="py-3 pr-4">Symbol</th>
            <th className="py-3 pr-4">Score</th>
            <th className="py-3 pr-4">Level</th>
            <th className="py-3 pr-4">Date</th>
            <th className="py-3">Action</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} className="border-b border-gray-800/50 hover:bg-gray-900/50">
              <td className="py-3 pr-4 font-medium">{item.stock_symbol}</td>
              <td className="py-3 pr-4">{item.risk_score}</td>
              <td className="py-3 pr-4">
                <span
                  className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                    item.risk_level === "red"
                      ? "bg-red-500/20 text-red-300"
                      : "bg-emerald-500/20 text-emerald-300"
                  }`}
                >
                  {item.risk_level}
                </span>
              </td>
              <td className="py-3 pr-4 text-gray-400">
                {new Date(item.created_at).toLocaleDateString()}
              </td>
              <td className="py-3">
                <Link href={`/analyze?id=${item.id}`} className="text-emerald-400 hover:underline">
                  View
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
