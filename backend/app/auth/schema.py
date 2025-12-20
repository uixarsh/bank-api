from enum import Enum
import uuid
from sqlmodel import SQLModel, Field
from pydantic import EmailStr, field_validator
from fastapi import HTTPException, status

class SecurityQuestionsSchema(str, Enum):
    MOTHERS_MAIDEN_NAME = "mothers_maiden_name"
    FIRST_PET_NAME = "first_pet_name"
    FAVORITE_TEACHER = "favorite_teacher"
    BIRTH_CITY = "birth_city"
    FAVORITE_BOOK = "favorite_book"

    @classmethod
    def get_description(cls, value : "SecurityQuestionsSchema") -> str:
        descriptions = {
            cls.MOTHERS_MAIDEN_NAME: "What is your mother's maiden name?",
            cls.FIRST_PET_NAME: "What was the name of your first pet?",
            cls.FAVORITE_TEACHER: "Who was your favorite teacher?",
            cls.BIRTH_CITY: "In which city were you born?",
            cls.FAVORITE_BOOK: "What is your favorite book?",
        }
        return descriptions.get(value, "Unknown security question")
    

class AccountStatusSchema(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    PENDING = "pending"


class RoleChoicesSchema(str, Enum):
    CUSTOMER = "customer"
    ACCOUNT_EXECUTIVE = "account_executive"
    BRANCH_MANAGER = "branch_manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    TELLER = "teller"

class BaseUserSchema(SQLModel):
    username: str | None = Field(default=None, max_length=50, unique=True)
    email: EmailStr | None = Field(default=None, unique=True, index=True)
    first_name: str | None = Field(max_length=30)
    middle_name: str | None = Field(default=None, max_length=30)
    last_name: str | None = Field(max_length=30)
    id_no: int = Field(unique=True, gt=0)   # gt => greater than or equal to 0
    is_active: bool = False
    is_superuser: bool = False
    securtiy_question: SecurityQuestionsSchema = Field(max_length=30)
    security_answer: str = Field(max_length=30)
    account_status: AccountStatusSchema = Field(default=AccountStatusSchema.INACTIVE)
    role: RoleChoicesSchema = Field(default=RoleChoicesSchema.CUSTOMER)

class UserCreateSchema(BaseUserSchema):
    password: str = Field(min_length=8, max_length=40)
    confirm_password: str = Field(min_length=8, max_length=40)

    @field_validator("confirm_password")
    def validate_confirm_password(cls, v, values):  # v: value of confirm_password, values: dict of other field values
        if "password" in values.data and v != values.data["password"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "error",
                    "message": "Password and confirm password do not match.",
                    "action": "Please re-enter matching passwords."
                }
            )
        return v
    
class UserReadSchema(BaseUserSchema):
    id: uuid.UUID
    full_name: str

class EmailRequestSchema(SQLModel):
    email: EmailStr

class LoginRequestSchema(SQLModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=40)

class OTPVerifyRequestSchema(SQLModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6)