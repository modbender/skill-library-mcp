from sqlalchemy import Column, String, DateTime, Text, Boolean
from openexec.db import Base
import datetime

class ExecutionLog(Base):
    __tablename__ = "execution_log"

    id = Column(String, primary_key=True)
    action = Column(String, nullable=False)
    payload = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    nonce = Column(String, unique=True, nullable=False)
    approved = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
