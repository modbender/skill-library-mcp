# Referência: Funções do InvestmentAnalystAgent

## get_market_data

```python
def get_market_data(ticker: str, period: str = "1y") -> dict:
    """
    Obtem dados de mercado para um ativo.
    
    Args:
        ticker: Symbol (ex: PETR4, XIIG11, BTC)
        period: Periodo (1d, 1w, 1m, 6m, 1y, 5y)
    
    Returns:
        dict: {
            "price": float,
            "change": float,
            "volume": int,
            "high": float,
            "low": float,
            "fundamentalists": {
                "pl": float,
                "pvp": float,
                "dividend_yield": float,
                "roe": float,
                "divida_patrimonio": float
            }
        }
    """
```

## calculate_roi

```python
def calculate_roi(initial_value: float, final_value: float, days: int = None) -> dict:
    """
    Calcula retorno sobre investimento.
    
    Args:
        initial_value: Valor inicial investido
        final_value: Valor atual/final
        days: Numero de dias (opcional, para anualizar)
    
    Returns:
        dict: {
            "roi_percent": float,
            "roi_annualized": float,
            "total_gain": float,
            "cagr": float  # se days informado
        }
    """
```

## portfolio_analysis

```python
def portfolio_analysis(holdings: list[dict]) -> dict:
    """
    Analisa carteira de investimentos.
    
    Args:
        holdings: Lista de {
            "ticker": str,
            "quantity": float,
            "avg_price": float,
            "current_price": float,
            "type": str  # "acao", "fii", "renda_fixa", "crypto"
        }
    
    Returns:
        dict: {
            "total_value": float,
            "allocation": dict,  # por tipo
            "concentration": dict,  # por ativo
            "diversification_score": float,
            "suggestions": list[str]
        }
    """
```

## generate_report

```python
def generate_report(asset: str, report_type: str = "fundamentalist") -> str:
    """
    Gera relatorio de analise.
    
    Args:
        asset: Ativo ou ticker
        report_type: "fundamentalist", "technical", "full", "comparative"
    
    Returns:
        str: Relatorio em formato markdown
    """
```

## risk_profile_classifier

```python
def risk_profile_classifier(answers: dict) -> str:
    """
    Classifica perfil de risco do investidor.
    
    Args:
        answers: Respostas do questionario {
            "age": int,
            "investment_horizon": str,  # "short", "medium", "long"
            "risk_tolerance": str,  # "low", "medium", "high"
            "experience": str,  # "none", "little", "moderate", "high"
            "loss_tolerance": str  # "low", "medium", "high"
        }
    
    Returns:
        str: "conservative", "moderate", ou "aggressive"
    """
```
