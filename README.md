# 📊 Serverless Data Pipeline with Clustering, Intelligent Retry & Production-Grade Testing

This project implements a **fully serverless, event-driven data pipeline on AWS**, designed for **high availability, cost efficiency, fault tolerance, and professional-grade testability**.  
It automatically handles **data gaps**, **external API failures**, and **controlled reprocessing** through message queues.

In addition to the main pipeline, the architecture includes a **specialized Lambda function dedicated exclusively to rechecking the database and triggering controlled re-downloads** of missing or invalid data. This separation was a **deliberate design choice to reduce system complexity and improve long-term maintainability**.

The repository also features a **fully automated CI/CD deployment system using OIDC (OpenID Connect)** instead of static AWS secret keys, ensuring **high security even with a public repository**.

---

## 🔐 Secure CI/CD with OIDC (No Secret Keys)

This project uses **GitHub Actions with OIDC authentication** to deploy Lambda functions securely to AWS:

- **No AWS access keys are stored in the repository**
- GitHub Actions assumes an **AWS IAM Role via OIDC**
- The deployment is **short-lived, scoped, and auditable**
- Safe for **fully public repositories**

### Automated Lambda Sync

- Each Lambda function in AWS is **automatically matched to a directory in the repository**
- The **GitHub Actions YAML workflow**:
  - Detects changes in the repo
  - Packages the code
  - Deploys each function to the **Lambda with the same name**
- This ensures:
  - Zero manual deployments
  - Full traceability
  - Reproducible infrastructure behavior
  - Production-ready DevOps workflow

This approach follows **cloud security best practices** and eliminates the risks of credential leakage.

---

## 🚀 Technologies & Skills

| Category          | Technology                     | Demonstrated Skill                                                                 |
|-------------------|--------------------------------|-------------------------------------------------------------------------------------|
| Architecture      | AWS Lambda, SQS                | Orchestration of asynchronous, decoupled workflows                                 |
| Database          | Amazon DynamoDB                | NoSQL Single-Table Design, query optimization, and *Hot Partition* mitigation      |
| Data & Analysis   | Python, Pandas                 | Time-series manipulation and gap analysis                                          |
| Testing           | Pytest, unittest.mock          | Code isolation and AWS service simulation (*Mocking*)                               |
| Infra & Security  | IAM, OIDC, Environment Vars   | Least Privilege, secure CI/CD, and environment portability                         |
| DevOps            | GitHub Actions                | Automated build, test, and deployment pipelines                                    |

---

## 📐 Abstractions & Design Patterns

The project applies **established data engineering patterns for high-throughput environments**.

### 1. Optimized Data Modeling (Single-Table Design)

- **Composite Primary Key**  
  Use of *Partition Key* (`info_type`) to group data by asset  
  (e.g., `CURRENCY#USD`, `CURRENCY#BRL`, `FUEL#DIESEL`)  
  and *Sort Key* (`date`) to enable efficient time-range queries.

- **I/O Optimization**  
  All reads are executed through **a single highly selective `Query` per PK**, following DynamoDB best practices.  
  Additional filters are processed **in-memory (Python)**, avoiding multiple network calls.

---

### 2. Workflow Optimization & Batching

The download orchestration system is optimized for **external API behavior** and **DynamoDB write efficiency**.

- **Continuous Stream Grouping**  
  Dates to be processed are grouped into **continuous sequences (*streams*)** rather than isolated date requests.

- **Technical Motivation**  
  Many financial APIs (e.g., Central Bank APIs) perform better when receiving **continuous date ranges**  
  (`start_date` → `end_date`) in a single request.  
  This approach:
  - Reduces the total number of requests  
  - Minimizes network latency  
  - Decreases the risk of *throttling*

- **DynamoDB Batch Writes**  
  Each continuous stream is split into **batches of up to 25 items**, leveraging the `BatchWriteItem` limit.

  Benefits:
  - Maximizes write throughput  
  - Drastically reduces total latency  
  - Lowers operational cost compared to multiple individual `PutItem` calls

---

## ⚙️ Data Pipeline Architecture (Clustering + Controlled Retry)

The pipeline is **fully decoupled** into specialized stages using **Amazon SQS** and dedicated Lambda functions.

### 1. Orchestrator Lambda (`data_clustering`)

- **Trigger:** Scheduled execution.
- **Responsibilities:**
  - Optimized queries on DynamoDB  
  - Detection of missing data (*gaps*)  
- **Output:**  
  Sends `partition_key` and the list of `dates_to_download` to the SQS queue.

---

### 2. Scraper Worker Lambda (`scraper`)

- **Trigger:** SQS message consumption.
- **Responsibilities:**
  - Payload deserialization  
  - External data source request (scraping)  
  - Final persistence via `PutItem` in DynamoDB  

This model ensures:
- Automatic horizontal scalability  
- Fault isolation  
- High resilience under load spikes

---

### 3. Specialized Recheck & Retry Lambda (`retry_recheck`)

To handle persistent data issues without overloading the main pipeline, the architecture includes a **dedicated Lambda function exclusively responsible for controlled reprocessing**.

- **Purpose:**  
  Periodically re-scan the database to identify records with **`null` values or incomplete fields**.

- **Retry Control:**  
  Each record contains a `retry_count` attribute.  
  - The function **re-enqueues the item for re-download only if `retry_count < 5`**  
  - After each failed attempt, `retry_count` is incremented  
  - Once the limit is reached, the record is **quarantined for manual inspection**

- **Architectural Rationale:**  
  This logic was intentionally **separated from the main pipeline** to:
  - Reduce cognitive and operational complexity  
  - Prevent infinite retry loops  
  - Improve debuggability and observability  
  - Make the core ingestion pipeline simpler and more reliable

This design introduces **bounded, auditable, and safe retries**, aligned with production-grade data engineering practices.

---

## 💻 Production-Grade Testing & Isolation

The project is designed with **testability as a core architectural requirement**.

### Dependency Injection

AWS clients (`table`, `sqs_client`) are injected into functions, allowing the **test environment to fully replace real AWS services**.

### AWS Service Mocking

Uses:
- `unittest.mock`
- `pytest`

This enables:
- Simulation of DynamoDB responses  
- Simulation of SQS message publishing  
- Validation of *retry logic* and *gap detection*
- Fast, isolated tests with **zero cloud cost**

---

## ✅ Key Architectural Benefits

- Fully **serverless**
- **Loosely coupled** components
- **High scalability**
- **Fault tolerant**
- **Cost optimized**
- **Automated testing without real cloud dependencies**
- **Bounded and auditable retry mechanism**
- **Secure CI/CD via OIDC (no static credentials)**
- **Automatic Lambda deployment from GitHub**
- **Improved maintainability via functional separation**

---

## 👨‍💻 Author

Project developed by **Gabriel**  
Focused on **Serverless Data Engineering, Scalable Architectures, Secure CI/CD, and Professional Testing Best Practices**
