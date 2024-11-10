from typing import Optional

from sqlmodel import Field, SQLModel, create_engine


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tg_id: int = Field(description="ID пользователя в Telegram")
    tg_username: str = Field(description="Username пользователя в Telegram")
    tg_fullname: str = Field(description="Полное имя пользователя в Telegram")
    tg_is_user_admin: bool = Field(description="Уровень работы пользователя. True - ответ от нейронки", default=True)
    internal_room_id: int = Field(description="ID комнаты внутри системы")
    internal_username: str = Field(description="Username пользователя внутри системы")

# hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
# hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
# hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)

def create_db_engine(db_path:str):
    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)
    return engine


# with Session(engine) as session:
#     session.add(hero_1)
#     session.add(hero_2)
#     session.add(hero_3)
#     session.commit()
