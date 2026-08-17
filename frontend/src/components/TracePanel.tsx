import { useState } from "react";
import type { Trace } from "../types";
import { formatCost } from "../lib/cost";

const EVENT_COLORS: Record<string, string> = {
  llm_call: "text-blue-400",
  tool_call: "text-green-400",
  agent_decision: "text-purple-400",
  error: "text-red-400",
  retry: "text-yellow-400",
};

export default function TracePanel({ traces }: { traces: Trace[] }) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  const toggle = (id: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  if (traces.length === 0) {
    return <p className="text-sm text-gray-500">No traces recorded.</p>;
  }

  return (
    <div className="space-y-2">
      {traces.map((trace) => (
        <div key={trace.id} className="rounded-lg border border-gray-800 bg-gray-900">
          <button
            onClick={() => toggle(trace.id)}
            className="flex w-full items-center gap-3 px-4 py-3 text-left text-sm"
          >
            <span className={`font-mono font-bold ${EVENT_COLORS[trace.event_type] ?? "text-gray-400"}`}>
              {trace.event_type}
            </span>
            {trace.model && <span className="text-gray-500">{trace.model}</span>}
            {trace.duration_ms != null && (
              <span className="text-gray-600">{trace.duration_ms}ms</span>
            )}
            {trace.token_usage?.total_tokens && (
              <span className="text-gray-600">{trace.token_usage.total_tokens} tokens</span>
            )}
            {trace.cost_usd > 0 && (
              <span className="font-mono text-emerald-400">{formatCost(trace.cost_usd)}</span>
            )}
            <span className="ml-auto text-xs text-gray-600">
              {new Date(trace.timestamp).toLocaleTimeString()}
            </span>
            <span className="text-gray-500 text-xs">{expanded.has(trace.id) ? "▲" : "▼"}</span>
          </button>

          {expanded.has(trace.id) && (
            <div className="border-t border-gray-800 px-4 py-3 space-y-3 text-xs">
              {trace.input_data && (
                <div>
                  <p className="font-medium text-gray-400 mb-1">Input:</p>
                  <pre className="whitespace-pre-wrap text-gray-300 bg-gray-800 rounded p-2 max-h-48 overflow-auto">
                    {JSON.stringify(trace.input_data, null, 2)}
                  </pre>
                </div>
              )}
              {trace.output_data && (
                <div>
                  <p className="font-medium text-gray-400 mb-1">Output:</p>
                  <pre className="whitespace-pre-wrap text-gray-300 bg-gray-800 rounded p-2 max-h-48 overflow-auto">
                    {JSON.stringify(trace.output_data, null, 2)}
                  </pre>
                </div>
              )}
              {trace.token_usage && (
                <p className="text-gray-500">
                  Tokens: {trace.token_usage.prompt_tokens ?? 0} in / {trace.token_usage.completion_tokens ?? 0} out / {trace.token_usage.total_tokens ?? 0} total
                </p>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
