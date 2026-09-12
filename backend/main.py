"""Оркестрация: загрузка → фильтр → аналитика → экспорт."""

import argparse
import warnings
from datetime import date, datetime, timedelta

import config
from analytics import analyze_by_month, analyze_by_month_shift, analyze_downtime, analyze_volume
from exporters import save_all
from loader import filter_by_period, load_dataframe

warnings.filterwarnings("ignore")


def parse_args():
    parser = argparse.ArgumentParser(description="Анализ упаковки по сменам")
    parser.add_argument("--from", dest="date_from", type=_parse_date,
                        help="Начало периода: YYYY-MM-DD")
    parser.add_argument("--to", dest="date_to", type=_parse_date,
                        help="Конец периода: YYYY-MM-DD")
    parser.add_argument("--month", type=_parse_month,
                        help="Месяц: 2026-01 или просто 1 (текущий год)")
    return parser.parse_args()


def _parse_date(text: str) -> date:
    return datetime.strptime(text, "%Y-%m-%d").date()


def _parse_month(text: str):
    """'2026-01' → (2026, 1); '1' → (текущий год, 1)."""
    if "-" in text:
        y, m = text.split("-")
        return int(y), int(m)
    return date.today().year, int(text)


def _resolve_period(args):
    """Приоритет: --month > --from/--to > config."""
    if args.month:
        year, month = args.month
        start = date(year, month, 1)
        if month == 12:
            end = date(year, 12, 31)
        else:
            end = date(year, month + 1, 1) - timedelta(days=1)
        return start, end

    return (
        args.date_from or config.DATE_FROM,
        args.date_to or config.DATE_TO,
    )


def main():
    args = parse_args()
    date_from, date_to = _resolve_period(args)

    if date_from or date_to:
        print(f"📅 Период: {date_from or '...'} → {date_to or '...'}")
    else:
        print("📅 Период: весь файл")

    df = load_dataframe()
    df = filter_by_period(df, date_from, date_to)

    if df.empty:
        print("❌ Нет данных за указанный период")
        return
    print(f"📊 Строк после фильтра: {len(df)}")

    volume = analyze_volume(df)
    downtime = analyze_downtime(df)
    by_month = analyze_by_month(df)
    by_month_shift = analyze_by_month_shift(df)

    _print_report(volume, downtime, by_month)

    print("\n" + "=" * 60)
    save_all(df, volume, downtime, by_month, by_month_shift)
    print("\n🎉 Готово")


def _print_report(volume, downtime, by_month):
    print("\n" + "=" * 60)
    print("📊  ОБЪЁМ")
    print("=" * 60)
    print(f"Общий: {volume['total_kg']:,.0f} кг ({volume['total_kg'] / 1000:,.1f} т)")
    for s, t in volume["by_shift_tons"].items():
        print(f"  Смена {s}: {t:,.1f} т")

    print("\n" + "=" * 60)
    print("⏱  ПРОСТОЙ")
    print("=" * 60)
    print(f"Общий: {downtime['total_hours']:.1f} ч")
    for s, h in downtime["by_shift_hours"].items():
        print(f"  Смена {s}: {h:.1f} ч")

    if by_month:
        print("\n" + "=" * 60)
        print("📅  ПО МЕСЯЦАМ")
        print("=" * 60)
        for m in by_month:
            print(f"  {m['label']}: {m['tons']:,.1f} т, {m['hours']:.1f} ч простоя")


if __name__ == "__main__":
    main()