import pytest
from unittest import skip
from unittest.mock import patch, mock_open, MagicMock, call 
from colecao.livros import (consultar_livros,
                            executar_requisicao,
                            escrever_em_arquivo,
                            Consulta,
                            baixar_livros,
                            Resposta,
                            registrar_livros,
                            )
from urllib.request import HTTPError, URLError



class StubHTTPResponse:
    def read(self):
        return b''

    def __enter__(self):
        return self

    def __exit__(self, param1, param2, param3):
        pass


@patch("colecao.livros.urlopen", return_value=StubHTTPResponse())
def test_quando_consultar_livros_deve_retornar_uma_string(stub_urlopen):
    resultado = consultar_livros("Agatha Christie")

    assert type(resultado) == str


@patch("colecao.livros.urlopen", return_value=StubHTTPResponse())
def test_quando_consultar_livros_deve_chamar_preparar_dados_com_os_mesmos_parametros(stub_urlopen):
    with patch("colecao.livros.preparar_dados_para_requisicao") as spy_preparar_dados:
        consultar_livros("Agatha Christie")
        spy_preparar_dados.assert_called_once_with("Agatha Christie")


@patch("colecao.livros.urlopen", return_value=StubHTTPResponse())
def test_quando_consultar_livros_deve_chamar_obter_url_com_o_retorno_de_preparar_dados_para_requisicao(stub_urlopen):
    with patch("colecao.livros.preparar_dados_para_requisicao") as stub_preparar_dados:
        dados = {"author": "Agatha Christie"}
        stub_preparar_dados.return_value = dados
        with patch("colecao.livros.obter_url") as spy_obter_url:
            consultar_livros("Agatha Christie")
            spy_obter_url.assert_called_once_with("https://buscador", dados)


@patch("colecao.livros.urlopen", return_value=StubHTTPResponse())
def test_quando_consultar_livro_deve_executar_requisicao_usando_retorno_obter_url(stub_urlopen):
    with patch("colecao.livros.obter_url") as stub_obter_url:
        stub_obter_url.return_value = "https://buscador"
        with patch("colecao.livros.executar_requisicao") as spy_executar_requisicao:
            consultar_livros("Agatha Christie")
            spy_executar_requisicao.assert_called_once_with("https://buscador")


def stub_urlopen(url, timeout):
    return StubHTTPResponse()


def test_quando_executar_requisicao_deve_retornar_string_1():
    with patch("colecao.livros.urlopen", stub_urlopen):
        url = "https://buscarlivros?author=J+K+Rowlings"
        resultado = executar_requisicao(url)
        assert type(resultado) == str


def test_quando_executar_requisicao_deve_retornar_string_2():
    with patch("colecao.livros.urlopen") as stub_urlopen_2:
        stub_urlopen_2.return_value = StubHTTPResponse()
        url = "https://buscarlivros?author=J+K+Rowlings"
        resultado = executar_requisicao(url)
        assert type(resultado) == str



def test_quando_executar_requisicao_deve_retornar_string_3():
    with patch("colecao.livros.urlopen", return_value=StubHTTPResponse()):
        url = "https://buscarlivros?author=J+K+Rowlings"
        resultado = executar_requisicao(url)
        assert type(resultado) == str


@patch("colecao.livros.urlopen", return_value=StubHTTPResponse())
def test_quando_executar_requisicao_deve_retornar_string_4(stub_urlopen_4):
    url = "https://buscarlivros?author=J+K+Rowlings"
    resultado = executar_requisicao(url)
    assert type(resultado) == str



@patch("colecao.livros.urlopen")
def test_quando_executar_requisicao_deve_retornar_string_5(stub_urlopen_5):
    stub_urlopen_5.return_value = StubHTTPResponse()
    url = "https://buscarlivros?author=J+K+Rowlings"
    resultado = executar_requisicao(url)
    assert type(resultado) == str


class Dummy:
    pass

def stub_urlopen_http_error(url, timeout):
    fp = mock_open
    fp.close = Dummy
    raise HTTPError(Dummy(), Dummy(), "mensagem de erro", Dummy(), fp)



