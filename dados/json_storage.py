import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


def _pasta_padrao() -> Path:
    """
    C:\\Users\\<usuario>\\Python\\feriasJson
    """

    base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    pasta = base / "PGD1-Fiel"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def _arquivo_por_sigla(sigla: str) -> Path:
    """
    Retorna:
    ferias_DVGD.json
    ferias_DAED.json
    etc...
    """
    sigla_limpa = (sigla or "").upper().strip()
    nome = f"ferias_{sigla_limpa}.json"
    return _pasta_padrao() / nome


def carregar_dados(sigla: str):
    arquivo = _arquivo_por_sigla(sigla)

    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)

        if isinstance(dados, list):
            dados = {"versao": None, "sigla": sigla, "dados": dados}
        if "feriados" not in dados:
            dados["feriados"] = []

        return dados

    except FileNotFoundError:
        return {"versao": None,
                "sigla": sigla,
                "dados": [],
                "feriados": []
                }


def salvar_dados(dados: dict, sigla: str):
    arquivo = _arquivo_por_sigla(sigla)

    with NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=arquivo.parent, delete=False
    ) as tmp:
        caminho_tmp = Path(tmp.name)
        try:
            json.dump(dados, tmp, ensure_ascii=False, indent=4)
            tmp.close()
            os.replace(caminho_tmp, arquivo)
        finally:
            tmp.close()
            caminho_tmp.unlink(missing_ok=True)


def cadastrar_feriado(sigla: str, dia: int, mes: int, ano: int, tipo: str, uf: str | None):
    dados = carregar_dados(sigla)

    novo_feriado = {
        "dia": dia,
        "mes": mes,
        "ano": ano,
        "tipo": tipo,
        "uf": uf,
    }

    dados["feriados"].append(novo_feriado)
    salvar_dados(dados, sigla)

def remover_feriado(sigla: str, dia: int, mes: int, ano: int, tipo: str, uf: str | None):
    dados = carregar_dados(sigla)

    dados["feriados"] = [
        f for f in dados["feriados"]
        if not (
            f.get("dia") == dia and
            f.get("mes") == mes and
            f.get("ano") == ano and
            f.get("tipo") == tipo and
            f.get("uf") == uf
        )
    ]

    salvar_dados(dados, sigla)

def caminho_padrao_json(sigla: str) -> Path:
    return _arquivo_por_sigla(sigla)
