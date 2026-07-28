from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database.base import Base


class Flag(Base):
    __tablename__ = "feature_flags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    key = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255))
    is_enabled = Column(Boolean, default=False)
    environment_id = Column(Integer, ForeignKey("environments.id"), nullable=True)
    default_value = Column(String(255), nullable=True)

    @property
    def enabled(self):
        return self.is_enabled

    @enabled.setter
    def enabled(self, value):
        self.is_enabled = value
