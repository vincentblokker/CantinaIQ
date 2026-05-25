import { Recommendation } from "../lib/data";

const STYLES: Record<Recommendation, string> = {
  "Premium Brand Builder": "bg-purple-50 text-purple-800 border-purple-200",
  Target: "bg-blue-50 text-blue-800 border-blue-200",
  "Value Opportunity": "bg-green-50 text-green-800 border-green-200",
  Monitor: "bg-stone-50 text-stone-700 border-stone-200",
  "Avoid for Now": "bg-rose-50 text-rose-800 border-rose-200",
};

export default function RecommendationPill({ value }: { value: Recommendation }) {
  return (
    <span
      className={`inline-block px-2 py-0.5 text-xs rounded-full border ${
        STYLES[value] ?? STYLES.Monitor
      }`}
    >
      {value}
    </span>
  );
}
