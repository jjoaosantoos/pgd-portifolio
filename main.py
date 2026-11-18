import sys

from PyQt6.QtWidgets import QApplication

from dados.db_repository import inicializar_demonstracao
from services.datafone_service import SIGLA, colaboradores
from ui.tela_principal import TelaPrincipal


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("PGD1")
    pessoas = colaboradores()
    inicializar_demonstracao(SIGLA, pessoas)
    painel = TelaPrincipal(pessoas, SIGLA)
    painel.show()
    sys.exit(app.exec())
