# -*- coding: utf-8 -*-
from enum import Enum
from datetime import datetime, timedelta


class constants(Enum):  # pylint: disable=c0103
    """
    Constant values for the br_b3_cotacoes project
    """

    data = datetime.now().strftime("%d-%m-%Y")
    B3_URL = f"https://arquivos.b3.com.br/apinegocios/tickercsv/{data}"
    B3_PATH_INPUT = "/tmp/input/br_b3_cotacoes"
    B3_PATH_OUTPUT_DF = f"/tmp/input/br_b3_cotacoes/{data}_NEGOCIOSAVISTA.txt"
    B3_PATH_OUTPUT = "/tmp/output/br_b3_cotacoes"