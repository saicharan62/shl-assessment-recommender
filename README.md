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

---

## 8. Notes & Limitations

* Only publicly available catalog information is used.
* Assessment metadata such as duration or test type is not enforced due to inconsistent availability.
* The system is designed to be deterministic, simple, and easy to test.

---

## 9. Final Remarks

This solution prioritizes **clarity, correctness, and robustness** over complexity. All required components — API, evaluation logic, and CSV output — are included, along with supporting scripts for transparency.

Thank you for reviewing this submission.
