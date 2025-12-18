# SHL GenAI Assessment Recommendation Engine

Hi 👋

This repository contains my solution for the **SHL GenAI Assessment Recommendation** assignment. The goal of this project is to build a **simple, deterministic, and review‑friendly** system that recommends relevant **individual SHL assessment solutions** based on a natural language query or job description.

I have intentionally kept the design minimal and transparent, focusing on correctness and reproducibility rather than overengineering.

---

## 1. Problem Statement (In Simple Words)

Given a free‑text query such as a job description or hiring requirement, the system should:

* Recommend **5–10 relevant SHL individual assessments**
* Use only assessments from SHL’s **product catalog**
* **Ignore pre‑packaged job solutions**
* Return results in a format suitable for **automated evaluation**

---

## 2. High‑Level Approach

The solution follows a clean retrieval‑based GenAI pipeline:

### a) Data Preparation (Offline)

* Individual assessment URLs were collected from SHL’s public product catalog.
* Pre‑packaged job solutions were filtered out during data preparation.
* The final catalog contains only in‑scope individual assessment solutions.

### b) Semantic Retrieval

* Assessment names are converted into vector embeddings using a sentence‑transformer model.
* A **FAISS index** is built for fast and deterministic similarity search.
* Incoming queries are embedded and matched against the catalog to retrieve the most relevant assessments.

### c) Recommendation Logic

* Semantic similarity is the primary signal.
* For queries that span multiple domains (e.g., technical + behavioral), semantic retrieval naturally provides diverse results.
* A very light post‑processing heuristic is applied to avoid overly narrow recommendations when soft‑skill intent is detected.

The system avoids complex rules and heavy metadata dependencies to preserve recall and robustness.

---

## 3. API Design

The application is exposed as a **FastAPI** service.

### Health Check

```
GET /health
```

Response:

```json
{ "status": "ok" }
```

### Recommendation Endpoint

```
POST /recommend
```

Request body:

```json
{
  "query": "Need a Java developer who can collaborate with stakeholders"
}
```

Response format (as required by SHL Appendix):

```json
{
  "recommendations": [
    {
      "assessment_name": "Core Java (Advanced Level)",
      "assessment_url": "https://www.shl.com/products/product-catalog/view/core-java-advanced-level-new/"
    }
  ]
}
```

Only the **minimum required attributes** are returned to ensure strict compatibility with SHL’s automated evaluation pipeline.

---

## 4. Evaluation Strategy

### Quantitative Evaluation

* **Recall@10** was implemented to evaluate retrieval quality using the provided **training dataset**.
* Only valid individual assessment URLs were considered during evaluation.
* Evaluation scripts are included in the repository as supporting evidence.

### Test Dataset

* The provided test dataset is unlabeled and intended for SHL’s internal evaluation.
* Predictions for the test set are generated and exported in the required CSV format.

### Recommendation Balance

For multi‑domain queries (e.g., technical skills + collaboration or behavioral skills), semantic embeddings naturally retrieve a mix of relevant assessments. A lightweight heuristic ensures that recommendations are not overly technical when soft‑skill intent is present, without enforcing hard constraints or relying on unavailable metadata.

---

## 5. CSV Output (Appendix 3)

Predictions are exported in the **long CSV format** required by SHL:

```
Query,Assessment_url
Query 1,URL 1
Query 1,URL 2
...
```

The generated file is available at:

```
data/predictions.csv
```

---

## 6. Running the Project Locally

### Install Dependencies

```
pip install -r requirements.txt
```

### Start the API

```
uvicorn main:app --reload
```

### Optional Frontend

A minimal HTML frontend is provided under the `frontend/` directory for quick local testing of the API. This is optional and not required for evaluation.

---

## 7. Repository Structure

```
├── app / main.py              # FastAPI application
├── scripts/                  # Data prep, indexing, recommendation & evaluation scripts
├── models/                   # FAISS index and metadata
├── data/                     # Dataset and CSV predictions
├── ui/                 # Minimal HTML frontend (optional)
├── requirements.txt
└── README.md
```


## 8. Deployment & Access URLs

To ensure the solution is easy to evaluate and test, the system is deployed publicly.

### API Endpoint (FastAPI)

The recommendation API is deployed on **Hugging Face Spaces** and can be queried programmatically:
```
https://charansai62-shl-assessment-recommender.hf.space/recommend

```

This endpoint is intended for automated testing and returns deterministic JSON responses.

A health endpoint is also exposed:
```
https://charansai62-shl-assessment-recommender.hf.space/health

```
### Web Application Frontend

A lightweight **Streamlit-based frontend** is deployed to allow quick manual testing of queries and to visually inspect recommendations:
```
https://shl-assessment-recommender-solution.streamlit.app/
```

This frontend is provided for demonstration and manual validation only; the API endpoint should be used for automated evaluation.

---

## 9. Technology Stack

* Python 3.10.9
* FastAPI – backend API framework
* FAISS (CPU) – fast similarity search
* Sentence-Transformers – semantic text embeddings
* Streamlit – lightweight frontend for rapid prototyping
* Hugging Face Spaces – cloud deployment

---

## 10. Automated Evaluation Readiness

The API design, response schema, and CSV output strictly follow the formats described in the assignment appendix. The system is deterministic and stateless at inference time, making it suitable for:

* automated API testing
* batch evaluation using CSV inputs
* reproducible scoring across multiple runs

No manual intervention is required once the service is running.
Thank you for reviewing this submission.

---
