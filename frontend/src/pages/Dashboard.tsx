import { useQuery } from "@tanstack/react-query";
import { listRuns } from "../api/client";
import GoalForm from "../components/GoalForm";
import RunCard from "../components/RunCard";
import { formatCost, formatTokens } from "../lib/cost";

export default function Dashboard() {
  const { data: runs, isLoading } = useQuery({
    queryKey: ["runs"],
    queryFn: () => listRuns(),
    refetchInterval: 3000,
  });

  const totalCost = runs?.reduce((sum, r) => sum + r.cost_usd, 0) ?? 0;
  const totalTokens = runs?.reduce((sum, r) => sum + r.tokens, 0) ?? 0;

  return (
    <div className="space-y-8">
      <GoalForm />

      {!isLoading && !!runs?.length && (
        <div className="flex items-center gap-6 rounded-xl border border-gray-800 bg-gray-900 px-5 py-4">
          <div>
            <p className="text-xs text-gray-500">Total spend (last {runs.length})</p>
            <p className="text-xl font-semibold text-emerald-400 font-mono">{formatCost(totalCost)}</p>
          </div>
          <div className="h-8 w-px bg-gray-800" />
          <div>
            <p className="text-xs text-gray-500">Total tokens</p>
            <p className="text-xl font-semibold text-gray-200 font-mono">{formatTokens(totalTokens)}</p>
          </div>
        </div>
      )}

      <section>
        <h2 className="mb-4 text-lg font-semibold text-white">Recent Runs</h2>
        {isLoading ? (
          <p className="text-sm text-gray-500">Loading...</p>
        ) : !runs?.length ? (
          <p className="text-sm text-gray-500">No runs yet. Submit a goal above to get started.</p>
        ) : (
          <div className="space-y-3">
            {runs.map((run) => (
              <RunCard key={run.id} run={run} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
