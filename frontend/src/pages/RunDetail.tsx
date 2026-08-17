import { useParams, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getRun, cancelRun } from "../api/client";
import StatusBadge from "../components/StatusBadge";
import StepTimeline from "../components/StepTimeline";
import { formatCost, formatTokens } from "../lib/cost";

export default function RunDetail() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();

  const { data: run, isLoading } = useQuery({
    queryKey: ["run", id],
    queryFn: () => getRun(id!),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "running" || status === "planning" || status === "pending" ? 2000 : false;
    },
  });

  const cancel = useMutation({
    mutationFn: () => cancelRun(id!),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["run", id] }),
  });

  if (isLoading) return <p className="text-sm text-gray-500">Loading...</p>;
  if (!run) return <p className="text-sm text-red-400">Run not found.</p>;

  const isActive = ["pending", "planning", "running"].includes(run.status);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/" className="text-sm text-gray-500 hover:text-gray-300">&larr; Back</Link>
      </div>

      <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-lg font-semibold text-white">{run.goal}</h1>
            <p className="mt-1 text-sm text-gray-500">
              {run.model_provider}/{run.model_name} &middot; {new Date(run.created_at).toLocaleString()}
            </p>
          </div>
          <div className="flex items-center gap-3">
            {run.tokens > 0 && (
              <div className="text-right">
                <p className="font-mono text-sm font-semibold text-emerald-400">{formatCost(run.cost_usd)}</p>
                <p className="text-xs text-gray-500">{formatTokens(run.tokens)} tokens</p>
              </div>
            )}
            <StatusBadge status={run.status} />
            {isActive && (
              <button
                onClick={() => cancel.mutate()}
                className="rounded-lg border border-red-800 px-3 py-1 text-xs text-red-400 hover:bg-red-950 transition-colors"
              >
                Cancel
              </button>
            )}
          </div>
        </div>
        {run.error && (
          <p className="mt-3 text-sm text-red-400">{run.error}</p>
        )}
      </div>

      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">Steps</h2>
          <Link
            to={`/runs/${run.id}/traces`}
            className="text-sm text-blue-400 hover:text-blue-300"
          >
            View Traces &rarr;
          </Link>
        </div>
        <StepTimeline steps={run.steps} />
      </section>
    </div>
  );
}
