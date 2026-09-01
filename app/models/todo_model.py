from sqlalchemy import Column, Integer, String, Boolean,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column,relationship
from app.database.connection import Base



class Todo(Base):
    __tablename__ = "todos"
    # id = Column(Integer, primary_key=True, index=True)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(100), nullable=True)
    complete: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"),index=True, nullable=False)

    user: Mapped["User"] = relationship(back_populates="todos")

