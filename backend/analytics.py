"""DataFrame → метрики (объём, простой)."""

import random

import pandas as pd

import config

def analyze_by_month_shift(df: pd.DataFrame, coefficient=None) -> list[dict]:
    """Матрица: месяц × смена. Для stacked/grouped графиков."""
    coeff = _resolve_coeff(coefficient)

    grouped = (
        df.groupby(["Год", "Месяц", "Месяц_имя", "Смена_номер"])
        .agg(
            kg=("УПАКОВАНО_КГ", "sum"),
            minutes=("Простой_минуты", "sum"),
        )
        .reset_index()
        .sort_values(["Год", "Месяц", "Смена_номер"])
    )

    result = []
    for (year, month, label), chunk in grouped.groupby(
        ["Год", "Месяц", "Месяц_имя"], sort=True
    ):
        result.append({
            "year": int(year),
            "month": int(month),
            "label": f"{label} {int(year)}",
            "shifts": [
                {
                    "shift": int(r["Смена_номер"]),
                    "tons": round(r["kg"] * coeff / 1000, 1),
                    "hours": round(r["minutes"] / 60, 1),
                }
                for _, r in chunk.iterrows()
            ],
        })

    return result


def analyze_volume(df: pd.DataFrame, coefficient=None) -> dict:
    """Объём продукции. Маскируется коэффициентом."""
    coeff = _resolve_coeff(coefficient)

    return {
        "total_kg": float(df["УПАКОВАНО_КГ"].sum() * coeff),
        "by_shift_tons": (
            df.groupby("Смена_номер")["УПАКОВАНО_КГ"].sum().sort_index() * coeff / 1000
        ),
    }


def analyze_downtime(df: pd.DataFrame) -> dict:
    """Простои. Не маскируются — они в минутах/часах."""
    total_min = float(df["Простой_минуты"].sum())
    return {
        "total_minutes": total_min,
        "total_hours": total_min / 60,
        "by_shift_hours": (
            df.groupby("Смена_номер")["Простой_минуты"].sum().sort_index() / 60
        ),
    }


def analyze_by_month(df: pd.DataFrame, coefficient=None) -> list[dict]:
    """Объём + простой по месяцам. Для дашборда с динамикой."""
    coeff = _resolve_coeff(coefficient)

    grouped = df.groupby(["Год", "Месяц", "Месяц_имя"]).agg(
        kg=("УПАКОВАНО_КГ", "sum"),
        minutes=("Простой_минуты", "sum"),
    ).reset_index().sort_values(["Год", "Месяц"])

    return [
        {
            "year": int(r["Год"]),
            "month": int(r["Месяц"]),
            "label": f"{r['Месяц_имя']} {int(r['Год'])}",
            "tons": round(r["kg"] * coeff / 1000, 1),
            "hours": round(r["minutes"] / 60, 1),
        }
        for _, r in grouped.iterrows()
    ]


# --- Внутреннее ---

def _resolve_coeff(explicit=None) -> float:
    if explicit is not None:
        return explicit
    if not config.ANONYMIZE:
        return 1.0
    rng = random.Random(config.ANONYMIZE_SEED)
    return rng.uniform(*config.ANONYMIZE_RANGE)