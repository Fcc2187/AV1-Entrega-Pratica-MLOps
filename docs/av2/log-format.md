# AV2 — formato do log de inferência

Implementação: `src/careerpath/monitoring.py`, integrada ao serviço BentoML com
`workers=1`. Formato versão 1: arquivo UTF-8 JSONL, um objeto JSON por linha.
O handler abre em modo `a`, acrescenta e descarrega cada evento; iniciar novamente
o serviço com o mesmo caminho não apaga as linhas anteriores.

## Executar e observar

Usar o ambiente preparado no [baseline](phase-1-baseline.md). Na raiz do projeto:

```powershell
$env:CAREERPATH_LOG_PATH = 'logs/inference.jsonl'
uv run --frozen bentoml serve careerpath.service:CareerPathService --host 127.0.0.1 --port 3000 --do-not-track
```

Em outro terminal, enviar uma inferência e consultar o arquivo:

```powershell
curl.exe -X POST http://127.0.0.1:3000/predict -H 'Content-Type: application/json' --data-binary '@examples/case-1.json'
Get-Content -LiteralPath logs/inference.jsonl -Tail 5
```

Se a variável não existir, o padrão é `logs/inference.jsonl`. Caminhos relativos
partem do diretório de trabalho do processo. O diretório pai é criado no startup.
`.env.example` documenta o nome, mas não é carregado automaticamente: exportar a
variável no shell. Em Linux/macOS, usar `export CAREERPATH_LOG_PATH=logs/inference.jsonl`.

O logger/arquivo é configurado no startup do worker, não no import do supervisor,
e fechado no shutdown. A configuração repetida do mesmo destino não duplica o
handler. `logs/`, `.bentoml/` e os destinos temporários usados pelos testes não
entram no commit; caminhos personalizados precisam de exclusão própria se necessário.

## Dicionário do evento

| Campo | Tipo e significado |
| --- | --- |
| `schema_version` | Inteiro `1`; versão do contrato do arquivo |
| `timestamp` | String ISO 8601 UTC, com seis dígitos de microssegundos e `+00:00` |
| `request_id` | String UUID v4 gerada para cada pedido; não reutiliza IDs do cliente |
| `method` | Método HTTP recebido |
| `endpoint` | Caminho `/predict`; queries não são gravadas |
| `status_code` | Inteiro enviado no início da resposta, ou `null` se a resposta não começou |
| `outcome` | `success`, `client_error` ou `server_error` |
| `latency_ms` | Número não negativo; relógio monotônico, do início HTTP ao envio do último chunk |
| `input` | Objeto com os campos de entrada permitidos, antes da normalização do Pydantic |
| `input_capture` | `complete`, `invalid_json`, `truncated` ou `unsupported` |
| `output` | Classe, probabilidade e versão devolvidas; `null` em falha ou captura de saída indisponível |
| `model_version` | Versão do artefato carregado, presente também nos eventos de erro |
| `error_type` | `null` em sucesso; categoria `client_error` ou `server_error`, sem mensagem da exceção |

A latência exclui a escrita do próprio log e tarefas posteriores à conclusão da
resposta. Se a resposta não termina, o evento usa o instante de saída/falha do ASGI.
O instante tem precisão de representação de microssegundos; isso não promete a
mesma resolução física do relógio do sistema. A medição pode diferir da do BentoML
porque as fronteiras de instrumentação são distintas.

O status é preservado mesmo se uma resposta parcial já começou com 200 e depois
falhou: nesse caso o evento tem `status_code=200`, `outcome=server_error` e saída
nula. Exceções não tratadas são propagadas ao servidor, sem fabricar outra resposta.

## Entradas e saídas permitidas

Entrada: `age`, `education`, `workclass`, `occupation`, `marital_status` e
`hours_per_week`. Saída: `income_class_proxy`, `probability_above_50k` e `model_version`.

Valores escalares e nulos são preservados; strings são limitadas a 80 caracteres.
Campo ausente continua ausente, enquanto `null` explícito permanece `null`.
Valores aninhados são omitidos. Não se gravam campos extras, corpo bruto, headers,
autorização, IP, cookies, query string ou texto de exceções. O JSONL escapa quebras
de linha e Unicode, preservando o valor quando decodificado com `json.loads`.
`NaN` e infinitos não são serializados como números JSON.

