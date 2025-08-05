from prometheus_fastapi_instrumentator import Instrumentator

def setup_prometheus(app):
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=False,
        excluded_handlers=["/metrics"]
    )
    instrumentator.instrument(app).expose(app, include_in_schema=False)
