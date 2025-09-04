"""
包名称：endpoints
功能说明：API端点包，包含具体的业务接口实现
"""
from .personas import router as personas_router
from .tags import router as tags_router
from .authors import router as authors_router
from .auth import router as auth_router