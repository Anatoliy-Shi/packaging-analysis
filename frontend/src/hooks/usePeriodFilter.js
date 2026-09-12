import { useMemo } from "react";

/**
 * Фильтрует by_month по пресету периода.
 * Возвращает отфильтрованный массив + границы.
 */
export function usePeriodFilter(months, preset = "all", custom = null) {
    return useMemo(() => {
        if (!months || months.length === 0) {
            return { filtered: [], range: null };
        }

        const sorted = [...months].sort(
            (a, b) => a.year * 12 + a.month - (b.year * 12 + b.month)
        );

        const lastIdx = sorted.length - 1;
        let fromIdx = 0;
        let toIdx = lastIdx;

        switch (preset) {
            case "last3":
                fromIdx = Math.max(0, lastIdx - 2);
                break;
            case "last6":
                fromIdx = Math.max(0, lastIdx - 5);
                break;
            case "ytd": {
                const lastYear = sorted[lastIdx].year;
                const yStart = sorted.findIndex((m) => m.year === lastYear);
                fromIdx = yStart >= 0 ? yStart : 0;
                break;
            }
            case "custom": {
                if (!custom?.from || !custom?.to) break;
                const i1 = sorted.findIndex(
                    (m) => m.year === custom.from.year && m.month === custom.from.month
                );
                const i2 = sorted.findIndex(
                    (m) => m.year === custom.to.year && m.month === custom.to.month
                );
                if (i1 >= 0 && i2 >= 0 && i1 <= i2) {
                    fromIdx = i1;
                    toIdx = i2;
                }
                break;
            }
            default:
                break;
        }

        const filtered = sorted.slice(fromIdx, toIdx + 1);
        const range = filtered.length
            ? { from: filtered[0], to: filtered[filtered.length - 1] }
            : null;

        return { filtered, range };
    }, [months, preset, custom]);
}