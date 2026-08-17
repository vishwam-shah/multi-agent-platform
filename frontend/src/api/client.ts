import axios from "axios";
import type { Run, RunDetail, Step, Trace } from "../types";

const api = axios.create({ baseURL: "/api" });

export async function createRun(data: {
  goal: string;
  model_provider?: string;
  model_name?: string;
}): Promise<Run> {
  const res = await api.post("/runs", data);
  return res.data;
}

export async function listRuns(limit = 20, offset = 0): Promise<Run[]> {
  const res = await api.get("/runs", { params: { limit, offset } });
  return res.data;
}

export async function getRun(runId: string): Promise<RunDetail> {
  const res = await api.get(`/runs/${runId}`);
  return res.data;
}

export async function cancelRun(runId: string): Promise<void> {
  await api.delete(`/runs/${runId}`);
}

export async function listSteps(runId: string): Promise<Step[]> {
  const res = await api.get(`/runs/${runId}/steps`);
  return res.data;
}

export async function listTraces(runId: string): Promise<Trace[]> {
  const res = await api.get(`/runs/${runId}/traces`);
  return res.data;
}

export async function listStepTraces(runId: string, stepId: string): Promise<Trace[]> {
  const res = await api.get(`/runs/${runId}/steps/${stepId}/traces`);
  return res.data;
}
