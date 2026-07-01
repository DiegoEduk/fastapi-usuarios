from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.security import get_current_user
from modules.users.user_schema import UserCreate, UserResponse, UserResponseSmall, UserUpdate
from modules.users.user_service import UserService

router = APIRouter(prefix="/users", tags=["Usuarios"])

@router.get("/all-users", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def read_users(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    rol_name = current_user["role_name"]
    if current_user["role_name"] != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Acceso denegado. Rol {rol_name} insuficiente.")
    
    service = UserService(db)
    return await service.get_all_users()

@router.post("/create-user", response_model=UserResponseSmall, status_code=status.HTTP_201_CREATED)
async def add_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role_name"] != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado. Rol insuficiente.")
    
    service = UserService(db)
    return await service.create_user(user_in)

@router.put("/actualizar/{user_id}", response_model=UserResponseSmall, status_code=status.HTTP_200_OK)
async def update_existing_user(
    user_id: int, 
    user_data: UserUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    """
    Endpoint Protegido por Token y RBAC:
    - Admin: Modifica a cualquier usuario sin restricciones.
    - Aprendiz: Solo puede modificarse a sí mismo (restringido en capa de servicios).
    """
    # REGLA 1: Un 'Aprendiz' solo puede editarse a sí mismo
    if current_user["role_name"] != "Administrador" and current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Permiso denegado. No tienes autorización para modificar datos de otros usuarios."
        )
    
    service = UserService(db)
    return await service.update_user(user_id, user_data, current_user)