-- Latest market snapshot

SELECT
    period,
    brent,
    wti,
    brent_wti_spread,
    production_kbd,
    stocks_kbbl,
    stock_change_kbbl,
    imports_kbd,
    exports_kbd,
    net_imports_kbd
FROM weekly_market
ORDER BY period DESC
LIMIT 10;


-- Four-week averages using window functions

SELECT
    period,
    brent,
    AVG(brent) OVER (
        ORDER BY period
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) AS brent_4w_average,

    production_kbd,
    AVG(production_kbd) OVER (
        ORDER BY period
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) AS production_4w_average,

    net_imports_kbd,
    AVG(net_imports_kbd) OVER (
        ORDER BY period
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) AS net_imports_4w_average
FROM weekly_market
ORDER BY period;


-- Largest commercial inventory draws

SELECT
    period,
    stocks_kbbl,
    stock_change_kbbl,
    brent
FROM weekly_market
WHERE stock_change_kbbl IS NOT NULL
ORDER BY stock_change_kbbl ASC
LIMIT 20;


-- Largest commercial inventory builds

SELECT
    period,
    stocks_kbbl,
    stock_change_kbbl,
    brent
FROM weekly_market
WHERE stock_change_kbbl IS NOT NULL
ORDER BY stock_change_kbbl DESC
LIMIT 20;


-- Largest Brent weekly moves

SELECT
    period,
    brent,
    ROUND(brent_return_1w * 100, 2)
        AS weekly_return_pct
FROM weekly_market
WHERE brent_return_1w IS NOT NULL
ORDER BY ABS(brent_return_1w) DESC
LIMIT 20;


-- Weeks where net imports were unusually high

WITH trade_stats AS (
    SELECT
        AVG(net_imports_kbd) AS mean_net_imports
    FROM weekly_market
)
SELECT
    w.period,
    w.imports_kbd,
    w.exports_kbd,
    w.net_imports_kbd,
    w.brent
FROM weekly_market AS w
CROSS JOIN trade_stats AS t
WHERE w.net_imports_kbd > t.mean_net_imports
ORDER BY w.net_imports_kbd DESC
LIMIT 20;