@patch("colecao.livros.urlopen", return_value=StubHTTPResponse())
def test_quando_executar_requsicao_deve_retornar_http_error_1(stub_urlopen):
    stub_urlopen.side_effect = URLError("mensagem de erro")
    with pytest.raises(URLError) as excecao:
        executar_requisicao("https://buscador")
    assert "mensagem de erro" in str(excecao.value)

@patch("colecao.livros.urlopen")
def test_quando_executar_requsicao_deve_retornar_http_error_2(stub_urlopen):
    stub_urlopen.side_effect = URLError("mensagem de erro")
    with pytest.raises(URLError) as excecao:
        executar_requisicao("https://buscador")
    assert "mensagem de erro" in str(excecao.value)


def test_quando_executar_requisicao_deve_logar_http_error(caplog):
    with patch("colecao.livros.urlopen", stub_urlopen_http_error):
        resultado = executar_requisicao("https://buscador")
        mensagem_de_erro = "mensagem de erro"
        assert len(caplog.records) == 1
        for registro in caplog.records:
            assert mensagem_de_erro in registro.message



@patch("colecao.livros.urlopen")
def test_quando_executar_requsicao_deve_logar_http_error_2(stub_urlopen, caplog):
    fp = mock_open
    mensagem_de_erro = "mensagem de erro"
    fp.close = Dummy
    stub_urlopen.side_effect = HTTPError(Dummy(), Dummy(), "mensagem de erro", Dummy(), fp)
    executar_requisicao("https://buscador")
    assert len(caplog.records) == 1
    for registro in caplog.records:
        assert mensagem_de_erro in registro.message



class StubLogging():
    def __init__(self):
        self._mensagens = []

    @property
    def mensagens(self):
        return self._mensagens

    def exception(self, mensagem):
        self._mensagens.append(mensagem)


def stub_makedirs(diretorio):
    raise OSError(f"Nao foi possivel criar o diretorio {diretorio}")

def test_quando_escreve_em_arquivo_deve_logar_os_error():
    arquivo = "/tmp/arquivos.json"
    conteudo = "dados de livros"
    stub_logging = StubLogging()
    with patch("colecao.livros.os.makedirs", stub_makedirs):
        with patch("colecao.livros.logging", stub_logging):
            escrever_em_arquivo(arquivo, conteudo)
            assert "Nao foi possivel criar o diretorio /tmp." in stub_logging.mensagens 



@patch("colecao.livros.open", side_effect=OSError())
@patch("colecao.livros.os.makedirs")
@patch("colecao.livros.logging.exception")
def test_quando_escreve_em_arquivo_deve_logar_erro_ao_criar_arquivo(spy_exception,
                                                                    stub_makedirs,
                                                                    stub_open
                                                                   ):
    arq = "/bla/bla/bla.json"
    escrever_em_arquivo(arq, "dados de livros")
    spy_exception.assert_called_once_with(f"Nao foi possivel criar arquivo {arq}.")


class SpyFp():

    def __init__(self):
        self._conteudo = None

    def __enter__(self):
        return self

    def __exit__(self, param1, param2, param3):
        pass

    def write(self, conteudo):
        self._conteudo = conteudo

    @property
    def conteudo(self):
        return self._conteudo


@patch("colecao.livros.open")
def test_quando_escrever_arquivo_deve_chamar_write_1(stub_open):
    arq = "tmp/arquivo"
    conteudo = "conteudo do arquivo."
    spy_de_fp = SpyFp()
    stub_open.return_value = spy_de_fp

    escrever_em_arquivo(arq, conteudo)
    assert spy_de_fp.conteudo == conteudo



@patch("colecao.livros.open")
def test_quando_escrever_arquivo_deve_chamar_write_2(stub_de_open):
    arq = "tmp/arquivo"
    conteudo = "Conteudo do arquivo"
    spy_de_fp = MagicMock()
    spy_de_fp.__enter__.return_value = spy_de_fp
    spy_de_fp.__exit__.return_value = None
    stub_de_open.return_value = spy_de_fp

    escrever_em_arquivo(arq, conteudo)
    spy_de_fp.write.assert_called_once_with(conteudo)