`input_capture=complete` significa JSON objeto capturado por inteiro; não significa
que passou pela validação do perfil. Pedidos 400 também podem ter esse valor.
Interpretar `input_capture` junto com `outcome` e `status_code` nas análises.

O limite é **8192 bytes por corpo**, tanto na cópia de entrada quanto na de saída.
A cópia deixa de crescer ao atingir o limite; os bytes originais continuam para
o servidor/cliente. Uma requisição JSON válida com muito espaço em branco ainda
pode retornar 200, com `input_capture=truncated`, `input={}` e saída preservada.
Não usar capturas truncadas nas distribuições de features.

`invalid_json` inclui sintaxe/codificação inválida e constantes não finitas.
`unsupported` inclui corpo incompleto, JSON cuja raiz não é objeto ou tipo de
conteúdo diferente de JSON. Nenhuma dessas condições cria uma nova regra de
rejeição HTTP: o contrato da API continua sendo validado pelo BentoML/Pydantic.

## Escolha das variáveis e análises futuras

| Variável | Uso no contexto CareerPath e análise possível |
| --- | --- |
| `age`, `hours_per_week` | Caracterizar mudanças nos perfis recebidos; histogramas, boxplots e futura comparação numérica KS/PSI |
| Escolaridade, vínculo, ocupação, estado civil | Frequências e PSI categórico, incluindo nulos e categorias desconhecidas |
| `probability_above_50k` | Distribuição do sinal socioeconômico devolvido; histograma, boxplot e futura comparação com probabilidades da referência |
| `income_class_proxy` | Proporção das classes previstas |
| `latency_ms`, `status_code`, `outcome` | Distribuição da duração e desfechos operacionais |

São as features e saídas do componente socioeconômico já descrito no entendimento
de negócio. O rastro não mede intenção de compra, necessidade profissional, renda
atual comprovada ou conversão comercial. Mudança na distribuição, isoladamente,
não comprova queda de acurácia nem mudança na relação entre features e rótulo.

A referência prevista é Adult com a mesma preparação de `train.py`; para a saída,
usar probabilidades produzidas pelo mesmo modelo nos perfis de referência, e não
comparar diretamente probabilidades com rótulos reais. O detalhamento está no
[escopo](escopo.md). Nesta fase não foram implementados KS, PSI, gráficos ou alertas.

## Falhas, retenção e limites

- São registrados pedidos de `/predict`, inclusive validação rejeitada e falha
  interna. `/health` e `/metrics` são encaminhados sem virar eventos de inferência.
- Falha de abertura do destino impede concluir o startup. Falha posterior de
  escrita emite `CareerPath monitoring: failed to write inference event` em stderr,
  mesmo com `logging.raiseExceptions=False`, e preserva a resposta HTTP.
- Se a escrita falhar ou o processo cair abruptamente, o evento pode ser perdido:
  este arquivo não é uma transação durável, fila ou mecanismo de recuperação.
- Não há rotação ou expiração automática nesta fase. O arquivo fica no disco até
  remoção manual; o serviço não reescreve seu conteúdo para acrescentar eventos.
- O `FileHandler` coordena threads no único worker; não há garantia de escrita
  entre vários processos/instâncias apontando para o mesmo arquivo.
- O Dockerfile prepara `/app/logs` para UID 10001 para compatibilidade com o novo
  startup. Build real e persistência por volume ficam para a fase 5; remover um
  container sem volume pode remover seus logs.

## Verificação realizada

- Teste inicial falhou porque a API ainda não criava o arquivo; depois da implementação,
  a suíte completa passou com **59 testes em 23,66 s**.
- Cobertos append entre lifespans, reconfiguração sem duplicação, sucesso, 400,
  500, nulos, Unicode, limites/chunks, concorrência, falha no startup e falha de disco.
- Servidor HTTP real produziu exatamente três eventos para um pedido válido, um
  perfil inválido e um JSON malformado; a saída no arquivo correspondeu à resposta.
  Consultas a health e metrics não acrescentaram linhas; o servidor foi encerrado.
- A consulta a `/metrics` via TestClient em memória ficou esperando sem resposta,
  também isoladamente. O teste do filtro foi feito na fronteira ASGI e a consulta
  real foi validada pelo CLI; não se alterou a instrumentação nativa do BentoML.

Capturas locais de verificação ficam em `.bentoml/phase2/`, fora do Git. A próxima
fase detalhará a interpretação de `/metrics` e seus cálculos.
