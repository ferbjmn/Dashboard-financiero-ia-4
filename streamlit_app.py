
import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import time

# ParÃ¡metros para WACC
Rf = 0.0435
Rm = 0.085
Tc = 0.21

def calcular_wacc(info, balance_sheet):
    try:
        beta = info.get("beta")
        price = info.get("currentPrice")
        shares = info.get("sharesOutstanding")
        market_cap = price * shares if price and shares else None

        # Obtener deudas a largo y corto plazo
        posibles_nombres_st = ["Short Long Term Debt", "Short/Long Term Debt"]
        st_debt = next((balance_sheet.loc[n].iloc[0] for n in posibles_nombres_st if n in balance_sheet.index), 0)

        lt_debt = balance_sheet.loc["Long Term Debt"].iloc[0] if "Long Term Debt" in balance_sheet.index else 0
        total_debt = lt_debt + st_debt

        Re = Rf + beta * (Rm - Rf) if beta is not None else None
        Rd = 0.055 if total_debt > 0 else 0
        E = market_cap
        D = total_debt

        if Re is None or E is None or D is None or (E + D == 0):
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
        fcf = cf.loc["Total Cash From Operating Activities"].iloc[0] if "Total Cash From Operating Activities" in cf.index else None
        shares = info.get("sharesOutstanding")
        pfcf = price / (fcf / shares) if fcf and shares else None
        ebit = fin.loc["EBIT"].iloc[0] if "EBIT" in fin.index else None
        equity = bs.loc["Total Stockholder Equity"].iloc[0] if "Total Stockholder Equity" in bs.index else None

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

# ConfiguraciÃ³n de Streamlit
st.set_page_config(page_title="Dashboard Financiero", layout="wide")
st.title("ðŸ“Š Dashboard de AnÃ¡lisis Financiero")

if "resultados" not in st.session_state:
    st.session_state["resultados"] = {}

st.markdown("## ðŸ§® SecciÃ³n 1: Ratios Financieros Generales")
tickers_input = st.text_area("ðŸ”Ž Ingresa hasta 50 tickers separados por coma", "AAPL,MSFT,GOOGL,TSLA,AMZN")
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
tickers = tickers[:50]

if st.button("ðŸ” Analizar"):
    nuevos = [t for t in tickers if t not in st.session_state["resultados"]]
    for i, t in enumerate(nuevos):
        with st.spinner(f"â³ Procesando {t} ({i+1}/{len(nuevos)})..."):
            st.session_state["resultados"][t] = get_data(t)
            time.sleep(1.5)

if st.session_state["resultados"]:
    datos = list(st.session_state["resultados"].values())
    df = pd.DataFrame(datos).drop(columns=["Deuda Total", "Patrimonio Neto", "Error"], errors="ignore")
    st.dataframe(df, use_container_width=True)
