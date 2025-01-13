# Esto asegura que la app de django esté cargada cuando Celery importe las tareas
default_app_config = 'core.apps.CoreConfig'

# No importamos las tareas aquí para evitar importaciones circulares
