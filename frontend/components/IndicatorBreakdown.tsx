import type { IndicatorScore } from "@/lib/api";

interface Props {
  indicators: IndicatorScore[];
}

export default function IndicatorBreakdown({ indicators }: Props) {
  return (
    <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-6">
      <h3 className="text-lg font-semibold mb-4">Risk Indicators</h3>
      <div className="space-y-4">
        {indicators.map((ind) => {
          const pct = ind.max_score > 0 ? (ind.score / ind.max_score) * 100 : 0;
          const barColor = pct >= 70 ? "bg-red-500" : pct >= 40 ? "bg-yellow-500" : "bg-emerald-500";
          return (
            <div key={ind.name}>
              <div className="flex justify-between text-sm mb-1">
                <span className="font-medium">{ind.name}</span>
                <span className="text-gray-400">
                  {ind.score}/{ind.max_score}
                </span>
              </div>
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
              </div>
              <p className="text-xs text-gray-500 mt-1">{ind.detail}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
