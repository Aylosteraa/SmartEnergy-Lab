from typing import Optional

from pydantic import BaseModel


class SolarData(BaseModel):
    power: float


class BatteryData(BaseModel):
    soc: float
    power: float


class LoadData(BaseModel):
    load_power: float


class MeterData(BaseModel):
    grid_power: float


class TestRealtimeData(BaseModel):
    solar: SolarData
    battery: BatteryData
    load: LoadData
    meter: MeterData


class ForecastTestItem(BaseModel):
    time: str

    total_consumption: float

    solar_generation: float

    energy_balance: Optional[float] = None


class RecommendationTestRequest(BaseModel):
    realtime_data: TestRealtimeData

    forecast: Optional[list[ForecastTestItem]] = None