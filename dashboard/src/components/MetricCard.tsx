interface Props {
  label: string;
  value: string | number;
  hint?: string;
}

export default function MetricCard({ label, value, hint }: Props) {
  return (
    <div className="rounded-lg border border-stone-200 bg-white px-5 py-4">
      <div className="text-xs uppercase tracking-wide text-ink-2">{label}</div>
      <div className="mt-1 font-serif text-3xl text-ink">{value}</div>
      {hint && <div className="mt-1 text-xs text-ink-2">{hint}</div>}
    </div>
  );
}
