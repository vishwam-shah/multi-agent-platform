import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createRun } from "../api/client";

export default function GoalForm() {
  const [goal, setGoal] = useState("");
  const [provider, setProvider] = useState("openai");
  const [model, setModel] = useState("gpt-4o");
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: createRun,
    onSuccess: () => {
      setGoal("");
      queryClient.invalidateQueries({ queryKey: ["runs"] });
    },
  });

  const providerModels: Record<string, string[]> = {
    openai: ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
    anthropic: ["claude-sonnet-4-20250514", "claude-haiku-4-20250414"],
  };

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!goal.trim()) return;
        mutation.mutate({ goal, model_provider: provider, model_name: model });
      }}
      className="rounded-xl border border-gray-800 bg-gray-900 p-6 space-y-4"
    >
      <h2 className="text-lg font-semibold text-white">New Workflow Run</h2>
      <textarea
        value={goal}
        onChange={(e) => setGoal(e.target.value)}
        placeholder="Describe your goal... (e.g. 'Research the top 3 Python web frameworks and compare them')"
        rows={3}
        className="w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-3 text-sm text-gray-100 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      />
      <div className="flex items-center gap-4">
        <select
          value={provider}
          onChange={(e) => {
            setProvider(e.target.value);
            setModel(providerModels[e.target.value][0]);
          }}
          className="rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 focus:border-blue-500 focus:outline-none"
        >
          <option value="openai">OpenAI</option>
          <option value="anthropic">Anthropic</option>
        </select>
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 focus:border-blue-500 focus:outline-none"
        >
          {providerModels[provider].map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
        <button
          type="submit"
          disabled={mutation.isPending || !goal.trim()}
          className="ml-auto rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {mutation.isPending ? "Starting..." : "Start Run"}
        </button>
      </div>
      {mutation.isError && (
        <p className="text-sm text-red-400">Failed to start run. Check your API keys and try again.</p>
      )}
    </form>
  );
}
