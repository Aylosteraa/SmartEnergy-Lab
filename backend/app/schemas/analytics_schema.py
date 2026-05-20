from pydantic import BaseModel


class AnalyticsPoint(BaseModel):

    label: str

    value: float


class AnalyticsStats(BaseModel):

    avg: float

    min: float

    max: float


class AnalyticsResponse(BaseModel):

    chart: list[AnalyticsPoint]

    stats: AnalyticsStats