from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from modules.roles.role_schema import RoleCreate
from core.logger import logger

class RoleService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all_roles(self) -> list[dict]:
        logger.info("SQL Nativo: Consultando todos los roles.")
        query = text("SELECT id, name, description FROM roles ORDER BY id ASC;")
        result = await self.db.execute(query)
        return [dict(row) for row in result.mappings().all()]
    
    async def get_role_by_name(self, el_nombre: str) -> list[dict]:
        logger.info("SQL Nativo: Consultar un rol por su nombre.")
        query = text("SELECT id, name, description FROM roles WHERE name LIKE :nombre;")
        el_nombre = f"%{el_nombre}%"
        result = await self.db.execute(query, {"nombre": el_nombre})
        return [dict(row) for row in result.mappings().all()]
    
    async def get_role_by_id(self, el_id: int) -> dict:
        logger.info("SQL Nativo: Consultar un rol por su id.")
        query = text("SELECT id, name, description FROM roles WHERE id = :identificacion;")
        result = await self.db.execute(query, {"identificacion": el_id})
        return dict(result.mappings().first())

    async def create_role(self, role_data: RoleCreate) -> dict:
        logger.info(f"SQL Nativo: Insertando rol {role_data.name}")
        
        check = await self.db.execute(text("SELECT id FROM roles WHERE name = :name;"), {"name": role_data.name})
        if check.first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El rol ya existe.")

        query = text("INSERT INTO roles (name, description) VALUES (:name, :description) RETURNING id, name, description;")
        try:
            result = await self.db.execute(query, {"name": role_data.name, "description": role_data.description})
            await self.db.commit()
            return dict(result.mappings().first())
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error al insertar rol: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor.")

    async def delete_role_by_id(self, el_id: int) -> dict:
        logger.info("SQL Nativo: Eliminar un rol por su id.")
        query_check = text("SELECT id FROM roles WHERE id = :identificacion;")
        check = await self.db.execute(query_check, {"identificacion": el_id})
        if not check.first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El rol no existe.")
        query=text("DELETE FROM roles WHERE id = :identy;")
        try:
            await self.db.execute(query, {"identy": el_id})
            await self.db.commit()
            return {"message":f"role {el_id} eliminado con exito."}
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error al eliminar rol: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor.")


