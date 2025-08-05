from sqlalchemy import Column, Integer, String, Boolean, Numeric, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database.database_conn import Base  # Pastikan path sesuai

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)

    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)
    type = Column(String(10), nullable=False)  # 'income' atau 'expense'
    is_default = Column(Boolean, default=False)

    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    transaction_type = Column(Boolean, nullable=False)  # True: Income, False: Expense
    amount = Column(Numeric(15, 2), nullable=False)
    transaction_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
