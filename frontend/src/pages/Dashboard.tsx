import { useQuery } from "@tanstack/react-query";
import { listRuns } from "../api/client";
import GoalForm from "../components/GoalForm";
import RunCard from "../components/RunCard";

export default function Dashboard() {
  const { data: runs, isLoading } = useQuery({
    queryKey: ["runs"],
    queryFn: () => listRuns(),
    refetchInterval: 3000,
  });

  return (
    <div className="space-y-8">
      <GoalForm />

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
