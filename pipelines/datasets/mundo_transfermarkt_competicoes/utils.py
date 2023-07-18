# -*- coding: utf-8 -*-
"""
General purpose functions for the mundo_transfermarkt_competicoes project
"""

###############################################################################

# Esse é um arquivo onde podem ser declaratas funções que serão usadas
# pelo projeto mundo_transfermarkt_competicoes.
#
# Por ser um arquivo opcional, pode ser removido sem prejuízo ao funcionamento
# do projeto, caos não esteja em uso.
#
# Para declarar funções, basta fazer em código Python comum, como abaixo:
#
# ```
# def foo():
#     """
#     Function foo
#     """
#     print("foo")
# ```
#
# Para usá-las, basta fazer conforme o exemplo abaixo:
#
# ```py
# from pipelines.datasets.mundo_transfermarkt_competicoes.utils import foo
# foo()
# ```
#
###############################################################################
import re
from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd
import asyncio
from pipelines.datasets.mundo_transfermarkt_competicoes.constants import (
    constants as mundo_constants,
)
from pipelines.utils.utils import log
from pipelines.datasets.mundo_transfermarkt_competicoes.decorators import retry


@retry
def get_content(link_soup):
    content = link_soup.find("div", id="main")
    return content


def process_basico(df, content):
    """
    Process data
    """
    # armazenar as informações extraídas do conteúdo HTML.
    # Cada chave do dicionário representa um atributo e seu valor corresponde ao valor extraído do HTML.
    new_content = {
        # Extrai o nome do estádio do HTML
        "estadio": content.find_all("td", attrs={"class": "hauptlink"})[0].get_text(),
        # Extrai a data do HTML.
        # Usa expressões regulares para procurar um padrão de data (no formato dd/mm/aaaa) no texto do link que corresponda ao padrão.
        "data": re.search(
            re.compile(r"\d+/\d+/\d+"),
            content.find("a", text=re.compile(r"\d+/\d+/\d")).get_text().strip(),
        ).group(0),
        # Extrai o horário do HTML.
        "horario": content.find_all("p", attrs={"class": "sb-datum hide-for-small"})[0]
        .get_text()
        .split()[6],
        # Extrai o número da rodada do HTML
        "rodada": re.search(
            re.compile(r"\d+. Matchday"),
            content.find("a", text=re.compile(r"\d.")).get_text().strip(),
        )
        .group(0)
        .split(".", 1)[0],
        # Extrai o número de público do HTML.
        # Procura por todas as tags <td> e obtém o texto da 12ª ocorrência (índice 11).
        "publico": content.find_all("td")[11].get_text(),
        # Extrai o número máximo de público do HTML.
        "publico_max": content.find_all("table", attrs={"class": "profilheader"})[0]
        .find_all("td")[2]
        .get_text(),
        # Extrai o nome do árbitro do HTML.
        "arbitro": re.search(
            r"Referee: [\w\s?]+", content.find_all("p")[2].get_text().strip()
        )
        .group(0)
        .split(": ", 1)[1],
        "hthg": content.find_all("div", attrs={"class": "sb-halbzeit"})[0]
        .get_text()
        .split(":", 1)[0],
        "htag": content.find_all("div", attrs={"class": "sb-halbzeit"})[0]
        .get_text()
        .split(":", 1)[1],
        "hs": None,
        "as": None,
        "hsofft": None,
        "asofft": None,
        "hdef": None,
        "adef": None,
        "hf": None,
        "af": None,
        "hc": None,
        "ac": None,
        "himp": None,
        "aimp": None,
        "hfk": None,
        "afk": None,
    }

    df = df.append(new_content, ignore_index=True)
    return df


