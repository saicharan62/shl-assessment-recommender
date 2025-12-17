"""
main.py

FastAPI application for SHL Assessment Recommendation Engine
"""
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from scripts.recommend import SHLRecommender


# -------- App Init --------
app = FastAPI(
    title="SHL GenAI Assessment Recommender",
    description="Recommends relevant SHL individual assessments based on text query",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OK for assignment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load recommender ONCE at startup
recommender = None


# -------- Request / Response Models --------
class RecommendRequest(BaseModel):
    query: str


class AssessmentResponse(BaseModel):
    assessment_name: str
    assessment_url: str


class RecommendResponse(BaseModel):
    recommendations: List[AssessmentResponse]


# -------- Routes --------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    global recommender

    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if recommender is None:
        recommender = SHLRecommender(top_k=10)

    raw_results = recommender.recommend(req.query)

    # 🔑 MAP INTERNAL FORMAT → SHL CONTRACT
    formatted_results = [
        {
            "assessment_name": r["name"],
            "assessment_url": r["url"],
        }
        for r in raw_results
    ]

    return {"recommendations": formatted_results}
