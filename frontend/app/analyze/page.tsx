"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Navbar from "@/components/Navbar";
import RiskScoreCard from "@/components/RiskScoreCard";
import IndicatorBreakdown from "@/components/IndicatorBreakdown";
import StockSearchForm from "@/components/StockSearchForm";
import { useAuth } from "@/lib/useAuth";
import { api, Analysis } from "@/lib/api";

function AnalyzeContent() {
  const { loading: authLoading } = useAuth(true);
  const searchParams = useSearchParams();
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const runAnalysis = useCallback(async (symbol: string) => {
    setError("");
    setLoading(true);
    setAnalysis(null);
    try {
      const result = await api.analyze(symbol);
      setAnalysis(result);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const symbol = searchParams.get("symbol");
    const id = searchParams.get("id");
    if (id && !authLoading) {
      api.getAnalysis(Number(id)).then(setAnalysis).catch((e) => setError(e.message));
    } else if (symbol && !authLoading) {
      runAnalysis(symbol);
    }
  }, [searchParams, authLoading, runAnalysis]);

  if (authLoading) {
    return <div className="min-h-screen flex items-center justify-center text-gray-400">Loading...</div>;
  }

  return (
    <>
      <Navbar />
      <main className="max-w-5xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-2">Stock Analysis</h1>
        <p className="text-gray-400 mb-8">Enter a stock symbol to detect pump-and-dump fraud risk.</p>

        <div className="mb-8">
          <StockSearchForm onSubmit={runAnalysis} loading={loading} />
        </div>

        {error && (
          <div className="mb-6 text-red-400 bg-red-950/50 border border-red-800 rounded-xl p-4 text-sm">
            {error}
          </div>
        )}

        {loading && (
          <div className="text-center py-16 text-gray-400">
            <div className="inline-block w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mb-4" />
            <p>Collecting market data and running AI analysis...</p>
          </div>
        )}

        {analysis && !loading && (
          <div className="space-y-6">
            <RiskScoreCard analysis={analysis} />
            <IndicatorBreakdown indicators={analysis.indicators} />
          </div>
        )}
      </main>
    </>
  );
}

export default function AnalyzePage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center text-gray-400">Loading...</div>}>
      <AnalyzeContent />
    </Suspense>
  );
}
