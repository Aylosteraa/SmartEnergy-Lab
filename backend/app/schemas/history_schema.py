from pydantic import BaseModel


class HistoryPoint(BaseModel):

    label: str

    value: float