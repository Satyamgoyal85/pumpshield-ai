import type { Analysis } from "@/lib/api";

interface Props {
  analysis: Analysis;
}

export default function RiskScoreCard({ analysis }: Props) {
  const isRed = analysis.risk_level === "red";

  return (
    <div className={`rounded-2xl border-2 p-8 ${isRed ? "border-red-500/50 bg-red-950/30" : "border-emerald-500/50 bg-emerald-950/30"}`}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">{analysis.stock_symbol}</h2>
          <p className="text-gray-400 text-sm">Fraud Risk Analysis</p>
        </div>
        <div className="text-right">
          <div className={`text-5xl font-black ${isRed ? "text-red-400" : "text-emerald-400"}`}>
            {analysis.risk_score}
          </div>
          <span
            className={`inline-block mt-1 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
              isRed ? "bg-red-500/20 text-red-300" : "bg-emerald-500/20 text-emerald-300"
            }`}
          >
            {isRed ? "Red — High Risk" : "Green — Low Risk"}
          </span>
        </div>
      </div>

      <div className="bg-gray-900/60 rounded-xl p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-3">AI Explanation</h3>
        <p className="text-gray-200 whitespace-pre-line leading-relaxed text-sm">{analysis.explanation}</p>
      </div>
    </div>
  );
}