@pytest.fixture
def resultado_em_duas_paginas():
    return [
        """
        {
            "num_docs": 5,
            "docs": [
                {"author": "Luciano Ramalho",
                 "title": "Python Fluent"
                },
                {"author": "Nilo Neil",
                 "title": "Introducao a Programacao com Python"
                },
                {"author": "Allen B. Downey",
                 "title": "Pense em Python"
                }
            ]
        }
        """,
        """
        {
            "num_docs": 5,
            "docs": [
                {"author": "Kenneth Reitz",
                 "title": "O Guia do Mochileiro Python"
                },
                {"author": "Wes McKinney",
                 "title": "Python Para Abakuse de Dados"
                }
            ]
        }
        """,
    ]


@pytest.fixture
def resultado_em_tres_paginas():
    return [
        """
        {
            "num_docs": 8,
            "docs": [
                {"author": "Luciano Ramalho",
                 "title": "Python Fluent"
                },
                {"author": "Nilo Neil",
                 "title": "Introducao a Programacao com Python"
                },
                {"author": "Allen B. Downey",
                 "title": "Pense em Python"
                }
            ]
        }
        """,
        """
        {
            "num_docs": 8,
            "docs": [
                {"author": "Luciano Ramalho",
                 "title": "Python Fluent"
                },
                {"author": "Nilo Neil",
                 "title": "Introducao a Programacao com Python"
                },
                {"author": "Allen B. Downey",
                 "title": "Pense em Python"
                }
            ]
        }
        """,
        """
        {
            "num_docs": 8,
            "docs": [
                {"author": "Kenneth Reitz",
                 "title": "O Guia do Mochileiro Python"
                },
                {"author": "Wes McKinney",
                 "title": "Python Para Abakuse de Dados"
                }
            ]
        }
        """,
    ]


@pytest.fixture
def conteudo_de_quatro_arquivos():
    return [
        """
        {
            "num_docs": 17,
            "docs": [
                {"author": "Luciano Ramalho",
                 "title": "Python Fluent"
                },
                {"author": "Nilo Neil",
                 "title": "Introducao a Programacao com Python"
                },
                {"author": "Luciano Ramalho",
                 "title": "Python Fluent"
                },
                {"author": "Nilo Neil",
                 "title": "Introducao a Programacao com Python"
                },
                {"author": "Allen B. Downey",
                 "title": "Pense em Python"
                }
            ]
        }
        """,
        """
        {
            "num_docs": 17,
            "docs": [
                {"author": "Luciano Ramalho",
                 "title": "Python Fluent"
                },
                {"author": "Nilo Neil",
                 "title": "Introducao a Programacao com Python"
                },
                {"author": "Luciano Ramalho",
                 "title": "Python Fluent"
                },
                {"author": "Nilo Neil",
                 "title": "Introducao a Programacao com Python"
                },
                {"author": "Allen B. Downey",
                 "title": "Pense em Python"
                }
            ]
        }
        """,
        """
        {
            "num_docs": 17,
            "docs": [
                {"author": "Luciano Ramalho",
                 "title": "Python Fluent"
                },
                {"author": "Nilo Neil",
                 "title": "Introducao a Programacao com Python"
                },
                {"author": "Luciano Ramalho",
                 "title": "Python Fluent"
                },
                {"author": "Nilo Neil",
                 "title": "Introducao a Programacao com Python"
                },
                {"author": "Allen B. Downey",
                 "title": "Pense em Python"
                }
            ]
        }
        """,
        """
        {
            "num_docs": 17,
            "docs": [
                {"author": "Kenneth Reitz",
                 "title": "O Guia do Mochileiro Python"
                },
                {"author": "Wes McKinney",
                 "title": "Python Para Abakuse de Dados"
                }
            ]
        }
        """,
    ]


