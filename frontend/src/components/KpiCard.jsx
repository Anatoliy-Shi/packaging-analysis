export default function KpiCard({ label, value, unit, accent = "blue" }) {
  const colors = {
    blue: "bg-sky-50 text-sky-700 border-sky-200",
    red: "bg-red-50 text-red-700 border-red-200",
    green: "bg-emerald-50 text-emerald-700 border-emerald-200",
  };

  return (
    <div className={`rounded-xl border p-4 ${colors[accent]}`}>
      <div className="text-sm opacity-70">{label}</div>
      <div className="mt-1 text-2xl font-semibold">
        {value}
        {unit && <span className="ml-1 text-base opacity-70">{unit}</span>}
      </div>
    </div>
  );
}