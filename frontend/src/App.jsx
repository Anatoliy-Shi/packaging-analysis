import { useState } from "react";

import ChartCard from "./components/ChartCard";
import KpiCard from "./components/KpiCard";
import PeriodSelector from "./components/PeriodSelector";
import DowntimeByShift from "./charts/DowntimeByShift";
import MonthlyTrend from "./charts/MonthlyTrend";
import StackedByMonthShift from "./charts/StackedByMonthShift";
import VolumeByShift from "./charts/VolumeByShift";
import { useAnalytics } from "./hooks/useAnalytics";
import { usePeriodFilter } from "./hooks/usePeriodFilter";

export default function App() {
    const { data, loading, error } = useAnalytics();

    const [preset, setPreset] = useState("all");
    const [custom, setCustom] = useState({ from: null, to: null });

    const months = data?.by_month ?? [];
    const { filtered, range } = usePeriodFilter(months, preset, custom);

    if (loading) return <div className="p-8 text-slate-500">Загрузка…</div>;
    if (error)
        return <div className="p-8 text-red-600">Ошибка: {error.message}</div>;
    if (!data) return <div className="p-8 text-slate-500">Нет данных</div>;

    const {
        summary,
        period,
        generated_at,
        volume_by_shift,
        downtime_by_shift,
        by_month_shift,
    } = data;

    // Фильтруем by_month_shift под выбранный период
    const filteredMonthShift = (by_month_shift || []).filter((ms) =>
        filtered.some((m) => m.year === ms.year && m.month === ms.month)
    );

    return (
        <div className="min-h-screen bg-slate-50 p-2 sm:p-4 lg:p-8">
            <div className="mx-auto max-w-6xl">
                <header className="mb-6">
                    <h1 className="text-3xl font-bold text-slate-900">
                        📦 Аналитика упаковки
                    </h1>
                    <p className="mt-1 text-slate-500">
                        Объёмы и простои по сменам и месяцам
                    </p>
                </header>

                {/* Панель: инфо о данных + селектор периода */}
                <div className="mb-6 flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-200 bg-white p-4">
                    <div className="text-sm text-slate-600">
                        📁 Данные за <b>{period.from}</b> → <b>{period.to}</b>
                        <span className="ml-2 text-slate-400">
              ({period.days} дней)
            </span>
                        <span className="ml-4 text-xs text-slate-400">
              Обновлено: {new Date(generated_at).toLocaleString("ru-RU")}
            </span>
                    </div>

                    <PeriodSelector
                        months={months}
                        preset={preset}
                        onPresetChange={setPreset}
                        custom={custom}
                        onCustomChange={setCustom}
                    />
                </div>

                {/* KPI */}
                <section className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    <KpiCard
                        label="Общий объём"
                        value={summary.total_tons.toLocaleString("ru-RU")}
                        unit="т"
                        accent="blue"
                    />
                    <KpiCard
                        label="Общий простой"
                        value={summary.total_downtime_hours.toFixed(1)}
                        unit="ч"
                        accent="red"
                    />
                    <KpiCard
                        label="Показано месяцев"
                        value={filtered.length}
                        unit={`из ${months.length}`}
                        accent="green"
                    />
                    <KpiCard
                        label="Смен / линий"
                        value={`${summary.shift_count} / ${summary.line_count}`}
                        accent="blue"
                    />
                </section>

                {/* Динамика по месяцам */}
                <section className="mb-6 hidden lg:block">
                    <ChartCard
                        title="Динамика по месяцам"
                        subtitle={
                            range
                                ? `Показано: ${range.from.label} → ${range.to.label}`
                                : "Весь доступный период"
                        }
                        height={340}
                    >
                        <MonthlyTrend data={months} range={range} />
                    </ChartCard>
                </section>

                {/* Stacked: месяц × смена */}
                <section className="mb-6">
                    <ChartCard
                        title="Объём по месяцам и сменам"
                        subtitle="Вклад каждой смены в общий объём месяца"
                        height={340}
                    >
                        <StackedByMonthShift data={filteredMonthShift} />
                    </ChartCard>
                </section>

                {/* Смены — сравнение */}
                <section className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                    <ChartCard title="Объём по сменам" subtitle="Упаковано, тонны">
                        <VolumeByShift data={volume_by_shift} />
                    </ChartCard>

                    <ChartCard
                        title="Простой по сменам"
                        subtitle="Суммарное время простоя, часы"
                    >
                        <DowntimeByShift data={downtime_by_shift} />
                    </ChartCard>
                </section>
            </div>
        </div>
    );
}