@pytest.fixture
def resultado_em_tres_paginas_erro_na_pagina_2():
    return [
        """
        {
            "num_docs": 8,
            "docs": [
                {"author": "Luciano Ramalho",
                 "title": "Python Fluent"
                },
                {"author": "Nilo Neil",
                 "title": "Introducao a Programacao com Python"
                },
                {"author": "Allen B. Downey",
                 "title": "Pense em Python"
                }
            ]
        }
        """,
        None,
        """
        {
            "num_docs": 8,
            "docs": [
                {"author": "Kenneth Reitz",
                 "title": "O Guia do Mochileiro Python"
                },
                {"author": "Wes McKinney",
                 "title": "Python Para Abakuse de Dados"
                }
            ]
        }
        """,
    ]


@pytest.fixture
def resultado_em_tres_pagina_erro_na_pagina_1():
    return [
        None,
        """
        {
            "num_docs": 8,
            "docs": [
                {"author": "Luciano Ramalho",
                 "title": "Python Fluent"
                },
                {"author": "Nilo Neil",
                 "title": "Introducao a Programacao com Python"
                },
                {"author": "Allen B. Downey",
                 "title": "Pense em Python"
                }
            ]
        }
        """,
        """
        {
            "num_docs": 8,
            "docs": [
                {"author": "Kenneth Reitz",
                 "title": "O Guia do Mochileiro Python"
                },
                {"author": "Wes McKinney",
                 "title": "Python Para Abakuse de Dados"
                }
            ]
        }
        """,
    ]


class MockConsulta:
    def __init__(self):
        self.chamadas = []
        self.consultas = []


    def Consulta(self, autor=None, title=None, livre=None):
        consulta = Consulta(autor, title, livre)
        self.chamadas.append((autor, title, livre))
        self.consultas.append(consulta)
        return consulta


    def verifica(self):
        assert len(self.consultas) == 1
        assert self.chamadas == [(None, None, "Python")]


@patch ("colecao.livros.executar_requisicao")
def test_quando_baixar_livros_instancia_consulta_uma_vez(stub_executar_requisicao, resultado_em_duas_paginas):
    stub_executar_requisicao.side_effect = resultado_em_duas_paginas
    duble = MockConsulta()
    Resposta.quantidade_documentos_por_pagina = 3
    arquivo = [
        "/tmp/arquivo1",
        "/tmp/arquivo2",
        "/tmp/arquivo3"
    ]
    with patch("colecao.livros.Consulta", duble.Consulta):
        baixar_livros(arquivo, None, None, "Python")
        duble.verifica()


@patch ("colecao.livros.executar_requisicao")
def test_quando_baixar_livro_deve_chamar_requisicao_n_vezes(mock_executar_requisicao, resultado_em_duas_paginas):
    mock_executar_requisicao.side_effect = resultado_em_duas_paginas
    Resposta.quantidade_documentos_por_pagina = 3
    arquivo = [
        "/tmp/arquivo1",
        "/tmp/arquivo2",
        "/tmp/arquivo3"
    ]
    baixar_livros(arquivo, None, None, "Python")
    assert mock_executar_requisicao.call_args_list ==[
        call("https://buscarlivros?q=Python&page=1"),
        call("https://buscarlivros?q=Python&page=2"),
    ]



@patch ("colecao.livros.executar_requisicao")
def test_quando_baixar_livro_deve_instanciar_Resposta_tres_vezes(stub_executar_requisicao, resultado_em_tres_paginas):
    stub_executar_requisicao.side_effect = resultado_em_tres_paginas
    Resposta.quantidade_documentos_por_pagina = 3
    arquivo = [
        "/tmp/arquivo1",
        "/tmp/arquivo2",
        "/tmp/arquivo3"
    ]
    with patch("colecao.livros.Resposta") as MockResposta:
        MockResposta.side_effect = [
            Resposta(resultado_em_tres_paginas[0]),
            Resposta(resultado_em_tres_paginas[1]),
            Resposta(resultado_em_tres_paginas[2])
        ]
        baixar_livros(arquivo, None, None, "Python")
        assert MockResposta.call_args_list == [
            call(resultado_em_tres_paginas[0]),
            call(resultado_em_tres_paginas[1]),
            call(resultado_em_tres_paginas[2])
        ]
        

