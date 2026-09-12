import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function MonthlyTrend({ data, range }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-slate-400">
        Нет данных
      </div>
    );
  }

  const chartData = data.map((m) => {
    const inRange =
      !range ||
      (m.year * 12 + m.month >= range.from.year * 12 + range.from.month &&
        m.year * 12 + m.month <= range.to.year * 12 + range.to.month);

    return {
      name: m.label,
      tons: m.tons,
      hours: m.hours,
      inRange,
    };
  });

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart
        data={chartData}
        margin={{ top: 20, right: 30, bottom: 5, left: 0 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="name" stroke="#64748b" />
        <YAxis
          yAxisId="left"
          stroke="#38bdf8"
          label={{
            value: "Тонны",
            angle: -90,
            position: "insideLeft",
            fill: "#38bdf8",
            fontSize: 12,
          }}
        />
        <YAxis
          yAxisId="right"
          orientation="right"
          stroke="#f87171"
          label={{
            value: "Часы",
            angle: 90,
            position: "insideRight",
            fill: "#f87171",
            fontSize: 12,
          }}
        />
        <Tooltip
          contentStyle={{ borderRadius: 8, border: "1px solid #e2e8f0" }}
          formatter={(value, name) =>
            name === "tons"
              ? [`${value} т`, "Объём"]
              : [`${value} ч`, "Простой"]
          }
          cursor={{ stroke: "#94a3b8", strokeWidth: 1, strokeDasharray: "4 4" }}
        />
        <Legend
          formatter={(v) => (v === "tons" ? "Объём, т" : "Простой, ч")}
        />
        <Line
          yAxisId="left"
          type="monotone"
          dataKey="tons"
          stroke="#38bdf8"
          strokeWidth={3}
          dot={(props) => {
            const { cx, cy, payload, key } = props;
            return (
              <circle
                key={key}
                cx={cx}
                cy={cy}
                r={payload.inRange ? 6 : 4}
                fill={payload.inRange ? "#38bdf8" : "#cbd5e1"}
                stroke="white"
                strokeWidth={2}
              />
            );
          }}
        />
        <Line
          yAxisId="right"
          type="monotone"
          dataKey="hours"
          stroke="#f87171"
          strokeWidth={3}
          dot={(props) => {
            const { cx, cy, payload, key } = props;
            return (
              <circle
                key={key}
                cx={cx}
                cy={cy}
                r={payload.inRange ? 6 : 4}
                fill={payload.inRange ? "#f87171" : "#cbd5e1"}
                stroke="white"
                strokeWidth={2}
              />
            );
          }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}