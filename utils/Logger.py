import logging

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False  # 1. 切断向上传播
    if not logger.handlers:  # 2. 防止重复
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d  %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)  # 3. 按需改级别

    return logger

# 使用
# log = get_logger(__name__)
# log.warning('something happened')