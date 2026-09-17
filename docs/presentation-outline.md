# Roteiro da apresentação — 15 minutos

Este roteiro segue exatamente os quatro blocos da rubrica. Depois dos 15 minutos,
reservar 5 minutos para perguntas. Preencher os responsáveis antes do ensaio; os
nomes não foram inventados neste documento.

| Bloco | Tempo | Responsável |
| --- | ---: | --- |
| 1. Objetivo | 0:00–2:00 | `[definir integrante]` |
| 2. Processo de negócio | 2:00–5:00 | `[definir integrante]` |
| 3. Como subir | 5:00–9:00 | `[definir integrante]` |
| 4. Demonstração | 9:00–15:00 | `[definir integrante]` |

Todos os integrantes presentes devem falar. Se houver mais de quatro integrantes,
dividir a demonstração ou as perguntas técnicas; se houver menos, uma pessoa pode
assumir mais de um bloco.

## 1. Objetivo — 2 minutos

Tela: início do README.

- Apresentar a PoC CareerPath e o problema de priorização comercial.
- Explicar que a API recebe seis atributos e estima a classe histórica de renda
  `>50K` do Adult como sinal socioeconômico auxiliar.
- Separar claramente o resultado do modelo do objetivo comercial: não mede renda
  atual, intenção de compra, necessidade profissional ou potencial de carreira.
- Reforçar que não há decisão automática sobre pessoas; a revisão humana permanece.
- Antecipar o resultado técnico: serviço local reproduzível, artefato versionado,
  contrato HTTP validado e operação de inferência sem download ou novo treino.

Frase de transição: “Para entender onde esse sinal entra, vamos comparar o fluxo
atual com o processo futuro proposto.”

## 2. Processo de negócio — 3 minutos

Tela: seção “Objetivo e uso responsável” do README ou diagrama simples no quadro.

- Hoje: atendimento por ordem de chegada, engajamento e julgamento do consultor.
- Futuro proposto: processamento noturno forma uma fila no CRM até 08:00; Growth
  revisa a ordem; o consultor decide se fará o contato.
- A API implementa somente o componente socioeconômico. Engajamento, necessidade,
  estágio de carreira e tempo de espera não existem no Adult e não foram inventados.
- Meta do piloto: aumento relativo de 20% na conversão em oito semanas, 75% de
  confirmação do público-alvo entre alta prioridade e 60% das abordagens vindas
  da fila. São metas do negócio, não resultados do modelo.
- O Adult é uma base censitária dos EUA de 1994. A exclusão de `race` e `sex`
  reduz coleta direta de atributos sensíveis, mas não elimina vieses ou proxies.
- Se o serviço estiver indisponível, o fluxo retorna ao atendimento manual.

Frase de transição: “Com o limite de uso definido, vamos mostrar como qualquer
pessoa da equipe consegue reproduzir o serviço.”

## 3. Como subir — 4 minutos

Tela: README, da seção “Pré-requisitos” até “Primeira execução”.

1. Mostrar Python 3.12, Git e uv 0.12.5 como pré-requisitos.
2. Mostrar `uv.lock`, `pyproject.toml` e o artefato em `models/`.
3. Executar ou explicar:

   ```powershell
   uv sync --frozen --python 3.12
   uv run --frozen bentoml serve careerpath.service:CareerPathService --host 127.0.0.1 --port 3000 --do-not-track
   ```

4. Explicar que o modelo é carregado localmente, validando versão e SHA-256 antes
   do pickle; startup e inferência não baixam dados e não treinam como fallback.
5. Mostrar o contrato dos seis campos, os arquivos em `examples/`, os comandos de
   qualidade e a solução de problemas.
6. Informar o tempo observado: instalação preparada em menos de um segundo na
   Fase 6; nesta coleta fria, 81 pacotes foram preparados em 11,86 s. O startup
   observado ficou disponível após a inicialização do worker.

Frase de transição: “Com o serviço iniciado, vamos atravessar o contrato HTTP com
casos reais da demonstração.”

## 4. Demonstração — 6 minutos

Tela: terminal do serviço à esquerda e terminal de chamadas à direita.

1. Health:

   ```powershell
   curl.exe http://127.0.0.1:3000/health
   ```

   Confirmar HTTP 200, `status: ok` e `adult-income-v1`.

2. Executar `case-1.json` e apontar os três campos da resposta: classe proxy,
   probabilidade da classe histórica `>50K` e versão do modelo.
3. Executar `case-2.json`; explicar que categorias desconhecidas são aceitas pelo
   `OneHotEncoder(handle_unknown="ignore")`, mas não possuem efeito aprendido.
4. Executar `case-3.json`; explicar a imputação de `workclass` e `occupation` nulos.
5. Executar `invalid.json`; mostrar HTTP 400 e a regra `age >= 17`.
6. Mostrar `docs/evidence/` e o resultado final:

   ```text
   41 passed in 18.97s
   All checks passed!
   ```

7. Encerrar reforçando: a API funciona, mas sua saída é um proxy histórico e deve
   compor uma decisão humana, nunca determinar elegibilidade ou contato sozinha.

Se o serviço falhar ao vivo, gastar no máximo um minuto conferindo porta, artefato
e ambiente. Depois, usar o vídeo backup e explicar com transparência o ocorrido.

## Preparação para os 5 minutos de perguntas

Cada integrante deve conseguir responder, sem depender do próprio bloco:

- Qual decisão de negócio esta PoC apoia e quem mantém a decisão final?
- Por que `>50K` não equivale a intenção de compra ou renda atual?
- Quais seis features entram e por que as demais foram excluídas?
- Como o pipeline evita inconsistência entre treino e inferência?
- Por que usar `OneHotEncoder(handle_unknown="ignore")` e imputadores?
- Como o artefato é verificado antes de `pickle.loads`?
- O que `/health` comprova e o que ele não comprova?
- Por que uma entrada inválida retorna HTTP 400?
- O que o E2E valida ao reiniciar o serviço?
- O que acontece se o artefato estiver ausente ou corrompido?
- Quais são accuracy, ROC-AUC e o baseline, e por que comparar os dois?
- Como operar sem rede durante a apresentação?
- Qual foi a contribuição da IA e como a equipe revisou criticamente o resultado?

## Checklist do ensaio

- Preencher os responsáveis e garantir fala de todos os presentes.
- Ensaiar com cronômetro e manter os quatro blocos em 2 + 3 + 4 + 6 minutos.
- Preparar o ambiente e o cache antes da apresentação.
- Fechar processos que ocupem a porta 3000.
- Conferir modelo, metadata, exemplos e vídeo localmente.
- Não depender do Docker enquanto o daemon deste computador estiver indisponível.
- Não criar a tag `sr1` antes do horário e da revisão final da equipe.
