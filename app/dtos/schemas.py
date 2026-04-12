from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)

class OTPVerify(BaseModel):
    otp_code: str = Field(..., min_length=6, max_length=6)

class PatientProfileUpdate(BaseModel):
    age: Optional[int] = Field(None, ge=0, le=120)
    current_weight: Optional[float] = Field(None, ge=0)
    target_weight: Optional[float] = Field(None, ge=0)
    height: Optional[float] = Field(None, ge=0)
    gender: Optional[str] = None
    objective: Optional[str] = None
    activity_level: Optional[str] = None
    profession: Optional[str] = None
    ville: Optional[str] = None
    mode_de_vie: Optional[str] = None
    preference: Optional[str] = None
    liked_recipes: Optional[str] = None
    disliked_recipes: Optional[str] = None
    meals_per_day: Optional[int] = Field(None, ge=1, le=10)
    waist_size: Optional[float] = Field(None, ge=0)
    allergies: Optional[str] = None
    remarks: Optional[str] = None

class MealAssign(BaseModel):
    patient_id: int
    day_of_week: str
    meal_type: str
    title: str = Field(..., min_length=1)
    ingredients: str
    photo_url: Optional[str] = None
    calories: int = 0
    proteins: int = 0
    carbs: int = 0
    fats: int = 0

class MessageSend(BaseModel):
    receiver_id: int
    content: str = Field(..., min_length=1)
