"""Generate tests/fixtures/vivino_sample.xlsx — a hand-curated 50-row fixture
covering every dirty pattern in the spec §7.2."""

from __future__ import annotations

from pathlib import Path

import openpyxl

HERE = Path(__file__).parent

# Each tuple: (sheet, wine_name, country, region, rating, rating_count, price)
# Patterns documented inline so the fixture is self-explanatory.
ROWS: list[tuple[str, str, str, str, object, object, object]] = [
    # --- 5 whitelist-matchable producers (good case) ---
    ("Italy", "Castello di Ama Chianti Classico 2020", "Italy", "Toscana", 4.4, 1200, 38.0),
    ("Italy", "Tenuta San Guido Sassicaia 2018", "Italy", "Toscana", 4.7, 4500, 280.0),
    ("Italy", "Marchesi Antinori Tignanello 2019", "Italy", "Toscana", 4.6, 5200, 145.0),
    ("Italy", "Gaja Barbaresco 2017", "Italy", "Piemonte", 4.6, 1800, 230.0),
    ("Italy", "Biondi-Santi Brunello di Montalcino 2016", "Italy", "Toscana", 4.5, 900, 220.0),
    # --- 5 pass-1 misses, pass-2 LLM-cache should resolve ---
    ("Italy", "Tignanello 2019", "Italy", "Toscana", 4.5, 600, 130.0),
    ("Italy", "Sassicaia 2018", "Italy", "Toscana", 4.7, 4000, 290.0),
    ("Italy", "Solaia 2017", "Italy", "Toscana", 4.6, 800, 260.0),
    ("Italy", "Ornellaia 2018", "Italy", "Toscana", 4.5, 1500, 200.0),
    ("Italy", "Masseto 2017", "Italy", "Toscana", 4.8, 700, 850.0),
    # --- 3 truly ambiguous (no producer signal) ---
    ("Italy", "Rosso di Montalcino 2020", "Italy", "Toscana", 4.0, 250, 22.0),
    ("Italy", "Chianti Classico 2021", "Italy", "Toscana", 3.9, 180, 14.0),
    ("Italy", "Bolgheri Superiore 2018", "Italy", "Toscana", 4.2, 320, 55.0),
    # --- 5 macro-regions coverage ---
    ("Italy", "Vietti Barolo Castiglione 2019", "Italy", "Piemonte", 4.3, 1100, 65.0),
    ("Italy", "Allegrini Amarone della Valpolicella 2017", "Italy", "Veneto", 4.4, 1900, 75.0),
    ("Italy", "Planeta Etna Rosso 2020", "Italy", "Sicilia", 4.1, 450, 28.0),
    ("Italy", "Mastroberardino Taurasi 2016", "Italy", "Campania", 4.2, 380, 42.0),
    ("Italy", "Argiolas Turriga 2018", "Italy", "Sardegna", 4.3, 280, 58.0),
    # --- 10 with varying rating_count for Bayesian-shrinkage tests ---
    ("Italy", "Antica Cantina Test Wine A 2020", "Italy", "Toscana", 4.8, 5, 25.0),
    ("Italy", "Antica Cantina Test Wine B 2020", "Italy", "Toscana", 4.6, 50, 25.0),
    ("Italy", "Antica Cantina Test Wine C 2020", "Italy", "Toscana", 4.4, 500, 25.0),
    ("Italy", "Antica Cantina Test Wine D 2020", "Italy", "Toscana", 4.2, 5000, 25.0),
    ("Italy", "Antica Cantina Test Wine E 2020", "Italy", "Toscana", 4.0, 50000, 25.0),
    ("Italy", "Fattoria Pupille Saffredi 2019", "Italy", "Toscana", 4.4, 320, 78.0),
    ("Italy", "Podere Sapaio Volpolo 2020", "Italy", "Toscana", 4.1, 240, 32.0),
    ("Italy", "Villa Russiz Sauvignon 2021", "Italy", "Friuli-Venezia Giulia", 4.0, 180, 22.0),
    ("Italy", "Conte Vistarino Pernice 2019", "Italy", "Lombardia", 4.3, 110, 48.0),
    ("Italy", "Cascina Fontana Barolo 2018", "Italy", "Piemonte", 4.2, 90, 52.0),
    # --- 3 tuple-string country (dirt) ---
    ("Italy", "Dirty Tuple Wine A 2020", "('Italy',)", "Toscana", 4.0, 100, 20.0),
    ("Italy", "Dirty Tuple Wine B 2020", "('Italy',)", "Piemonte", 4.1, 150, 35.0),
    ("Italy", "Dirty Tuple Wine C 2020", "('Italy',)", "Veneto", 3.9, 220, 18.0),
    # --- 2 encoding-corruption rows ---
    ("Italy", "Encoding Test Wine A 2020", "ItalÃ«", "Toscana", 4.0, 100, 20.0),
    ("Italy", "Encoding Test Wine B 2020", "Italy", "ToscÃ\xa0na", 4.0, 100, 20.0),
    # --- 4 duplicates (will collapse to 2 in dedupe) ---
    ("Italy", "Frescobaldi Nipozzano Riserva 2019", "Italy", "Toscana", 4.2, 800, 28.0),
    ("Italy", "Frescobaldi Nipozzano Riserva 2019", "Italy", "Toscana", 4.2, 800, 28.0),
    ("Italy", "Bruno Giacosa Barbaresco 2018", "Italy", "Piemonte", 4.5, 600, 95.0),
    ("Italy", "Bruno Giacosa Barbaresco 2018", "Italy", "Piemonte", 4.5, 600, 95.0),
    # --- 5 non-Italian (must be filtered out post-cleaning) ---
    ("France", "Château Margaux 2015", "France", "Bordeaux", 4.8, 5000, 800.0),
    ("Spain", "Vega Sicilia Único 2010", "Spain", "Ribera del Duero", 4.7, 2000, 450.0),
    ("Argentina", "Catena Zapata Malbec 2019", "Argentina", "Mendoza", 4.3, 3000, 35.0),
    ("Portugal", "Quinta do Crasto Reserva 2018", "Portugal", "Douro", 4.4, 800, 38.0),
    ("USA", "Opus One 2018", "USA", "Napa Valley", 4.7, 4000, 380.0),
    # --- 3 missing price ---
    ("Italy", "Missing Price Wine A 2020", "Italy", "Toscana", 4.0, 100, None),
    ("Italy", "Missing Price Wine B 2020", "Italy", "Piemonte", 4.1, 150, None),
    ("Italy", "Missing Price Wine C 2020", "Italy", "Veneto", 3.9, 220, None),
    # --- 3 zero rating_count (validation failures) ---
    ("Italy", "Zero Reviews Wine A 2020", "Italy", "Toscana", 4.5, 0, 20.0),
    ("Italy", "Zero Reviews Wine B 2020", "Italy", "Toscana", 4.6, 0, 25.0),
    ("Italy", "Zero Reviews Wine C 2020", "Italy", "Toscana", 4.7, 0, 30.0),
    # --- 2 rating > 5 (data error, validation failures) ---
    ("Italy", "Impossible Rating Wine A 2020", "Italy", "Toscana", 5.4, 100, 20.0),
    ("Italy", "Impossible Rating Wine B 2020", "Italy", "Toscana", 5.2, 100, 25.0),
]

HEADERS = ["wine_name", "country", "region", "rating", "rating_count", "price"]


def main() -> None:
    by_sheet: dict[str, list[list[object]]] = {}
    for sheet, *rest in ROWS:
        by_sheet.setdefault(sheet, []).append(list(rest))
    wb = openpyxl.Workbook()
    default = wb.active
    if default is not None:
        wb.remove(default)
    for sheet, rows in by_sheet.items():
        ws = wb.create_sheet(title=sheet)
        ws.append(HEADERS)
        for r in rows:
            ws.append(r)
    out = HERE / "vivino_sample.xlsx"
    wb.save(out)
    total = sum(len(rs) for rs in by_sheet.values())
    print(f"wrote {out} with {total} rows across {len(by_sheet)} sheets")


if __name__ == "__main__":
    main()