def process(df, content):
    """
    Process complete
    """
    new_content = {
        "estadio": content.find_all("td", attrs={"class": "hauptlink"})[0].get_text(),
        "data": re.search(
            re.compile(r"\d+/\d+/\d+"),
            content.find("a", text=re.compile(r"\d+/\d+/\d")).get_text().strip(),
        ).group(0),
        "horario": content.find_all("p", attrs={"class": "sb-datum hide-for-small"})[0]
        .get_text()
        .split()[6],
        "rodada": re.search(
            re.compile(r"\d+. Matchday"),
            content.find("a", text=re.compile(r"\d.")).get_text().strip(),
        )
        .group(0)
        .split(".", 1)[0],
        "publico": content.find_all("td")[11].get_text(),
        "publico_max": content.find_all("table", attrs={"class": "profilheader"})[0]
        .find_all("td")[2]
        .get_text(),
        "arbitro": re.search(
            r"Referee: [\w\s?]+", content.find_all("p")[2].get_text().strip()
        )
        .group(0)
        .split(": ", 1)[1],
        "hthg": content.find_all("div", attrs={"class": "sb-halbzeit"})[0]
        .get_text()
        .split(":", 1)[0],
        "htag": content.find_all("div", attrs={"class": "sb-halbzeit"})[0]
        .get_text()
        .split(":", 1)[1],
        "hs": content.find_all("div", attrs={"class": "sb-statistik-zahl"})[
            0
        ].get_text(),
        "as": content.find_all("div", attrs={"class": "sb-statistik-zahl"})[
            1
        ].get_text(),
        "hsofft": content.find_all("div", attrs={"class": "sb-statistik-zahl"})[
            2
        ].get_text(),
        "asofft": content.find_all("div", attrs={"class": "sb-statistik-zahl"})[
            3
        ].get_text(),
        "hdef": content.find_all("div", attrs={"class": "sb-statistik-zahl"})[
            4
        ].get_text(),
        "adef": content.find_all("div", attrs={"class": "sb-statistik-zahl"})[
            5
        ].get_text(),
        "hf": content.find_all("div", attrs={"class": "sb-statistik-zahl"})[
            10
        ].get_text(),
        "af": content.find_all("div", attrs={"class": "sb-statistik-zahl"})[
            11
        ].get_text(),
        "hc": content.find_all("div", attrs={"class": "sb-statistik-zahl"})[
            6
        ].get_text(),
        "ac": content.find_all("div", attrs={"class": "sb-statistik-zahl"})[
            7
        ].get_text(),
        "himp": content.find_all("div", attrs={"class": "sb-statistik-zahl"})[
            12
        ].get_text(),
        "aimp": content.find_all("div", attrs={"class": "sb-statistik-zahl"})[
            13
        ].get_text(),
        "hfk": content.find_all("div", attrs={"class": "sb-statistik-zahl"})[
            8
        ].get_text(),
        "afk": content.find_all("div", attrs={"class": "sb-statistik-zahl"})[
            9
        ].get_text(),
    }

    df = df.append(new_content, ignore_index=True)
    return df


def pegar_valor(df, content):
    """
    Get value
    """
    # gera um dicionário
    valor_content = {
        "valor_equipe_titular_man": content.find_all("div", class_="table-footer")[0]
        .find_all("td")[3]
        .get_text()
        .split("€", 1)[1],
        "valor_equipe_titular_vis": content.find_all("div", class_="table-footer")[1]
        .find_all("td")[3]
        .get_text()
        .split("€", 1)[1],
        "idade_media_titular_man": content.find_all("div", class_="table-footer")[0]
        .find_all("td")[1]
        .get_text()
        .split(":", 1)[1],
        "idade_media_titular_vis": content.find_all("div", class_="table-footer")[1]
        .find_all("td")[1]
        .get_text()
        .split(":", 1)[1],
        "tecnico_man": content.find_all("a", attrs={"id": "0"})[1].get_text(),
        "tecnico_vis": content.find_all("a", attrs={"id": "0"})[3].get_text(),
    }
    df = df.append(valor_content, ignore_index=True)
    return df


def pegar_valor_sem_tecnico(df, content):
    """
    Get value without technical
    """
    valor_content = {
        "valor_equipe_titular_man": content.find_all("div", class_="table-footer")[0]
        .find_all("td")[3]
        .get_text()
        .split("€", 1)[1],
        "valor_equipe_titular_vis": content.find_all("div", class_="table-footer")[1]
        .find_all("td")[3]
        .get_text()
        .split("€", 1)[1],
        "idade_media_titular_man": content.find_all("div", class_="table-footer")[0]
        .find_all("td")[1]
        .get_text()
        .split(":", 1)[1],
        "idade_media_titular_vis": content.find_all("div", class_="table-footer")[1]
        .find_all("td")[1]
        .get_text()
        .split(":", 1)[1],
        "tecnico_man": None,
        "tecnico_vis": None,
    }
    df = df.append(valor_content, ignore_index=True)
    return df


def valor_vazio(df):
    """
    Return a temmplate DataFrame
    """
    valor_content = {
        "valor_equipe_titular_man": None,
        "valor_equipe_titular_vis": None,
        "idade_media_titular_man": None,
        "idade_media_titular_vis": None,
        "tecnico_man": None,
        "tecnico_vis": None,
    }
    df = df.append(valor_content, ignore_index=True)
    return df


