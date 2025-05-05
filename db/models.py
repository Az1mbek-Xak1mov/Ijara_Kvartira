from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import BIGINT, String, Text, Integer, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.engine import Base


class Apartment(Base):
    __tablename__ = "apartments"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("owners.chat_id", ondelete="CASCADE"))
    district: Mapped[str] = mapped_column(String(100))
    price: Mapped[int] = mapped_column(DECIMAL(10, 0))
    type: Mapped[str] = mapped_column(String(50))
    repair: Mapped[str] = mapped_column(String(50))
    images: Mapped[str] = mapped_column(Text)
    rooms: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    phone_number: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(50))
    floor: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())

    owner = relationship("Owner", back_populates="apartments", single_parent=True)




class Renter(Base):
    __tablename__ = "renters"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BIGINT)
    fullname: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())


class Owner(Base):
    __tablename__ = "owners"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BIGINT)
    fullname: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())

    # Apply cascade and delete-orphan on the "one" side (Owner)
    apartments = relationship("Apartment", back_populates="owner", cascade="all, delete-orphan")



class LikedListing(Base):
    __tablename__ = "liked_listings"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    renter_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("renters.chat_id", ondelete="CASCADE"))
    apartment_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("apartments.id", ondelete="CASCADE"))
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())


