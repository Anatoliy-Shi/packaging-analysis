"""Генератор синтетического analytics.json для публичного демо.

Все данные ВЫДУМАННЫЕ. Структура JSON совпадает с реальной,
поэтому фронт работает без изменений.

Запуск:
    python scripts/make_demo_data.py
"""

import json
import random
from datetime import datetime
from pathlib import Path


# Детерминированный seed — при каждом запуске одинаковые данные
random.seed(42)

# Пути
ROOT = Path(__file__).parent.parent.parent
OUTPUTS = [
    ROOT / "frontend" / "public" / "data" / "analytics.json",
    ROOT / "frontend" / "dist" / "data" / "analytics.json",
]


# ─── ПАРАМЕТРЫ ДЕМО (специально НЕ совпадают с реальностью) ─────────
DEMO_YEAR = 2024
DEMO_MONTHS = ["Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен"]
SHIFT_COUNT = 5
LINE_COUNT = 5
TOTAL_SCALE = 0.25


SHIFT_PROFILES = {
    1: {"tons": (30, 60), "hours": (3, 8)},
    2: {"tons": (25, 55), "hours": (12, 25)},   # проблемная
    3: {"tons": (40, 75), "hours": (2, 6)},     # лучшая
    4: {"tons": (30, 65), "hours": (4, 10)},
    5: {"tons": (20, 50), "hours": (6, 14)},    # пятая — нетипичная
}


def generate_month(month_idx: int, month_name: str):
    shifts = []
    for shift_num in range(1, SHIFT_COUNT + 1):
        profile = SHIFT_PROFILES[shift_num]
        s_tons = round(random.uniform(*profile["tons"]) * TOTAL_SCALE * 4, 1)
        s_hours = round(random.uniform(*profile["hours"]) * TOTAL_SCALE * 4, 1)
        shifts.append({"shift": shift_num, "tons": s_tons, "hours": s_hours})

    total_tons = round(sum(s["tons"] for s in shifts), 1)
    total_hours = round(sum(s["hours"] for s in shifts), 1)

    by_month = {
        "year": DEMO_YEAR,
        "month": month_idx + 3,
        "label": f"{month_name} {DEMO_YEAR}",
        "tons": total_tons,
        "hours": total_hours,
    }
    by_month_shift = {
        "year": DEMO_YEAR,
        "month": month_idx + 3,
        "label": f"{month_name} {DEMO_YEAR}",
        "shifts": shifts,
    }
    return by_month, by_month_shift


def build_payload() -> dict:
    by_month = []
    by_month_shift = []
    for i, name in enumerate(DEMO_MONTHS):
        m, ms = generate_month(i, name)
        by_month.append(m)
        by_month_shift.append(ms)

    volume_by_shift = [
        {
            "shift": s,
            "tons": round(sum(
                sh["tons"] for m in by_month_shift
                for sh in m["shifts"] if sh["shift"] == s
            ), 1),
        }
        for s in range(1, SHIFT_COUNT + 1)
    ]
    downtime_by_shift = [
        {
            "shift": s,
            "hours": round(sum(
                sh["hours"] for m in by_month_shift
                for sh in m["shifts"] if sh["shift"] == s
            ), 1),
        }
        for s in range(1, SHIFT_COUNT + 1)
    ]
    combined_by_shift = [
        {
            "shift": s,
            "tons": volume_by_shift[s - 1]["tons"],
            "hours": downtime_by_shift[s - 1]["hours"],
        }
        for s in range(1, SHIFT_COUNT + 1)
    ]

    total_tons = round(sum(m["tons"] for m in by_month), 1)
    total_hours = round(sum(m["hours"] for m in by_month), 1)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "period": {
            "from": f"{DEMO_YEAR}-03-01",
            "to": f"{DEMO_YEAR}-09-30",
            "days": 214,
        },
        "summary": {
            "total_kg": round(total_tons * 1000, 0),
            "total_tons": total_tons,
            "total_downtime_minutes": round(total_hours * 60, 0),
            "total_downtime_hours": total_hours,
            "shift_count": SHIFT_COUNT,
            "line_count": LINE_COUNT,
            "row_count": random.randint(800, 1500),
        },
        "volume_by_shift": volume_by_shift,
        "downtime_by_shift": downtime_by_shift,
        "combined_by_shift": combined_by_shift,
        "by_month": by_month,
        "by_month_shift": by_month_shift,
        "_demo": True,
        "_note": "Синтетические данные. Не связаны с реальным производством.",
    }


def main():
    payload = build_payload()
    text = json.dumps(payload, ensure_ascii=False, indent=2)

    for path in OUTPUTS:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"✅ {path.relative_to(ROOT)}")

    print("\n🎉 Синтетический датасет готов")
    print(f"   Период: {DEMO_YEAR}-03 → {DEMO_YEAR}-09 ({len(DEMO_MONTHS)} мес.)")
    print(f"   Смен: {SHIFT_COUNT}, линий: {LINE_COUNT}")
    print(f"   Всего: {payload['summary']['total_tons']} т")
    print(f"   Простой: {payload['summary']['total_downtime_hours']} ч")
    print("\n⚠️  Это ДЕМО. Реальные данные не использовались.")


if __name__ == "__main__":
    main()