<content>from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models
from .schemas import ( # 스키마 파일 가정
    RoadmapPlanCreate, RoadmapPlanRead, QA_SessionCreate, QA_SessionRead, TrustScoreRequest
)
from .database import get_db

# FastAPI 인스턴스 초기화
app = FastAPI(title="Trust Score API")

# --------------------------------------------------
# 핵심 로직: 맞춤형 로드맵 생성 및 Trust Score 연동
# --------------------------------------------------

@app.post("/roadmap/generate", response_model=RoadmapPlanRead)
def generate_roadmap(plan_data: RoadmapPlanCreate, db: Session = Depends(get_db)):
    """
    사용자 요청에 따라 맞춤형 로드맵을 생성하고 Trust Score를 초기화합니다.
    """
    # 1. Trust Score 계산 (가정: 실제 로직은 복잡하므로 여기서는 임시값 및 모델 연동)
    initial_score = plan_data.trust_score if plan_data.trust_score is not None else 0.5 # 예시 로직
    
    # 2. 데이터베이스에 계획 저장 (Trust Score 포함)
    db_plan = models.RoadmapPlan(
        user_id=plan_data.user_id,
        plan_title=plan_data.plan_title,
        content=plan_data.content,
        trust_score=initial_score # Trust Score 저장
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)

    # 3. QA 세션 기록 (사용자 피드백을 위한 준비)
    qa_session = models.QA_Session(
        roadmap_plan_id=db_plan.id,
        session_details=f"Initial Request for: {plan_data.plan_title}",
        result="Awaiting User Feedback"
    )
    db.add(qa_session)
    db.commit()
    
    return db_plan

@app.get("/roadmap/{plan_id}", response_model=RoadmapPlanRead)
def get_roadmap(plan_id: int, db: Session = Depends(get_db)):
    """
    특정 로드맵 계획을 조회합니다.
    """
    plan = db.query(models.RoadmapPlan).filter(models.RoadmapPlan.id == plan_id).first()
    if plan is None:
        raise HTTPException(status_code=404, detail="Roadmap plan not found")
    return plan

# TODO: AI Q&A 기능은 별도의 LLM 호출 로직을 추가해야 함 (향후 확장)