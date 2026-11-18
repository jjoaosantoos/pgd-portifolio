from datetime import date

from dados.json_storage import carregar_dados, caminho_padrao_json, salvar_dados


def buscar_dados_atuais(area):
    documento = carregar_dados(area)
    if documento["versao"] is None:
        return None
    return {"versao": documento["versao"], "dados": documento["dados"]}


def obter_versao_atual(area):
    return carregar_dados(area)["versao"]


def salvar_nova_versao(area, dados):
    documento = carregar_dados(area)
    documento.update(versao=(documento["versao"] or 0) + 1, dados=dados)
    salvar_dados(documento, area)


def inicializar_demonstracao(area, pessoas):
    if caminho_padrao_json(area).exists():
        return
    hoje = date.today()
    registros = [
        {
            "sigla": area,
            "ano": hoje.year,
            "mes": hoje.month,
            "dia": dia,
            "nome": f"{pessoa['nome']} ({pessoa['matricula']})",
            "valor": valor,
        }
        for pessoa, valor, dias in (
            (pessoas[0], "F", range(3, 8)),
            (pessoas[1], "L", range(12, 15)),
        )
        for dia in dias
    ]
    salvar_nova_versao(area, registros)
