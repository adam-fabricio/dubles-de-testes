from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import HTTPError
from math import ceil
import logging
import os
import json

def consultar_livros(autor):
    dados = preparar_dados_para_requisicao(autor)
    url = obter_url("https://buscador", dados)
    ret = executar_requisicao(url)
    return ret


def preparar_dados_para_requisicao(autor):
    dados = {"autor": autor}
    return dados


def obter_url(url, dados):
    pass


def executar_requisicao(url):
    try:
        with urlopen(url, timeout=10) as resposta:
            resultado = resposta.read().decode()
    except HTTPError as e:
        logging.exception(f"Ao acessar {url}: {e}")
    else:
        return resultado


def escrever_em_arquivo(arquivo, conteudo):
    diretorio = os.path.dirname(arquivo)
    try:
        os.makedirs(diretorio)
    except OSError as e:
        logging.exception(f"Nao foi possivel criar o diretorio {diretorio}.")
    try:
        with open(arquivo, "w") as fp:
            fp.write(conteudo)
    except OSError as e:
        logging.exception(f"Nao foi possivel criar arquivo {arquivo}.")


class Consulta:
    """
    Armazena os dados da expressao de busca:
        - autor, titulo, livre
        - pagina
        - url
        - dados_para_requisicao
    """

    def __init__(self, autor: str, titulo: str, livre: str) -> None:
        self._autor: str = autor
        self._titulo: str = titulo
        self._livre: str = livre
        self._pagina: int = 0
        self._dados_para_requisicao: dict = None
        self._url = "https://buscarlivros"


    @property
    def pagina(self)->str:
        return self._pagina

    @property
    def dados_para_requisicao(self)->str:
        """Retorna um dicionario com os dados de Consulta."""
        if not self._dados_para_requisicao:
            self._dados_para_requisicao = {}
            if self._livre:
                self._dados_para_requisicao = {"q": self._livre}
            else:
                if self._autor:
                    self._dados_para_requisicao["autor"] = self._autor
                if self._titulo:
                    self._dados_para_requisicao["title"] = self._titulo
        return self._dados_para_requisicao


    @property
    def seguinte(self):
        dados_para_requisicao = self.dados_para_requisicao
        self._pagina += 1
        dados_para_requisicao["page"] = self._pagina
        req = Request(self._url, dados_para_requisicao)
        if req.data:
            return req.full_url + "?" + urlencode(req.data)


class Resposta:
    """Conteudo da pagina em formato JSON."""

    quantidade_documentos_por_pagina = 50

    def __init__(self, conteudo: str):
        # Conteudo maximo da pagina pura
        self._conteudo = conteudo
        # Conteudo processado, formato dicionario
        self._dados = None

    @property
    def conteudo(self):
        return self._conteudo

    @property
    def dados(self):
        if not self._dados:
            try:
                j = json.loads(self.conteudo)
            except TypeError as e:
                logging.exception(
                    "Resultado da consulta {self.conteudo}: tipo invalido. "
                                 )
            except json.JSONDecodeError as e:
                logging.exception(
                    "Resultado da consulta {self.conteudo}: JSON invalido"
                )
            else:
                self._dados = j
        return self._dados


    @property
    def documentos(self):
        """Documentos retornados na pagina."""
        return self.dados.get("docs", [])


    @property
    def total_de_paginas(self):
        """Total de paginas, todos os resultados."""
        if len(self.documentos):
            return   ceil(
                self.dados.get("num_docs", 0)
                / self.quantidade_documentos_por_pagina
                )
        return 0


def baixar_livros(arquivo, autor, titulo, livre):
    consulta = Consulta(autor, titulo, livre)
    total_de_paginas = 1
    i = 0
    while True:
        resultado = executar_requisicao(consulta.seguinte)
        if resultado:
            resposta = Resposta(resultado)
            total_de_paginas = resposta.total_de_paginas
            escrever_em_arquivo(arquivo[i], resultado)
        elif consulta.pagina == 1:
            total_de_paginas = 2
        if consulta.pagina == total_de_paginas:
            break
        i += 1


def ler_arquivo():
    return ""


def registrar_livros(arquivos, inserir_registros):
    quantidade = 0
    for arquivo in arquivos:
        conteudo = ler_arquivo(arquivo)
        resposta = Resposta(conteudo)
        quantidade += inserir_registros(resposta.documentos)
    return quantidade


