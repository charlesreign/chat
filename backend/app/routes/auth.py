from fastapi import APIRouter, HTTPException, status
from app.models.user import UserCreate, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

# In-memory user storage for demonstration
users_db = {}
user_id_counter = 1


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register a new user."""
    global user_id_counter
    
    # Check if user already exists
    for stored_user in users_db.values():
        if stored_user["username"] == user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        if stored_user["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    user_id = user_id_counter
    user_id_counter += 1
    
    users_db[user_id] = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "password": user.password,  # In production, hash this!
        "is_active": True,
        # "created_at": None
    }
    
    return users_db[user_id]


@router.post("/login")
async def login(username: str, password: str):
    """Login a user and return user data."""
    for user_id, user in users_db.items():
        if user["username"] == username and user["password"] == password:
            return {
                "user_id": user_id,
                "username": user["username"],
                "email": user["email"],
                "token": f"fake_token_{user_id}"  # In production, use JWT!
            }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )


@router.get("/users")
async def get_all_users():
    """Get all users."""
    return [
        {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "is_active": user["is_active"]
        }
        for user in users_db.values()
    ]
