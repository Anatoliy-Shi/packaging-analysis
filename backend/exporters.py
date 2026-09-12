"""Метрики → CSV + JSON."""

import json
from datetime import datetime

import pandas as pd

import config


def save_all(df, volume, downtime, by_month, by_month_shift) -> None:
    """Сохраняет всё: CSV для BI + JSON для фронта."""
    config.OUTPUT_DIR.mkdir(exist_ok=True)

    _save_csv(df, volume, downtime)
    _save_json(df, volume, downtime, by_month, by_month_shift)


# --- CSV ---

def _save_csv(df, volume, downtime):
    df.to_csv(config.OUTPUT_FULL_DATA, index=False, encoding="utf-8-sig")
    volume["by_shift_tons"].to_csv(config.OUTPUT_VOLUME_BY_SHIFT, encoding="utf-8-sig")
    downtime["by_shift_hours"].to_csv(config.OUTPUT_DOWNTIME_BY_SHIFT, encoding="utf-8-sig")
    print(f"✅ CSV → {config.OUTPUT_FULL_DATA.name}")


# --- JSON ---

def _save_json(df, volume, downtime, by_month, by_month_shift):
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "period": _period_info(df),
        "summary": _summary(df, volume, downtime),
        "volume_by_shift": _by_shift(volume["by_shift_tons"], "tons"),
        "downtime_by_shift": _by_shift(downtime["by_shift_hours"], "hours"),
        "combined_by_shift": _combined(volume, downtime),
        "by_month": by_month,
        "by_month_shift": by_month_shift,       # ← НОВОЕ
    }

    text = json.dumps(payload, ensure_ascii=False, indent=2, default=str)

    config.OUTPUT_JSON.write_text(text, encoding="utf-8")
    print(f"✅ JSON → {config.OUTPUT_JSON.relative_to(config.BASE_DIR.parent)}")

    try:
        config.OUTPUT_JSON_FRONTEND.parent.mkdir(parents=True, exist_ok=True)
        config.OUTPUT_JSON_FRONTEND.write_text(text, encoding="utf-8")
        print(f"✅ JSON → {config.OUTPUT_JSON_FRONTEND.relative_to(config.BASE_DIR.parent)}")
    except OSError as e:
        print(f"⚠️  Не удалось записать во фронт: {e}")


# --- Хелперы ---

def _period_info(df):
    if df["Дата"].isna().all():
        return {"from": None, "to": None, "days": 0}
    valid = df["Дата"].dropna()
    return {
        "from": valid.min().date().isoformat(),
        "to": valid.max().date().isoformat(),
        "days": int((valid.max() - valid.min()).days) + 1,
    }


def _summary(df, volume, downtime):
    return {
        "total_kg": round(volume["total_kg"], 0),
        "total_tons": round(volume["total_kg"] / 1000, 1),
        "total_downtime_minutes": round(downtime["total_minutes"], 0),
        "total_downtime_hours": round(downtime["total_hours"], 1),
        "shift_count": int(df["Смена_номер"].nunique()),
        "line_count": int(df["Линия"].nunique()),
        "row_count": int(len(df)),
    }


def _by_shift(series: pd.Series, key: str) -> list[dict]:
    return [
        {"shift": int(s), key: round(float(v), 1)}
        for s, v in series.items()
    ]


def _combined(volume, downtime) -> list[dict]:
    return [
        {
            "shift": int(s),
            "tons": round(float(volume["by_shift_tons"][s]), 1),
            "hours": round(float(downtime["by_shift_hours"][s]), 1),
        }
        for s in volume["by_shift_tons"].index
    ]