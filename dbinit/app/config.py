import os

# Configuración de conexión a MySQL (sin contraseñas en texto plano)
DATABASE_CONFIG = {
    "HOST": os.getenv("MYSQL_HOST", "mysql"),
    "ROOT_USER": os.getenv("MYSQL_ROOT_USER", "root"),
    "DATABASE_NAME": os.getenv("MYSQL_DATABASE", "universidad"),
    "APP_USER": os.getenv("MYSQL_APP_USER", "app_user"),
    "PASSWORD": os.getenv("MYSQL_APP_PASSWORD"),
    "NombreTablaConexiones": os.getenv("MYSQL_TABLE_CONEXIONES", "conexiones"),
    "NombreTablaMovimientos": os.getenv("MYSQL_TABLE_MOVIMIENTOS", "movimientos")
}




