"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import AnalysisHistoryTable from "@/components/AnalysisHistoryTable";
import StockSearchForm from "@/components/StockSearchForm";
import { useAuth } from "@/lib/useAuth";
import { api, AnalysisSummary } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const { user, loading } = useAuth(true);
  const router = useRouter();
  const [recent, setRecent] = useState<AnalysisSummary[]>([]);

  useEffect(() => {
    if (!loading) {
      api.history(0, 5).then((res) => setRecent(res.items)).catch(() => {});
    }
  }, [loading]);

  function handleSearch(symbol: string) {
    router.push(`/analyze?symbol=${encodeURIComponent(symbol)}`);
  }

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-gray-400">Loading...</div>;
  }

  return (
    <>
      <Navbar />
      <main className="max-w-5xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-2">Welcome, {user?.name}</h1>
        <p className="text-gray-400 mb-8">
          Search any stock symbol to get an AI-powered fraud risk assessment.
        </p>

        <div className="mb-10">
          <StockSearchForm onSubmit={handleSearch} />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
          <div className="rounded-xl border border-gray-800 bg-gray-900/50 p-5">
            <p className="text-gray-400 text-sm">Risk Zones</p>
            <p className="text-lg font-semibold mt-1">
              <span className="text-emerald-400">Green 0–79</span>
              <span className="text-gray-600 mx-2">|</span>
              <span className="text-red-400">Red 80–100</span>
            </p>
          </div>
          <div className="rounded-xl border border-gray-800 bg-gray-900/50 p-5">
            <p className="text-gray-400 text-sm">Quick Analyze</p>
            <Link href="/analyze?symbol=AAPL" className="text-emerald-400 hover:underline font-semibold">
              Try AAPL →
            </Link>
          </div>
          <div className="rounded-xl border border-gray-800 bg-gray-900/50 p-5">
            <p className="text-gray-400 text-sm">Full History</p>
            <Link href="/history" className="text-emerald-400 hover:underline font-semibold">
              View all →
            </Link>
          </div>
        </div>

        <h2 className="text-xl font-semibold mb-4">Recent Analyses</h2>
        <AnalysisHistoryTable items={recent} />
      </main>
    </>
  );
}
