"""
main.py

FastAPI application for SHL Assessment Recommendation Engine
"""

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

# Load recommender ONCE at startup
recommender = SHLRecommender(top_k=10)


# -------- Request / Response Models --------
class RecommendRequest(BaseModel):
    query: str


class Assessment(BaseModel):
    name: str
    url: str


class RecommendResponse(BaseModel):
    recommendations: List[Assessment]


# -------- Routes --------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    results = recommender.recommend(req.query)

    return {"recommendations": results}
