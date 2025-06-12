import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import time

Rf = 0.0435
Rm = 0.085
Tc = 0.21

def calcular_wacc(info, balance_sheet):
    try:
        beta = info.get("beta")
        price = info.get("currentPrice")
        shares = info.get("sharesOutstanding")
        market_cap = price * shares if price and shares else None
        lt_debt = balance_sheet.loc["Long Term Debt", :].iloc[0] if "Long Term Debt" in balance_sheet.index else 0
        st_debt = balance_sheet.loc["Short Long Term Debt", :].iloc[0] if "Short Long Term Debt" in balance_sheet.index else 0
        total_debt = lt_debt + st_debt
        Re = Rf + beta * (Rm - Rf) if beta is not None else None
        Rd = 0.055 if total_debt > 0 else 0
        E = market_cap
        D = total_debt
        if not Re or not E or not D or E + D == 0:
            return None, total_debt
        wacc = (E / (E + D)) * Re + (D / (E + D)) * Rd * (1 - Tc)
        return wacc, total_debt
    except:
        return None, None

def get_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        bs = stock.balance_sheet
        fin = stock.financials
        cf = stock.cashflow

        price = info.get("currentPrice")
        name = info.get("longName")
        sector = info.get("sector")
        country = info.get("country")
        industry = info.get("industry")
        pe = info.get("trailingPE")
        pb = info.get("priceToBook")
        dividend = info.get("dividendRate")
        dividend_yield = info.get("dividendYield")
        payout = info.get("payoutRatio")
        roa = info.get("returnOnAssets")
        roe = info.get("returnOnEquity")
        current_ratio = info.get("currentRatio")
        ltde = info.get("longTermDebtEquity")
        de = info.get("debtToEquity")
        op_margin = info.get("operatingMargins")
        profit_margin = info.get("netMargins")

        fcf = cf.loc["Total Cash From Operating Activities", :].iloc[0] if "Total Cash From Operating Activities" in cf.index else None
        shares = info.get("sharesOutstanding")
        pfcf = price / (fcf / shares) if fcf and shares else None

        ebit = fin.loc["EBIT", :].iloc[0] if "EBIT" in fin.index else None
        equity = bs.loc["Total Stockholder Equity", :].iloc[0] if "Total Stockholder Equity" in bs.index else None
        wacc, total_debt = calcular_wacc(info, bs)
        capital_invertido = total_debt + equity if total_debt and equity else None
        roic = ebit / capital_invertido if ebit and capital_invertido else None
        eva = roic - wacc if roic and wacc else None

        return {
            "Ticker": ticker,
            "Nombre": name,
            "Sector": sector,
            "PaÃ­s": country,
            "Industria": industry,
            "Precio": price,
            "P/E": pe,
            "P/B": pb,
            "P/FCF": pfcf,
            "Dividend Year": dividend,
            "Dividend Yield %": dividend_yield,
            "Payout Ratio": payout,
            "ROA": roa,
            "ROE": roe,
            "Current Ratio": current_ratio,
            "LtDebt/Eq": ltde,
            "Debt/Eq": de,
            "Oper Margin": op_margin,
            "Profit Margin": profit_margin,
            "WACC": wacc,
            "ROIC": roic,
            "EVA": eva,
            "Deuda Total": total_debt,
            "Patrimonio Neto": equity,
        }
    except Exception as e:
        return {"Ticker": ticker, "Error": str(e)}

if "resultados" not in st.session_state:
    st.session_state["resultados"] = {}

st.set_page_config(page_title="Dashboard Financiero", layout="wide")
st.title("ðŸ“Š Dashboard de AnÃ¡lisis Financiero")

# -------- SecciÃ³n 1 --------
st.markdown("## ðŸ“‹ SecciÃ³n 1: Ratios Financieros Generales")
tickers_input = st.text_area("ðŸ”Ž Ingresa hasta 50 tickers separados por coma", "AAPL,MSFT,GOOGL,TSLA,AMZN")
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
tickers = tickers[:50]

if st.button("ðŸ” Analizar"):
    nuevos = [t for t in tickers if t not in st.session_state["resultados"]]
    for i, t in enumerate(nuevos):
        st.write(f"â³ Procesando {t} ({i+1}/{len(nuevos)})...")
        st.session_state["resultados"][t] = get_data(t)
        time.sleep(1.5)

if st.session_state["resultados"]:
    datos = list(st.session_state["resultados"].values())
    df = pd.DataFrame(datos).drop(columns=["Deuda Total", "Patrimonio Neto", "Error"], errors="ignore")
    st.dataframe(df, use_container_width=True)



# ---------------------- SECCIÃ“N 5 ---------------------- #
st.markdown("## ðŸš€ SecciÃ³n 5: AnÃ¡lisis de Crecimiento")

