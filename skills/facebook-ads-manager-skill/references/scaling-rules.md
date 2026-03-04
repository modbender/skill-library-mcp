# Scaling Rules

Regras matematicas para escalar com menor risco.

## Principios

- Escala sem diagnostico previo aumenta custo e volatilidade.
- Escala deve ser incremental e reversivel.
- Medir por janela consistente e comparavel.

## Regra de incremento

- Incremento recomendado por ciclo: ate 20% no budget.
- Evitar saltos abruptos que reiniciem aprendizado de forma agressiva.
- Entre alteracoes, aguardar dados suficientes para comparar resultado.

## Classificacao operacional

- Winner: resultado acima da meta com volume consistente.
- Watchlist: resultado aceitavel, mas instavel.
- Bleeder: gasto relevante sem retorno proporcional.

## Acoes por classe

Winner:
- Escalar budget de forma incremental.
- Duplicar variacoes de criativo para sustentar frequencia.

Watchlist:
- Ajustar criativo/angulo antes de escalar.
- Revisar targeting e sinais de learning.

Bleeder:
- Reduzir exposicao rapidamente.
- Pausar ou reestruturar tese antes de novo investimento.

## Tools que suportam escala

- Medicao: `get_campaign_insights`, `get_adset_insights`, `get_ad_insights`
- Estrutura: `get_campaign_by_id`, `get_adset_by_id`, `get_ad_by_id`
- Ajuste: `update_campaign`, `update_adset`, `update_ad`
