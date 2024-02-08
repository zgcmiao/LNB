# -*- coding: utf-8 -*-
import sys
from conf import Conf, ModelType, TransformersLocalRemoteType
from utils import pipeline_logger

support_local_transformers_scope = [
    ModelType.LLAMA,
    ModelType.LLAMA2
]


def transformers_factory(model_type: ModelType,
                         local_or_remote: TransformersLocalRemoteType = TransformersLocalRemoteType.REMOTE):
    if local_or_remote == TransformersLocalRemoteType.LOCAL and model_type in support_local_transformers_scope:
        from src import LOCAL_TRANSFORMERS_PATH
        sys.path.insert(1, str(Conf.BASE_PATH / LOCAL_TRANSFORMERS_PATH))
        from src import transformers_local_ as transformers
        pipeline_logger.info(f"transformers are using the `local` version. version is {transformers.__version__}")
        return transformers

    import transformers as transformers
    pipeline_logger.info(f"transformers are using the `remote` version. version is {transformers.__version__}")
    return transformers