@patch ("colecao.livros.executar_requisicao")
def test_quando_baixar_livros_deve_escrever_em_arquivo_tres_vezes(stub_executar_requisicao, resultado_em_tres_paginas):
    stub_executar_requisicao.side_effect = resultado_em_tres_paginas
    Resposta.quantidade_documentos_por_pagina = 3
    arquivo = [
        "/tmp/arquivo1",
        "/tmp/arquivo2",
        "/tmp/arquivo3"
    ]
    with patch("colecao.livros.escrever_em_arquivo") as mock_escrever:
        mock_escrever.return_value = baixar_livros(arquivo, None, None, "Python")
        assert mock_escrever.call_args_list == [
            call(arquivo[0], resultado_em_tres_paginas[0]),
            call(arquivo[1], resultado_em_tres_paginas[1]),
            call(arquivo[2], resultado_em_tres_paginas[2]),            
        ]


@patch ("colecao.livros.executar_requisicao")
def test_quando_baixar_livros_deve_escrever_em_arquivos_para_pagina_1_e_3(stub_executar_requisicao, resultado_em_tres_paginas_erro_na_pagina_2):
    stub_executar_requisicao.side_effect = resultado_em_tres_paginas_erro_na_pagina_2
    Resposta.quantidade_documentos_por_pagina = 3
    arquivo = [
        "/tmp/arquivo1",
        "/tmp/arquivo2",
        "/tmp/arquivo3"
    ]
    with patch("colecao.livros.escrever_em_arquivo") as mock_escrever:
        mock_escrever.side_effect = [None, None]
        mock_escrever.return_value = baixar_livros(arquivo, None, None, "Python")
        assert mock_escrever.call_args_list == [
            call(arquivo[0], resultado_em_tres_paginas_erro_na_pagina_2[0]),
            # call(arquivo[1], resultado_em_tres_paginas_erro_na_pagina_2[1]),
            call(arquivo[2], resultado_em_tres_paginas_erro_na_pagina_2[2]),            
        ]


@patch ("colecao.livros.executar_requisicao")
def test_quando_baixar_livros_deve_escrever_em_arquivos_para_pagina_2_e_3(stub_executar_requisicao, resultado_em_tres_pagina_erro_na_pagina_1):
    stub_executar_requisicao.side_effect = resultado_em_tres_pagina_erro_na_pagina_1
    Resposta.quantidade_documentos_por_pagina = 3
    arquivo = [
        "/tmp/arquivo1",
        "/tmp/arquivo2",
        "/tmp/arquivo3"
    ]
    with patch("colecao.livros.escrever_em_arquivo") as mock_escrever:
        mock_escrever.side_effect = [None, None]
        mock_escrever.return_value = baixar_livros(arquivo, None, None, "Python")
        assert mock_escrever.call_args_list == [
            # call(arquivo[0], resultado_em_tres_paginas_erro_na_pagina_2[0]),
            call(arquivo[1], resultado_em_tres_pagina_erro_na_pagina_1[1]),
            call(arquivo[2], resultado_em_tres_pagina_erro_na_pagina_1[2]),            
        ]



def test_quando_registrar_livros_deve_chamar_ler_arquivo_3_vezes(resultado_em_tres_paginas):
    arquivos = [
            "/tmp/arquivo1",
            "/tmp/arquivo2",
            "/tmp/arquivo3",
            ] 
    with patch("colecao.livros.ler_arquivo") as duble_ler_arquivo:
        duble_ler_arquivo.side_effect = resultado_em_tres_paginas
        registrar_livros(arquivos, fake_inserir_registros)
        assert duble_ler_arquivo.call_args_list == [
            call(arquivos[0]),
            call(arquivos[1]),
            call(arquivos[2]),
        ]


