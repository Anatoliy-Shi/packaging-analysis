"""Excel → очищенный DataFrame с датами."""

import pandas as pd
from openpyxl import load_workbook

import config


def load_dataframe() -> pd.DataFrame:
    """Загружает Excel и возвращает очищенный DataFrame."""
    rows = _read_sheet()
    print(f"📄 Всего строк в файле: {len(rows)}")

    header = _find_header(rows)
    print(f"✅ Шапка на строке {header}")

    records = _parse_rows(rows[header + 1:])
    df = _clean(pd.DataFrame(records))
    print(f"📊 Строк после очистки: {len(df)}")
    return df


# --- Внутреннее ---

def _read_sheet():
    wb = load_workbook(config.INPUT_FILE, data_only=True)
    return list(wb[config.SHEET_NAME].iter_rows(values_only=True))


def _find_header(rows):
    for i, row in enumerate(rows):
        if len(row) > config.WEIGHT_COL and row[config.WEIGHT_COL]:
            if config.HEADER_MARKER in str(row[config.WEIGHT_COL]):
                return i
    raise RuntimeError("Шапка не найдена")


def _get(row, idx):
    return row[idx] if len(row) > idx else None


def _parse_rows(rows):
    records, current_shift = [], None

    for row in rows:
        if not row or all(c is None for c in row):
            continue

        weight = _parse_weight(row)
        if weight is None:
            continue

        current_shift = _update_shift(row, current_shift)
        records.append({
            "Дата": _parse_date(row),
            "Смена": current_shift,
            "Линия": _parse_line(row),
            "УПАКОВАНО_КГ": weight,
            "Простой_минуты": _parse_downtime(row),
            "Проблема": _get(row, config.PROBLEM_COL),
            "Комментарий": _get(row, config.COMMENT_COL),
        })

    return records


def _parse_weight(row):
    cell = _get(row, config.WEIGHT_COL)
    if cell is None:
        return None
    if isinstance(cell, str):
        cell = cell.replace(",", ".").replace(" ", "").strip()
        if not cell:
            return None
    try:
        w = float(cell)
        return w if w > 0 else None
    except (TypeError, ValueError):
        return None


def _parse_downtime(row):
    cell = _get(row, config.DOWNTIME_COL)
    if cell is None:
        return 0.0
    text = str(cell).strip()
    if not text or text in {"0", "00:00:00"}:
        return 0.0
    try:
        parts = text.split(":")
        if len(parts) == 3:
            h, m, s = map(float, parts)
            return h * 60 + m + s / 60
        if len(parts) == 2:
            h, m = map(float, parts)
            return h * 60 + m
        if len(parts) == 1:
            return float(text) * 60
    except ValueError:
        pass
    return 0.0


def _parse_line(row):
    val = _get(row, config.LINE_COL)
    if isinstance(val, str):
        val = val.strip()
    try:
        return float(val) if val else None
    except (TypeError, ValueError):
        return None


def _update_shift(row, current):
    val = _get(row, config.SHIFT_COL)
    if val is None:
        return current
    text = str(val).strip()
    return text if text else current


def _parse_date(row):
    """Дата → pandas.Timestamp. Поддерживает datetime, строку, Excel-число."""
    cell = _get(row, config.DATE_COL)
    if cell is None:
        return pd.NaT

    if isinstance(cell, pd.Timestamp):
        return cell
    if hasattr(cell, "year"):
        return pd.Timestamp(cell)

    text = str(cell).strip()
    if not text:
        return pd.NaT

    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return pd.to_datetime(text, format=fmt)
        except (ValueError, TypeError):
            continue

    try:
        return pd.to_datetime(text, dayfirst=True)
    except (ValueError, TypeError):
        return pd.NaT


def _clean(df):
    df = df.dropna(subset=["Смена"]).copy()
    df["Смена_номер"] = df["Смена"].replace(config.SHIFT_MAP)
    df = df.dropna(subset=["Смена_номер"])
    df["Линия"] = df["Линия"].fillna(0).astype(int)

    df["Дата"] = pd.to_datetime(df["Дата"], errors="coerce")
    df["Год"] = df["Дата"].dt.year
    df["Месяц"] = df["Дата"].dt.month
    MONTHS_RU_SHORT = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн",
                       "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]

    df["Месяц_имя"] = df["Дата"].dt.month.apply(
        lambda m: MONTHS_RU_SHORT[int(m) - 1] if pd.notna(m) else ""
    )
    return df


# --- Фильтр по периоду ---

def filter_by_period(df, date_from=None, date_to=None):
    """Фильтрует DataFrame по диапазону дат (включительно)."""
    result = df.copy()

    if date_from is not None:
        result = result[result["Дата"] >= pd.Timestamp(date_from)]
    if date_to is not None:
        result = result[result["Дата"] <= pd.Timestamp(date_to)]

    return result