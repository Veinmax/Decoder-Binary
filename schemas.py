from pydantic import BaseModel


class TestResultUpdate(BaseModel):
    test_name: str
    test_value: float
    pass_fail: int


class UpdateData(BaseModel):
    temperature: float
    test_results: list[TestResultUpdate]
