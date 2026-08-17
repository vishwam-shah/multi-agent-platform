import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { listTraces, getRun } from "../api/client";
import TracePanel from "../components/TracePanel";

export default function TraceView() {
  const { id } = useParams<{ id: string }>();

  const { data: run } = useQuery({
    queryKey: ["run", id],
    queryFn: () => getRun(id!),
  });

  const { data: traces, isLoading } = useQuery({
    queryKey: ["traces", id],
    queryFn: () => listTraces(id!),
    refetchInterval: (query) => {
      const status = run?.status;
      return status === "running" || status === "planning" ? 3000 : false;
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to={`/runs/${id}`} className="text-sm text-gray-500 hover:text-gray-300">&larr; Back to Run</Link>
      </div>

      <h1 className="text-lg font-semibold text-white">
        Traces {run ? `— ${run.goal.slice(0, 80)}` : ""}
      </h1>

      {traces && (
        <div className="flex gap-4 text-sm text-gray-400">
          <span>{traces.length} events</span>
          <span>
            {traces.reduce((sum, t) => sum + (t.token_usage?.total_tokens ?? 0), 0)} total tokens
          </span>
          <span>
            {traces.reduce((sum, t) => sum + (t.duration_ms ?? 0), 0)}ms total time
          </span>
        </div>
      )}

      {isLoading ? (
        <p className="text-sm text-gray-500">Loading traces...</p>
      ) : (
        <TracePanel traces={traces ?? []} />
      )}
    </div>
  );
}