def test_quando_registrar_livros_deve_instanciar_Resposta_3_vezes(resultado_em_tres_paginas):
    arquivos = [
            "/tmp/arquivo1",
            "/tmp/arquivo2",
            "/tmp/arquivo3",
            ]
    with patch("colecao.livros.ler_arquivo") as stub_ler_arquivo:
        stub_ler_arquivo.side_effect = resultado_em_tres_paginas
        with patch("colecao.livros.Resposta") as MockResposta:
            registrar_livros(arquivos, fake_inserir_registros)
            MockResposta.side_effect = [
                        Resposta(resultado_em_tres_paginas[0]),
                        Resposta(resultado_em_tres_paginas[1]),
                        Resposta(resultado_em_tres_paginas[2]),
                    ]
            assert MockResposta.call_args_list == [
                    call(resultado_em_tres_paginas[0]),
                    call(resultado_em_tres_paginas[1]),
                    call(resultado_em_tres_paginas[2]),
                    ]


@patch("colecao.livros.ler_arquivo")            
def test_quando_registrar_livros_deve_instanciar_Resposta_quatro_vezes(stub_ler_arquivo, conteudo_de_quatro_arquivos):
    arquivos = [
            "/tmp/arquivo1",
            "/tmp/arquivo2",
            "/tmp/arquivo3",
            "/tmp/arquivo4",
            ]
    stub_ler_arquivo.side_effect = conteudo_de_quatro_arquivos
    with patch("colecao.livros.Resposta") as MockResposta:
        registrar_livros(arquivos, fake_inserir_registros)
        MockResposta.side_effect = [
                    Resposta(conteudo_de_quatro_arquivos[0]),
                    Resposta(conteudo_de_quatro_arquivos[1]),
                    Resposta(conteudo_de_quatro_arquivos[2]),
                    Resposta(conteudo_de_quatro_arquivos[3]),
                ]
        assert MockResposta.call_args_list == [
                call(conteudo_de_quatro_arquivos[0]),
                call(conteudo_de_quatro_arquivos[1]),
                call(conteudo_de_quatro_arquivos[2]),
                call(conteudo_de_quatro_arquivos[3]),
                ]


def fake_inserir_registros(dados):
    return len(dados)


@patch("colecao.livros.ler_arquivo")
def test_quando_registrar_livros_deve_chamar_inserir_registro(stub_ler_arquivos, conteudo_de_quatro_arquivos):
    arquivos = [
            "/tmp/arquivo1",
            "/tmp/arquivo3",
            "/tmp/arquivo4",
            ]
    conteudo_de_tres_arquivos = conteudo_de_quatro_arquivos[1:]
    stub_ler_arquivos.side_effect = conteudo_de_tres_arquivos
   
    quantidade = registrar_livros(arquivos, fake_inserir_registros)
    assert quantidade == 12



@patch("colecao.livros.ler_arquivo")
def test_quando_registrar_livros_deve_inserir_5_registros(stub_ler_arquivo, resultado_em_duas_paginas):
    stub_ler_arquivo.side_effect = resultado_em_duas_paginas
    arquivos = [
            "/tmp/arquivo_1",
            "/tmp/arquivo_2",
            ]
    fake_db = MagicMock()
    fake_db.inserir_registros = fake_inserir_registros
    # fake_db.inserir_registros = lambda dados: len(dados)
    quantidade = registrar_livros(arquivos, fake_db.inserir_registros)
    assert quantidade == 5



class FakeDb:
    def __init__(self):
        self._registros = []

    def inserir_registros(self, dados):
        self._registros.extend(dados)
        return len(dados)


@patch("colecao.livros.ler_arquivo")
def test_quando_registrar_livros_deve_inserir_8_registros_na_base_de_dados(stub_ler_arquivo, resultado_em_tres_paginas):
    arquivos = [
            "/tmp/arquivo1",
            "/tmp/arquivo2",
            "/tmp/arquivo3",
            ]
    stub_ler_arquivo.side_effect = resultado_em_tres_paginas
    fake_db = FakeDb()
    quantidade = registrar_livros(arquivos, fake_db.inserir_registros)
    assert quantidade == 8
    assert fake_db._registros[0] == {
            "author": "Luciano Ramalho",
            "title": "Python Fluent"}


