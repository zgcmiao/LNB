from flask_apscheduler import APScheduler
from opensearchpy import OpenSearch
scheduler = APScheduler()


def get_opensearch_client():
    from src.dms.app import get_runtime_env
    env = get_runtime_env()
    if env == 'dev':
        from src.dms.config.dev_config import OPENSEARCH_HOST, OPENSEARCH_PORT, OPENSEARCH_USER, OPENSEARCH_PASSWORD
    else:
        from src.dms.config.prod_config import OPENSEARCH_HOST, OPENSEARCH_PORT, OPENSEARCH_USER, OPENSEARCH_PASSWORD

    opensearch_client = OpenSearch(
        hosts=[{'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}],
        http_compress=True,  # enables gzip compression for request bodies
        http_auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD),
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False
    )
    return opensearch_client
