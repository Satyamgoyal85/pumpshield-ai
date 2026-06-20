"use client";

import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import AnalysisHistoryTable from "@/components/AnalysisHistoryTable";
import { useAuth } from "@/lib/useAuth";
import { api, AnalysisSummary } from "@/lib/api";

export default function HistoryPage() {
  const { loading: authLoading } = useAuth(true);
  const [items, setItems] = useState<AnalysisSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading) {
      api
        .history(0, 50)
        .then((res) => {
          setItems(res.items);
          setTotal(res.total);
        })
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [authLoading]);

  if (authLoading || loading) {
    return <div className="min-h-screen flex items-center justify-center text-gray-400">Loading...</div>;
  }

  return (
    <>
      <Navbar />
      <main className="max-w-5xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-2">Analysis History</h1>
        <p className="text-gray-400 mb-8">{total} total analyses</p>
        <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-6">
          <AnalysisHistoryTable items={items} />
        </div>
      </main>
    </>
  );
}
