# Write Confirmation Checklist

Use antes de qualquer update/delete/create com impacto relevante.

- [ ] Usuario confirmou intencao de escrita.
- [ ] Escopo da escrita esta delimitado (IDs e objetos).
- [ ] Status seguro foi definido (`PAUSED` para novas criacoes).
- [ ] Nao ha conflito com outras alteracoes em andamento.
- [ ] Risco financeiro foi explicitado.
- [ ] Rollback por objeto foi descrito.
- [ ] Confirmacao final recebida para operacoes irreversiveis.

## Operacoes sempre sensiveis

- `delete_object`
- `delete_audience`
- aumentos grandes de budget
- alteracoes em lote de targeting
