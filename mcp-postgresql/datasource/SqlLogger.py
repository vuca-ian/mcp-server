import logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
def sql_print(query: str,params:dict):
    if not params:
        return 'None'
    
    formatted = []
    for idx, param in enumerate(params, 1):
        try:
            type_name = type(param).__name__
            if isinstance(param, str):
                value_repr = str(param)
            else:    
                value_repr = repr(param)
            
            # 处理特殊类型
            if isinstance(param, bytes):
                value_repr = f"<bytes len={len(param)}>"
            elif param is None:
                type_name = 'NoneType'
            if isinstance(param, str) and 'password' in query.lower():
                value_repr = '******' 
            formatted.append(f"{value_repr}({type_name})")
        except Exception as e:
            formatted.append(f"!!PARAM_ERROR[{e}]!!")
    logger.info("Executing query: \nSQL:\t  %s\nPARAMETES:%s", query,  ', '.join(formatted))