from datetime import timedelta, datetime

from decouple import config
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
# noinspection PyPackageRequirements
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.server.database.models import User
from src.server.models.sessions import SignIn, SignUp, SignInOut, TokenData
from src.server.repositories.users import get_user_by_email, add_user

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(config('ACCESS_TOKEN_EXPIRE_MINUTES'))


def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + access_token_expires
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        if email is None or user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id, email=email)

    except JWTError:
        raise credentials_exception

    user = get_user_by_email(token_data.email)

    if user is None:
        raise credentials_exception

    return user


@router.post("/signup", response_model=SignInOut, status_code=status.HTTP_201_CREATED, summary="sign-up of a new user")
def signup(sign_up_data: SignUp):
    db_user = get_user_by_email(sign_up_data.email)

    if db_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    new_user = User(
        user_name=sign_up_data.user_name,
        email=sign_up_data.email,
        password=get_password_hash(sign_up_data.password),
    )
    add_user(new_user)
    access_token = create_access_token(data={"user_id": new_user.id, "email": new_user.email})
    sign_up_response = SignInOut(access_token=access_token, user_id=new_user.id)

    return sign_up_response


@router.post("/login", response_model=SignInOut, status_code=status.HTTP_200_OK, summary="sign-in for existing users")
def login(sign_in_data: SignIn):
    user = authenticate_user(sign_in_data.email, sign_in_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"user_id": user.id, "email": user.email})
    return SignInOut(access_token=access_token, user_id=user.id)
