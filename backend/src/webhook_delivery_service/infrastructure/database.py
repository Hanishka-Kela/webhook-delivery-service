from webhook_delivery_service.infrastructure.config.settings import get_settings
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker
settings = get_settings()

engine = create_engine(settings.DATABASE_URL,pool_pre_ping=True)

sessionLocal = sessionmaker(bind=engine,autoflush=False,expire_on_commit=False)