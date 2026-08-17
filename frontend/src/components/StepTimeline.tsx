import { useState } from "react";
import type { Step } from "../types";
import StatusBadge from "./StatusBadge";
import { formatCost } from "../lib/cost";

export default function StepTimeline({ steps }: { steps: Step[] }) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  const toggle = (id: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  if (steps.length === 0) {
    return <p className="text-sm text-gray-500">No steps yet...</p>;
  }

  return (
    <div className="space-y-3">
      {steps.map((step) => (
        <div key={step.id} className="rounded-lg border border-gray-800 bg-gray-900">
          <button
            onClick={() => toggle(step.id)}
            className="flex w-full items-center gap-3 px-4 py-3 text-left"
          >
            <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gray-800 text-xs font-bold text-gray-300">
              {step.index + 1}
            </span>
            <span className="flex-1 text-sm text-gray-200 truncate">{step.description}</span>
            {step.tokens > 0 && (
              <span className="text-xs font-mono text-emerald-400">{formatCost(step.cost_usd)}</span>
            )}
            <StatusBadge status={step.status} />
            <span className="text-gray-500 text-xs">{expanded.has(step.id) ? "▲" : "▼"}</span>
          </button>

          {expanded.has(step.id) && (
            <div className="border-t border-gray-800 px-4 py-3 space-y-2 text-xs">
              {step.retries > 0 && (
                <p className="text-yellow-400">Retries: {step.retries}</p>
              )}
              {step.error && (
                <div>
                  <p className="font-medium text-red-400">Error:</p>
                  <pre className="mt-1 whitespace-pre-wrap text-red-300 bg-red-950 rounded p-2">{step.error}</pre>
                </div>
              )}
              {step.output_data && (
                <div>
                  <p className="font-medium text-gray-400">Output:</p>
                  <pre className="mt-1 whitespace-pre-wrap text-gray-300 bg-gray-800 rounded p-2 max-h-64 overflow-auto">
                    {typeof step.output_data === "object"
                      ? JSON.stringify(step.output_data, null, 2)
                      : String(step.output_data)}
                  </pre>
                </div>
              )}
              {step.started_at && (
                <p className="text-gray-500">
                  Started: {new Date(step.started_at).toLocaleString()}
                  {step.completed_at && ` — Completed: ${new Date(step.completed_at).toLocaleString()}`}
                </p>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
