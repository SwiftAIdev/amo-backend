from pydantic import BaseModel
from typing import List, Optional, Dict


class DataItemModel(BaseModel):
    hash_id: str
    user_ids: List[int]
    activity_statuses: Dict[str, List[int]]
    custom_questions: Optional[List[str]]
    criterion_questions: Optional[List[str]]
    destination_user_id: int
    recipient_user_ids: Optional[List[int]]


class ClientRegisterModel(BaseModel):
    account_id: int
    data: List[DataItemModel]
    current_user_id: int
