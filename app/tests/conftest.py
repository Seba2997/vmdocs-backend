import pytest
from sqlalchemy.orm import configure_mappers

# Import all models to ensure mappers are initialized
from app.models.actividad_model import *
from app.models.caso_model import *
from app.models.caso_usuario_model import *
from app.models.cliente_model import *
from app.models.documento_model import *
from app.models.nota_caso_model import *
from app.models.notificacion_model import *
from app.models.password_reset import *
from app.models.usuario import *

configure_mappers()
