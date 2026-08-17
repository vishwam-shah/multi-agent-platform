import { Link } from "react-router-dom";
import type { Run } from "../types";
import StatusBadge from "./StatusBadge";
import { formatCost, formatTokens } from "../lib/cost";

export default function RunCard({ run }: { run: Run }) {
  const time = new Date(run.created_at).toLocaleString();

  return (
    <Link
      to={`/runs/${run.id}`}
      className="block rounded-xl border border-gray-800 bg-gray-900 p-5 hover:border-gray-600 transition-colors"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-white truncate">{run.goal}</p>
          <p className="mt-1 text-xs text-gray-500">
            {run.model_provider}/{run.model_name} &middot; {time}
          </p>
          {run.error && (
            <p className="mt-2 text-xs text-red-400 truncate">{run.error}</p>
          )}
        </div>
        <div className="flex shrink-0 flex-col items-end gap-1.5">
          <StatusBadge status={run.status} />
          {run.tokens > 0 && (
            <span className="text-xs font-mono text-emerald-400" title={`${formatTokens(run.tokens)} tokens`}>
              {formatCost(run.cost_usd)}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
