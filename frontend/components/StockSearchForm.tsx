"use client";

import { FormEvent, useState } from "react";

interface Props {
  onSubmit: (symbol: string) => void;
  loading?: boolean;
}

export default function StockSearchForm({ onSubmit, loading }: Props) {
  const [symbol, setSymbol] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (symbol.trim()) onSubmit(symbol.trim());
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-3">
      <input
        type="text"
        value={symbol}
        onChange={(e) => setSymbol(e.target.value.toUpperCase())}
        placeholder="Enter stock symbol (e.g. AAPL)"
        className="flex-1 px-4 py-3 rounded-xl bg-gray-900 border border-gray-700 focus:border-emerald-500 focus:outline-none text-white placeholder-gray-500"
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading || !symbol.trim()}
        className="px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed font-semibold text-white transition"
      >
        {loading ? "Analyzing..." : "Analyze"}
      </button>
    </form>
  );
}