for detalle in st.session_state["resultados"].values():
    nombre = detalle.get("Nombre", detalle["Ticker"])
    ticker = detalle["Ticker"]
    stock = yf.Ticker(ticker)
    fin = stock.financials
    cf = stock.cashflow
    bs = stock.balance_sheet

    try:
        revenue_growth = ((fin.loc["Total Revenue"][0] - fin.loc["Total Revenue"][1]) / abs(fin.loc["Total Revenue"][1]))
    except:
        revenue_growth = None

    try:
        eps_current = stock.info.get("trailingEps")
        eps_hist = stock.info.get("forwardEps")
        eps_growth = ((eps_current - eps_hist) / abs(eps_hist)) if eps_current and eps_hist else None
    except:
        eps_growth = None

    try:
        fcf_now = cf.loc["Total Cash From Operating Activities"][0]
        fcf_last = cf.loc["Total Cash From Operating Activities"][1]
        fcf_growth = (fcf_now - fcf_last) / abs(fcf_last)
    except:
        fcf_growth = None

    try:
        capex_now = cf.loc["Capital Expenditures"][0]
        capex_last = cf.loc["Capital Expenditures"][1]
        capex_growth = (capex_now - capex_last) / abs(capex_last)
    except:
        capex_growth = None

    try:
        bv_now = bs.loc["Total Stockholder Equity"][0]
        bv_last = bs.loc["Total Stockholder Equity"][1]
        bv_growth = (bv_now - bv_last) / abs(bv_last)
    except:
        bv_growth = None

    st.markdown(f"### ðŸ“Œ {nombre}")
    df_crecimiento = pd.DataFrame({
        "Indicador": [
            "Revenue Growth", "EPS Growth", "FCF Growth",
            "Book Value Growth", "CapEx Growth"
        ],
        "Crecimiento (%)": [
            revenue_growth * 100 if revenue_growth else None,
            eps_growth * 100 if eps_growth else None,
            fcf_growth * 100 if fcf_growth else None,
            bv_growth * 100 if bv_growth else None,
            capex_growth * 100 if capex_growth else None
        ]
    })

    st.dataframe(df_crecimiento.set_index("Indicador"))

    if all(val is not None and val > 5 for val in df_crecimiento["Crecimiento (%)"].dropna()):
        conclusion = "âœ… La empresa muestra un crecimiento sÃ³lido y consistente."
    elif any(val is not None and val < 0 for val in df_crecimiento["Crecimiento (%)"].dropna()):
        conclusion = "âŒ La empresa presenta seÃ±ales de contracciÃ³n o decrecimiento."
    else:
        conclusion = "âš ï¸ Crecimiento moderado, revisar evoluciÃ³n futura."

    st.markdown(f"**ConclusiÃ³n:** {conclusion}")
    st.markdown("---")

# ---------------------- SECCIÃ“N 6 ---------------------- #
st.markdown("## ðŸ’§ SecciÃ³n 6: Liquidez Avanzada")

for detalle in st.session_state["resultados"].values():
    nombre = detalle.get("Nombre", detalle["Ticker"])
    ticker = detalle["Ticker"]
    stock = yf.Ticker(ticker)
    bs = stock.balance_sheet
    cf = stock.cashflow
    fin = stock.financials

    try:
        cash = bs.loc["Cash"][0]
        current_liabilities = bs.loc["Current Liabilities"][0]
        current_assets = bs.loc["Total Current Assets"][0]
        inventory = bs.loc["Inventory"][0] if "Inventory" in bs.index else 0
        quick_ratio = (current_assets - inventory) / current_liabilities
        cash_ratio = cash / current_liabilities
        working_capital = current_assets - current_liabilities
    except:
        quick_ratio = cash_ratio = working_capital = None

    try:
        ebit = fin.loc["EBIT"][0]
        interest_expense = fin.loc["Interest Expense"][0]
        interest_coverage = ebit / abs(interest_expense)
    except:
        interest_coverage = None

    try:
        op_cash = cf.loc["Total Cash From Operating Activities"][0]
        op_cash_ratio = op_cash / current_liabilities
    except:
        op_cash_ratio = None

    st.markdown(f"### ðŸ“Œ {nombre}")
    df_liquidez = pd.DataFrame({
        "Indicador": [
            "Quick Ratio", "Cash Ratio", "Working Capital",
            "Interest Coverage", "Op. Cash Flow Ratio"
        ],
        "Valor": [
            quick_ratio, cash_ratio, working_capital,
            interest_coverage, op_cash_ratio
        ]
    })

    st.dataframe(df_liquidez.set_index("Indicador"))

    if quick_ratio and quick_ratio >= 1 and cash_ratio and cash_ratio >= 0.5 and interest_coverage and interest_coverage > 3:
        conclusion = "âœ… Buena liquidez y capacidad de pago a corto plazo."
    elif quick_ratio and quick_ratio < 1 or interest_coverage and interest_coverage < 1.5:
        conclusion = "âŒ Riesgo de liquidez, atenciÃ³n a obligaciones."
    else:
        conclusion = "âš ï¸ Liquidez aceptable pero frÃ¡gil, revisar contexto."

    st.markdown(f"**ConclusiÃ³n:** {conclusion}")
    st.markdown("---")
