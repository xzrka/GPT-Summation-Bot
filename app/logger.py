import logging


def makeLogger(save:bool = False, filename:str = "log.log"):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if save:
        file_handler = logging.FileHandler(f"{filename}.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger