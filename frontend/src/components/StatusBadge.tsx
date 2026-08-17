const STATUS_STYLES: Record<string, string> = {
  pending: "bg-gray-700 text-gray-300",
  planning: "bg-blue-900 text-blue-300 animate-pulse",
  running: "bg-yellow-900 text-yellow-300 animate-pulse",
  completed: "bg-green-900 text-green-300",
  failed: "bg-red-900 text-red-300",
  cancelled: "bg-gray-800 text-gray-400",
};

export default function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-block rounded-full px-3 py-1 text-xs font-medium ${STATUS_STYLES[status] ?? STATUS_STYLES.pending}`}>
      {status}
    </span>
  );
}