def vazio(df):
    """
    Return a template DataFrame
    """
    null_content = {
        "estadio": None,
        "data": None,
        "horario": None,
        "rodada": None,
        "publico": None,
        "publico_max": None,
        "arbitro": None,
        "hthg": None,
        "htag": None,
        "hs": None,
        "as": None,
        "hsofft": None,
        "asofft": None,
        "hdef": None,
        "adef": None,
        "hf": None,
        "af": None,
        "hc": None,
        "ac": None,
        "himp": None,
        "aimp": None,
        "hfk": None,
        "afk": None,
    }
    df = df.append(null_content, ignore_index=True)
    return df


async def execucao_coleta():
    """
    Execute the program
    """
    # Armazena informações do site em um único dataframe.
    base_url = "https://www.transfermarkt.com/campeonato-brasileiro-serie-a/gesamtspielplan/wettbewerb/BRA1?saison_id={season}&spieltagVon=1&spieltagBis=38"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
    }
    base_link = "https://www.transfermarkt.com"
    links = []

    ht_tag = []
    at_tag = []
    result_tag = []

    ht = []
    at = []
    fthg = []
    ftag = []
    col_home = []
    col_away = []

    # expressão regular para encontrar o número de gols marcados pelo time da casa
    pattern_fthg = re.compile(r"\d:")
    # expressão regular para encontrar o número de gols marcados pelo time visitante
    pattern_ftag = re.compile(r":\d")

    # para armazenar os dados das partidas
    df = pd.DataFrame(
        {"ht": [], "at": [], "fthg": [], "ftag": [], "col_home": [], "col_away": []}
    )
    df_valor = pd.DataFrame({})

    # season = data_atual.year - 1
    season = mundo_constants.SEASON.value
    # Pegar o link das partidas
    # Para cada temporada, adiciona os links dos jogos em `links`
    log(f"Obtendo links: temporada {season}")
    site_data = requests.get(base_url.format(season=season), headers=headers)
    soup = BeautifulSoup(site_data.content, "html.parser")
    link_tags = soup.find_all("a", attrs={"class": "ergebnis-link"})
    for tag in link_tags:
        links.append(re.sub(r"\s", "", tag["href"]))
    if len(links) % 10 != 0:
        num_excess = len(links) % 10
        del links[-num_excess:]
    tabela = soup.findAll("div", class_="box")
    for i in range(1, int(len(links) / 10) + 1):
        for row in tabela[i].findAll("tr"):  # para tudo que estiver em <tr>
            cells = row.findAll("td")  # variável para encontrar <td>
            if len(cells) == 7:
                ht_tag.append(cells[2].findAll(text=True))  # iterando sobre cada linha
                result_tag.append(
                    cells[4].findAll(text=True)
                )  # iterando sobre cada linha
                at_tag.append(cells[6].findAll(text=True))  # iterando sobre cada linha

    for time in range(len(links)):
        ht.append(str(ht_tag[time][2]))
        col_home.append(str(ht_tag[time][0]))
    for time in range(len(links)):
        at.append(str(at_tag[time][0]))
        col_away.append(str(at_tag[time][2]))
    for tag in result_tag:
        fthg.append(str(pattern_fthg.findall(str(tag))))
        ftag.append(str(pattern_ftag.findall(str(tag))))

    # links das estatísticas
    links_esta = []
    # links das escalações de cada partida
    links_valor = []

    for link in links:
        esta = link.replace("index", "statistik")
        links_esta.append(esta)
    for link in links:
        valor = link.replace("index", "aufstellung")
        links_valor.append(valor)

    n_links = len(links)
    log(f"Encontrados {n_links} partidas.")
    log("Extraindo dados...")
    for n, link in enumerate(links_esta):
        # Tentativas de obter os links
        content = await get_content(base_link + link)
        if content:
            try:
                df = process(df, content)
            except Exception:
                try:
                    df = process_basico(df, content)
                except Exception:
                    df = vazio(df)
        else:
            df = vazio(df)
        log(f"{n+1} dados de {n_links} extraídos.")
    for n, link in enumerate(links_valor):
        # Tentativas de obter os links
        content = await get_content(base_link + link)
        if content:
            try:
                df_valor = pegar_valor(df_valor, content)
            except Exception:
                try:
                    df_valor = pegar_valor_sem_tecnico(df_valor, content)
                except Exception:
                    df_valor = valor_vazio(df_valor)
        else:
            df_valor = valor_vazio(df_valor)
        log(f"{n+1} valores de {n_links} extraídos.")

    df["ht"] = ht
    df["at"] = at
    df["fthg"] = fthg
    df["ftag"] = ftag
    df["col_home"] = col_home
    df["col_away"] = col_away

    # limpar variaveis
    df["fthg"] = df["fthg"].map(lambda x: x.replace("['", ""))
    df["fthg"] = df["fthg"].map(lambda x: x.replace(":']", ""))

    df["ftag"] = df["ftag"].map(lambda x: x.replace("[':", ""))
    df["ftag"] = df["ftag"].map(lambda x: x.replace("']", ""))

    df["col_home"] = df["col_home"].map(lambda x: x.replace("(", ""))
    df["col_home"] = df["col_home"].map(lambda x: x.replace(".)", ""))

    df["col_away"] = df["col_away"].map(lambda x: x.replace("(", ""))
    df["col_away"] = df["col_away"].map(lambda x: x.replace(".)", ""))

    df["htag"] = df["htag"].map(lambda x: str(x).replace(")", ""))
    df["hthg"] = df["hthg"].map(lambda x: str(x).replace("(", ""))

    df_valor["idade_media_titular_vis"] = df_valor["idade_media_titular_vis"].map(
        lambda x: str(x).replace(" ", "")
    )
    df_valor["idade_media_titular_man"] = df_valor["idade_media_titular_man"].map(
        lambda x: str(x).replace(" ", "")
    )

    df_valor["valor_equipe_titular_man"] = df_valor["valor_equipe_titular_man"].map(
        lambda x: str(x).replace("m", "0000")
    )
    df_valor["valor_equipe_titular_man"] = df_valor["valor_equipe_titular_man"].map(
        lambda x: str(x).replace("Th.", "000")
    )
    df_valor["valor_equipe_titular_man"] = df_valor["valor_equipe_titular_man"].map(
        lambda x: str(x).replace(".", "")
    )

    df_valor["valor_equipe_titular_vis"] = df_valor["valor_equipe_titular_vis"].map(
        lambda x: str(x).replace("m", "0000")
    )
    df_valor["valor_equipe_titular_vis"] = df_valor["valor_equipe_titular_vis"].map(
        lambda x: str(x).replace("Th.", "000")
    )
    df_valor["valor_equipe_titular_vis"] = df_valor["valor_equipe_titular_vis"].map(
        lambda x: str(x).replace(".", "")
    )

    df["publico_max"] = df["publico_max"].map(lambda x: str(x).replace(".", ""))
    df["publico"] = df["publico"].map(lambda x: str(x).replace(".", ""))

    df["test"] = df["publico_max"].replace(to_replace=r"\d", value=1, regex=True)

    def sem_info(x, y):
        if x == 1:
            return y
        return None

    df["test2"] = df.apply(lambda x: sem_info(x["test"], x["publico_max"]), axis=1)
    df["publico_max"] = df["test2"]
    del df["test2"]
    del df["test"]

    df["data"] = pd.to_datetime(df["data"]).dt.date
    df["horario"] = pd.to_datetime(df["horario"]).dt.strftime("%H:%M")

    df.fillna("", inplace=True)

    df["rodada"] = df["rodada"].astype(np.int64)

    # renomear colunas
    df = df.rename(
        columns={
            "ht": "time_man",
            "at": "time_vis",
            "fthg": "gols_man",
            "ftag": "gols_vis",
            "col_home": "colocacao_man",
            "col_away": "colocacao_vis",
            "ac": "escanteios_vis",
            "hc": "escanteios_man",
            "adef": "defesas_vis",
            "hdef": "defesas_man",
            "af": "faltas_vis",
            "afk": "chutes_bola_parada_vis",
            "aimp": "impedimentos_vis",
            "as": "chutes_vis",
            "asofft": "chutes_fora_vis",
            "hf": "faltas_man",
            "hfk": "chutes_bola_parada_man",
            "himp": "impedimentos_man",
            "hs": "chutes_man",
            "hsofft": "chutes_fora_man",
            "htag": "gols_1_tempo_vis",
            "hthg": "gols_1_tempo_man",
        }
    )

    df = pd.concat([df, df_valor], axis=1)

    df["data"] = pd.to_datetime(df["data"])
    df["ano_campeonato"] = mundo_constants.DATA_ATUAL_ANO.value

    df = df[mundo_constants.ORDEM_COLUNA_FINAL.value]

    return df