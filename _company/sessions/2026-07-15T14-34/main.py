from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import time
# models.py에서 TrustScore 관련 로직과 모델을 임포트한다고 가정합니다.
from . import models 

app = FastAPI(title="Trust Score Gauge API")

# Pydantic 스키마 정의 (입력 및 출력)
class RoadmapRequest(BaseModel):
    user_input: str  # 사용자의 목표/현재 상황 입력
    wtp_score: float # WTP 기반 점수 입력 (Pro Tier 관련)

class RoadmapResponse(BaseModel):
    roadmap_id: int
    status: str
    result_data: Dict
    trust_score_update: float

@app.post("/generate", response_model=RoadmapResponse)
async def generate_roadmap(request: RoadmapRequest):
    """
    사용자 입력과 WTP 점수를 기반으로 맞춤형 로드맵을 생성하고 Trust Score를 업데이트합니다.
    """
    try:
        # 1. Trust Score 계산 (핵심 로직 연동)
        trust_score = models.calculate_trust_score(request.user_input, request.wtp_score)

        # 2. 로드맵 데이터 생성 (가정된 로직)
        roadmap_id = int(time.time() * 1000) # 임시 ID 생성
        result_data = {
            "roadmap_id": roadmap_id,
            "steps": [f"Step 1: Based on WTP score of {request.wtp_score} and input '{request.user_input}'"],
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # 3. DB 저장 (가정된 로직)
        models.save_roadmap(roadmap_id, request.user_input, trust_score)

        return RoadmapResponse(
            roadmap_id=roadmap_id,
            status="SUCCESS",
            result_data=result_data,
            trust_score_update=trust_score
        )
    except Exception as e:
        print(f"Error during roadmap generation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/roadmap/{id}", response_model=Dict)
async def get_roadmap(id: int):
    """
    특정 ID의 로드맵 정보를 조회합니다.
    """
    # DB에서 로드맵 정보 조회 (가정된 로직)
    try:
        roadmap = models.get_roadmap_by_id(id)
        if not roadmap:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        return {"message": "Roadmap retrieved successfully", "data": roadmap}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving roadmap: {str(e)}")

print("FastAPI application initialized.")