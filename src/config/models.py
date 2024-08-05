from typing import List, Optional
from pydantic import BaseModel


class CallDataModel(BaseModel):
    domain: str
    call_id: str
    call_duration: str
    user_id: str
    activity_id: str
    activity_type: str
    activity_status: str

    class Config:
        from_attributes = True


class ClientRegisterModel(BaseModel):
    domain: str
    users: List[str]
    activity_statuses: List[str]
    custom_questions: List[str]
    criterion_questions: Optional[List[str]] = None
    destination_user_id: str
    recipient_users_id: Optional[List[str]] = None

    class Config:
        from_attributes = True


class ProcessedCallDataModel(BaseModel):
    domain: str
    call_id: str
    transcription: str
    summary: str

    class Config:
        from_attributes = True


class ProcessedGroupCallDataModel(BaseModel):
    domain: str
    user_id: str
    activity_id: str
    summary: str
    summary_type: str

    class Config:
        from_attributes = True
