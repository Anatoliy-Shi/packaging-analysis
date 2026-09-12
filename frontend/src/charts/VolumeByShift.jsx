import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LabelList,
} from "recharts";

export default function VolumeByShift({ data }) {
  // data: [{ shift: 1, tons: 82.1 }, ...]
  const chartData = data.map((d) => ({
    name: `Смена ${d.shift}`,
    tons: d.tons,
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={chartData} margin={{ top: 20, right: 20, bottom: 5, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
        <XAxis dataKey="name" stroke="#64748b" />
        <YAxis stroke="#64748b" />
        <Tooltip
          formatter={(v) => [`${v.toFixed(1)} т`, "Объём"]}
          contentStyle={{ borderRadius: 8, border: "1px solid #e2e8f0" }}
          cursor={{ fill: "rgba(148, 163, 184, 0.12)" }}
        />
        <Bar dataKey="tons" fill="#38bdf8" radius={[6, 6, 0, 0]}>
          <LabelList
            dataKey="tons"
            position="top"
            formatter={(v) => `${v.toFixed(1)} т`}
            fill="#334155"
            fontSize={12}
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}