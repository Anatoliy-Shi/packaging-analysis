import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from "recharts";

// Цвета для смен — на случай, если смен больше 4
const SHIFT_COLORS = [
    "#38bdf8",  // 1 — голубой
    "#f87171",  // 2 — красный
    "#4ade80",  // 3 — зелёный
    "#a78bfa",  // 4 — фиолетовый
    "#fbbf24",  // 5 — жёлтый
    "#f472b6",  // 6 — розовый
    "#34d399",  // 7 — изумрудный
    "#60a5fa",  // 8 — синий
];

function colorForShift(shiftNum) {
    return SHIFT_COLORS[(shiftNum - 1) % SHIFT_COLORS.length];
}

function labelForShift(shiftNum) {
    return `Смена ${shiftNum}`;
}

export default function StackedByMonthShift({ data }) {
    if (!data || data.length === 0) {
        return (
            <div className="flex h-full items-center justify-center text-slate-400">
                Нет данных
            </div>
        );
    }

    // 1. Собираем уникальные номера смен из данных
    const shiftNumbers = new Set();
    for (const m of data) {
        for (const s of m.shifts) {
            shiftNumbers.add(s.shift);
        }
    }
    const shifts = [...shiftNumbers].sort((a, b) => a - b);

    // 2. Готовим данные для Recharts + ищем топ-смену в каждом месяце
    const chartData = data.map((m) => {
        const row = { name: m.label, topShift: null, total: 0 };
        let topTons = -1;

        for (const s of m.shifts) {
            row[`shift${s.shift}`] = s.tons;
            row.total += s.tons;
            if (s.tons > topTons) {
                topTons = s.tons;
                row.topShift = s.shift;
            }
        }
        return row;
    });

    return (
        <ResponsiveContainer width="100%" height="100%">
            <BarChart
                data={chartData}
                margin={{ top: 20, right: 20, bottom: 5, left: 0 }}
            >
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" />
                <YAxis stroke="#64748b" />

                <Tooltip content={<CustomTooltip />}
                         cursor={{ fill: "rgba(148, 163, 184, 0.12)" }}
                />
                <Legend
                    formatter={(value) => labelForShift(Number(value.replace("shift", "")))}
                />

                {/* Динамически рисуем столбик для каждой смены */}
                {shifts.map((shiftNum) => (
                    <Bar
                        key={`shift${shiftNum}`}
                        dataKey={`shift${shiftNum}`}
                        stackId="a"
                        fill={colorForShift(shiftNum)}
                        name={`shift${shiftNum}`}
                        radius={shiftNum === shifts[shifts.length - 1] ? [6, 6, 0, 0] : 0}
                    />
                ))}
            </BarChart>
        </ResponsiveContainer>
    );
}

/**
 * Tooltip: топ-смена месяца сверху с 🏆, остальные — ниже.
 * Показывает все смены, которые есть в данных.
 */
function CustomTooltip({ active, payload, label }) {
    if (!active || !payload?.length) return null;

    const row = payload[0].payload;
    const topShift = row.topShift;

    const shifts = payload
        .map((entry) => ({
            key: entry.name,
            shiftNum: Number(entry.name.replace("shift", "")),
            label: labelForShift(Number(entry.name.replace("shift", ""))),
            value: entry.value,
            color: entry.color,
        }))
        .sort((a, b) => b.value - a.value);

    return (
        <div className="rounded-lg border border-slate-200 bg-white p-3 shadow-md">
            <div className="mb-2 border-b border-slate-100 pb-1 text-sm font-semibold text-slate-800">
                {label}
            </div>

            <div className="space-y-1">
                {shifts.map((s) => {
                    const isTop = s.shiftNum === topShift;
                    return (
                        <div
                            key={s.key}
                            className={
                                isTop
                                    ? "flex items-center justify-between gap-4 text-sm font-bold text-slate-900"
                                    : "flex items-center justify-between gap-4 text-sm text-slate-600"
                            }
                        >
              <span className="flex items-center gap-2">
                <span
                    className="inline-block h-2 w-2 rounded-full"
                    style={{ background: s.color }}
                />
                  {s.label}
                  {isTop && <span>🏆</span>}
              </span>
                            <span>{s.value.toFixed(1)} т</span>
                        </div>
                    );
                })}
            </div>

            <div className="mt-2 flex items-center justify-between border-t border-slate-100 pt-2 text-sm text-slate-500">
                <span>Всего за месяц</span>
                <span className="font-medium text-slate-700">
          {row.total.toFixed(1)} т
        </span>
            </div>
        </div>
    );
}