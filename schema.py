from pydantic import BaseModel
from typing import List

class Patient(BaseModel):
    patientId: str
    notes: str

class PatientList(BaseModel):
    patients: List[Patient]