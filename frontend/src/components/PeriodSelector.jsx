const PRESETS = [
  { value: "all", label: "Весь период" },
  { value: "ytd", label: "С начала года" },
  { value: "last3", label: "Последние 3 месяца" },
  { value: "last6", label: "Последние 6 месяцев" },
  { value: "custom", label: "Выбрать вручную" },
];

export default function PeriodSelector({
  months,
  preset,
  onPresetChange,
  custom,
  onCustomChange,
}) {
  const sorted = [...(months || [])].sort(
    (a, b) => a.year * 12 + a.month - (b.year * 12 + b.month)
  );

  return (
    <div className="flex flex-wrap items-center gap-3">
      <span className="text-sm text-slate-500">📅 Период:</span>

      <select
        value={preset}
        onChange={(e) => onPresetChange(e.target.value)}
        className="min-w-[200px] cursor-pointer rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800"
      >
        {PRESETS.map((p) => (
          <option key={p.value} value={p.value}>
            {p.label}
          </option>
        ))}
      </select>

      {preset === "custom" && (
        <>
          <select
            value={custom?.from ? `${custom.from.year}-${custom.from.month}` : ""}
            onChange={(e) => {
              const [y, m] = e.target.value.split("-").map(Number);
              onCustomChange({ ...custom, from: { year: y, month: m } });
            }}
            className="min-w-[140px] cursor-pointer rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800"
          >
            <option value="">С:</option>
            {sorted.map((m) => (
              <option key={`f-${m.label}`} value={`${m.year}-${m.month}`}>
                {m.label}
              </option>
            ))}
          </select>

          <select
            value={custom?.to ? `${custom.to.year}-${custom.to.month}` : ""}
            onChange={(e) => {
              const [y, m] = e.target.value.split("-").map(Number);
              onCustomChange({ ...custom, to: { year: y, month: m } });
            }}
            className="min-w-[140px] cursor-pointer rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800"
          >
            <option value="">По:</option>
            {sorted.map((m) => (
              <option key={`t-${m.label}`} value={`${m.year}-${m.month}`}>
                {m.label}
              </option>
            ))}
          </select>
        </>
      )}
    </div>
  );
}