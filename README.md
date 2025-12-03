# 📊 Data Pipeline Serverless com Clusterização, Retry Inteligente e Testes Profissionais

Este projeto implementa um **data pipeline serverless em AWS**, totalmente desacoplado e orientado a eventos, com foco em **alta disponibilidade, eficiência de custo, resiliência a falhas e testabilidade profissional**.  
Ele resolve automaticamente problemas de **gaps de dados**, **falhas de integração com APIs externas** e **reprocessamento controlado** via filas.

---

## 🚀 Tecnologias e Habilidades

| Categoria        | Tecnologia                  | Habilidade Demonstrada                                                                  |
|------------------|-----------------------------|-----------------------------------------------------------------------------------------|
| Arquitetura      | AWS Lambda, SQS             | Orquestração de workflows assíncronos e desacoplados                                    |
| Banco de Dados   | Amazon DynamoDB             | Modelagem NoSQL Single-Table, otimização de consultas e mitigação de *Hot Partitions*   |
| Análise/Dados    | Python, Pandas              | Manipulação de Séries Temporais e análise de gaps                                       |
| Testes           | Pytest, unittest.mock      | Isolamento de código e simulação de serviços AWS (*Mocking*)                             |
| Infra/Segurança  | IAM, Variáveis de Ambiente | Princípio do Mínimo Privilégio e portabilidade entre ambientes                           |

---

## 📐 Abstrações e Padrões de Design

O projeto aplica padrões consagrados de **engenharia de dados para ambientes de alto volume**.

### 1. Modelagem Otimizada (Single-Table Design)

- **Chave Primária Composta**  
  Uso de *Partition Key* (`info_type`) para agrupar dados por ativo (`CURRENCY#USD`, `CURRENCY#BRL`, `FUEL#DISEL` etc)  
  e *Sort Key* (`date`) para permitir consultas eficientes por intervalo de tempo.

- **Otimização de I/O**  
  Toda a leitura é feita via **uma única `Query` altamente restritiva por PK**, seguindo as boas práticas do DynamoDB.  
  Filtros adicionais são processados **em memória (Python)**, evitando múltiplas chamadas de rede.

---

### 2. Otimização de Fluxo de Trabalho e Batching

O sistema de orquestração de downloads é otimizado para a **natureza das APIs externas** e para a **eficiência de escrita no DynamoDB**.

- **Separação por Streams Contínuos**  
  As datas a serem processadas são agrupadas em **sequências contínuas de dias (*streams*)**, em vez de requisições isoladas por data.

- **Motivação Técnica**  
  Muitas APIs financeiras (ex.: Banco Central) oferecem melhor desempenho quando recebem **intervalos contínuos de datas** (`data_inicial` → `data_final`) em uma única chamada.  
  Esse agrupamento:
  - Reduz o número total de requisições
  - Minimiza latência de rede
  - Diminui o risco de *throttling*

- **Batching para Inserção no DynamoDB**  
  Cada *stream* contínuo é dividido em **lotes de até 25 itens**, aproveitando o limite máximo da operação `BatchWriteItem`.

  Benefícios:
  - Maximiza o throughput de escrita
  - Reduz drasticamente a latência total
  - Diminui o custo operacional em comparação a múltiplos `PutItem` individuais

---

## ⚙️ Arquitetura do Data Pipeline (Clusterização)

O pipeline é **completamente desacoplado** em dois estágios via **Amazon SQS**.

### 1. Orchestrator Lambda (`data_clustering`)

- **Função:** Executa periodicamente via agendamento.
- **Responsabilidades:**
  - Consulta otimizada no DynamoDB
  - Identificação de Gaps 
- **Saída:**  
  Envio da `partition_key` e da lista de `dates_to_download` para a fila SQS.

---

### 2. Scraper Worker Lambda ('scraper')

- **Função:** Processa mensagens da fila SQS.
- **Responsabilidades:**
  - Deserialização do payload
  - Chamada à fonte externa (scraping)
  - Persistência final via `PutItem` no DynamoDB

Esse modelo garante:
- Escalabilidade horizontal automática
- Isolamento de falhas
- Alta resiliência a picos de carga

---

## 💻 Testes Profissionais e Isolamento

O projeto está sendo desenvolvido com **testabilidade como requisito arquitetural**.

### Injeção de Dependências

Os clientes AWS (`table`, `sqs_client`) são injetados nas funções, permitindo que o **ambiente de teste substitua completamente os serviços reais da AWS**.

### Mocking de Serviços

Utiliza:
- `unittest.mock`
- `pytest`

Com isso, é possível:
- Simular respostas do DynamoDB
- Simular envios ao SQS
- Validar a lógica de *retry* e *gap detection*
- Executar testes de forma **rápida, isolada e sem custo de nuvem**

---

## ✅ Principais Benefícios da Arquitetura

- Totalmente **serverless**
- **Baixo acoplamento** entre componentes
- **Alta escalabilidade**
- **Tolerância a falhas**
- **Custo otimizado**
- **Testes automatizados sem dependência de cloud real**

---

## 👨‍💻 Autor

Projeto desenvolvido por **Gabriel**  
Foco em **Engenharia de Dados Serverless, Arquiteturas Escaláveis e Boas Práticas Profissionais de Teste**.
