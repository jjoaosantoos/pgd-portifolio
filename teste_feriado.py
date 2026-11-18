import os
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from unittest.mock import patch

from dados.json_storage import cadastrar_feriado, carregar_dados, remover_feriado


class TesteFeriado(TestCase):
    def test_cadastrar_e_remover(self):
        with TemporaryDirectory() as diretorio, patch.dict(os.environ, {"LOCALAPPDATA": diretorio}):
            feriado = ("DEMO", 21, 4, 2026, "local", "DF")
            cadastrar_feriado(*feriado)
            self.assertEqual(len(carregar_dados("DEMO")["feriados"]), 1)
            remover_feriado(*feriado)
            self.assertEqual(carregar_dados("DEMO")["feriados"], [])


if __name__ == "__main__":
    main()
