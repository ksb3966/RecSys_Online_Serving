import os
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from loguru import logger

import torch
import pandas as pd
from sqlmodel import Session, select

from model import ModelOptions
from config import config
from trainer import Trainer
from database import PredictionResult, engine
from utils import save_time

import warnings
warnings.filterwarnings('ignore')


router = APIRouter()

model_path = os.environ.get("MODEL_PATH")
data_path = os.environ.get("DATA_PATH")


class PredictionResponse(BaseModel):
    user_id: int
    isbn: str
    rating: float


# 여러 모델에 대한 옵션, 학습 옵션을 추가해 볼 수 있습니다
# DeepCoNN 은 첫 실행 시 vector_create True 설정 필요
# 요청 예시: 0.0.0.0:8000/scoring/context?model_type=wdn
@router.get("/scoring/context")
def predict(model_type: str = "FM") -> PredictionResponse:
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model_name = model_type.lower()

    logger.info("Model Loading...")
    
    model_path = config.model_path
    data_path = config.data_path
    
    
    model_options = ModelOptions(model_name, data_path, model_path, device)
    
    model_saved_file = str(model_path) + f"/{str(model_type)}_model.pt"
    
    logger.info(data_path)
    logger.info(model_saved_file)
    
    
    if data_path is None:
        raise ValueError("DATA_PATH is not defined.")
        
    try:    
        if (model_name == "deepconn"):
            embeddings = model_options.get_embedding(vector_create=True)
        else:
            embeddings = model_options.get_embedding()
                
        model_options.load_model(embeddings = embeddings)
        model = model_options.get_model()
        trainer = model_options.get_trainer(model)
                
        # 모델의 SaveFile(.pt)이 있을 경우 Train 생략
        if os.path.exists(model_saved_file) == False:
            logger.info("Model saved file not existed, Start Training")
            # 모델 학습
            trainer.train(embeddings)    
            
        # 모델 Inference
        prediction = trainer.test(embeddings)        
        
        # 전체 Inference 결과 csv로 내보냄            
        submission = pd.read_csv(data_path + 'submit/sample_submission.csv')
        submission['rating'] = prediction
        submission.to_csv(data_path + f'submit/{model_type}_{save_time()}.csv', index=False)
        # print(submission)

        prediction_result = PredictionResult(user_id = submission.user_id, 
                                            isbn = submission.isbn,
                                            rating = prediction)
        logger.info("prediction done!")

        with Session(engine) as session:
            statement = select(PredictionResult)
            prediction_results = session.exec(statement).all()

        logger.info("DB Save Done!")


        response = PredictionResponse(user_id=int(submission.iloc[0]['user_id']),
                                        isbn=submission.iloc[0]['isbn'],
                                        rating=float(submission.iloc[0]['rating']))
    
    except RuntimeError:
        raise HTTPException(status_code=500, detail="Model is not initialized")
    except ValueError:
        raise HTTPException(status_code=400, detail="Input is not valid")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {e}")

    
    return response
    