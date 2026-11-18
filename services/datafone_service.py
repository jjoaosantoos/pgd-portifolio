SIGLA = "DEMO"


def colaboradores():
    nomes = (
        "Ana Torres", "Bruno Lima", "Camila Rocha", "Diego Martins",
        "Elisa Ramos", "Felipe Moura", "Gabriela Nunes", "Helena Dias",
        "Igor Alves", "Joana Castro", "Lucas Borges", "Mariana Lopes",
        "Nicolas Melo", "Olívia Duarte", "Pedro Vieira",
    )
    ufs = ("SC", "PB", "RN", "RJ", "DF", "CE")
    return [
        {
            "nome": nome,
            "matricula": f"{indice + 1:03}",
            "uf": ufs[indice % len(ufs)],
            "funcao": "LIDER DE EQUIPE" if indice in (0, 5, 10) else "",
            "lider_matricula": f"{indice // 5 * 5 + 1:03}",
            "afastado": indice == 14,
        }
        for indice, nome in enumerate(nomes)
    ]
