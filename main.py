import os
import sys
from datetime import date
from pathlib import Path
from uuid import uuid4

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QDateEdit, QDialog, QDialogButtonBox, QFileDialog,
    QFormLayout, QHBoxLayout, QInputDialog, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

from storage import Storage
from ui.calendario_ano import CalendarioAno
from utils.export_csv import exportar_calendario_csv


AREAS = {
    "Operações": [("Ana Torres", "SC", 0), ("Bruno Lima", "SC", 0),
                  ("Camila Rocha", "PR", 2), ("Diego Martins", "SP", 2)],
    "Planejamento": [("Elisa Ramos", "SP", 0), ("Felipe Moura", "PR", 0),
                     ("Gabriela Nunes", "SC", 0)],
}
UFS = ("SC", "PR", "SP")


def equipe(area):
    rows = AREAS[area]
    return [
        {"nome": nome, "matricula": str(i + 1), "uf": uf,
         "funcao": "LIDER DE EQUIPE" if i == responsavel else "",
         "lider": f"{rows[responsavel][0]} ({responsavel + 1})"}
        for i, (nome, uf, responsavel) in enumerate(rows)
    ]


def nome_completo(pessoa):
    return f"{pessoa['nome']} ({pessoa['matricula']})"


class Painel(QMainWindow):
    def __init__(self, storage):
        super().__init__()
        self.storage = storage
        self.area = next(iter(AREAS))
        self.calendario = None
        self.dirty = False
        self.state = storage.load()
        self.setWindowTitle("PGD1 · Painel de Disponibilidade · Demonstração")
        self.resize(1250, 710)
        root = QWidget()
        self.setCentralWidget(root)
        self.layout = QVBoxLayout(root)
        self.layout.addWidget(QLabel("Demonstração local · Equipes e ausências fictícias"))
        bar = QHBoxLayout()
        self.layout.addLayout(bar)
        bar.addWidget(QLabel("Área"))
        self.area_select = QComboBox()
        self.area_select.addItems(AREAS)
        self.area_select.currentTextChanged.connect(self.trocar_area)
        bar.addWidget(self.area_select)
        for title, action in (
            ("Salvar", self.salvar), ("Consultar", self.consultar),
            ("Exportar CSV", self.exportar), ("Feriados", self.feriados),
            ("Recursos externos", self.externos),
        ):
            button = QPushButton(title)
            button.clicked.connect(action)
            bar.addWidget(button)
        bar.addStretch()
        self.consultar(confirmar=False)

    def importados(self):
        hoje = date.today()
        clientes = equipe(self.area)
        return [
            {"sigla": self.area, "nome": nome_completo(clientes[index]), "ano": hoje.year,
             "mes": hoje.month, "dia": dia, "valor": codigo}
            for index, codigo, dias in [(0, "F", range(3, 8)), (1, "L", range(12, 15))]
            for dia in dias
        ]

    def render(self):
        ano = self.calendario.ano if self.calendario else date.today().year
        if self.calendario:
            self.layout.removeWidget(self.calendario)
            self.calendario.hide()
            self.calendario.deleteLater()
        pessoas = equipe(self.area) + [
            pessoa for pessoa in self.state["externos"] if pessoa["area"] == self.area
        ]
        self.calendario = CalendarioAno(
            pessoas, self.registros, self.area, ano, feriados=self.state["feriados"]
        )
        self.calendario.dados_alterados.connect(self.alterado)
        self.layout.addWidget(self.calendario)

    def alterado(self, _):
        self.dirty = True
        self.statusBar().showMessage("Há lançamentos aguardando salvamento.")

    def confirmar_descarte(self):
        if not self.dirty:
            return True
        return QMessageBox.question(
            self, "Alterações pendentes", "Descartar os lançamentos ainda não salvos?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ) == QMessageBox.StandardButton.Yes

    def trocar_area(self, area):
        if self.confirmar_descarte():
            self.area = area
            self.consultar(confirmar=False)
            return
        self.area_select.blockSignals(True)
        self.area_select.setCurrentText(self.area)
        self.area_select.blockSignals(False)

    def consultar(self, confirmar=True):
        if confirmar and not self.confirmar_descarte():
            return
        self.state = self.storage.load()
        atual = self.state["areas"].get(self.area, {})
        self.registros = self.importados() + atual.get("dados", [])
        self.dirty = False
        self.render()
        self.statusBar().showMessage(f"{self.area} · versão {atual.get('versao', 0)}")

    def gravar(self, state):
        try:
            self.storage.save(state)
        except OSError as error:
            QMessageBox.critical(self, "Erro ao salvar", str(error))
            return False
        self.state = state
        return True

    def salvar(self):
        state = self.storage.load()
        versao = state["areas"].get(self.area, {}).get("versao", 0) + 1
        state["areas"][self.area] = {
            "versao": versao,
            "dados": [item for item in self.registros if item["valor"] not in {"F", "L"}],
        }
        if self.gravar(state):
            self.dirty = False
            self.statusBar().showMessage(f"{self.area} · versão {versao} salva.")

    def exportar(self):
        ano = self.calendario.ano
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar calendário", f"PGD1-{self.area}-{ano}.csv", "CSV (*.csv)"
        )
        if not path:
            return
        try:
            exportar_calendario_csv(
                str(Path(path).resolve()), ano, self.calendario.obter_nomes(), self.registros
            )
        except OSError as error:
            QMessageBox.critical(self, "Erro ao exportar", str(error))
            return
        self.statusBar().showMessage(f"Calendário de {ano} exportado.")

    def formulario(self, title, fields):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        form = QFormLayout(dialog)
        for label, control in fields:
            form.addRow(label, control)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        return dialog.exec() == QDialog.DialogCode.Accepted

    def acao_cadastro(self, title, itens):
        choices = ["Cadastrar", "Remover"] if itens else ["Cadastrar"]
        action, ok = QInputDialog.getItem(self, title, "Ação", choices, editable=False)
        return action if ok else ""

    def feriados(self):
        state = self.storage.load()
        itens = state["feriados"]
        action = self.acao_cadastro("Feriados", itens)
        if action == "Cadastrar":
            nome = QLineEdit()
            data = QDateEdit(QDate(self.calendario.ano, 1, 1))
            data.setCalendarPopup(True)
            abrangencia = QComboBox()
            abrangencia.addItems(["Nacional", *UFS])
            if not self.formulario("Cadastrar feriado", [
                ("Nome", nome), ("Data", data), ("Abrangência", abrangencia)
            ]):
                return
            if not nome.text().strip():
                QMessageBox.warning(self, "Feriado", "Informe o nome do feriado.")
                return
            dia = data.date()
            uf = abrangencia.currentText() if abrangencia.currentIndex() else None
            itens.append({"nome": nome.text().strip(), "dia": dia.day(), "mes": dia.month(),
                          "ano": dia.year(), "tipo": "local" if uf else "nacional", "uf": uf})
        elif action == "Remover":
            labels = [
                f"{i + 1}. {item['nome']} · {item['dia']:02}/{item['mes']:02}/{item['ano']} "
                f"· {item['uf'] or 'Nacional'}" for i, item in enumerate(itens)
            ]
            label, ok = QInputDialog.getItem(self, "Remover feriado", "Feriado", labels, editable=False)
            if not ok:
                return
            itens.pop(labels.index(label))
        else:
            return
        if self.gravar(state):
            self.render()

    def externos(self):
        state = self.storage.load()
        locais = [item for item in state["externos"] if item["area"] == self.area]
        action = self.acao_cadastro("Recursos externos", locais)
        removido = None
        if action == "Cadastrar":
            nome, empresa = QLineEdit(), QLineEdit()
            uf, lider = QComboBox(), QComboBox()
            uf.addItems(UFS)
            lider.addItems([pessoa["lider"] for pessoa in equipe(self.area) if pessoa["funcao"]])
            if not self.formulario("Cadastrar recurso externo", [
                ("Nome", nome), ("Empresa", empresa), ("UF", uf), ("Líder", lider)
            ]):
                return
            if not nome.text().strip() or not empresa.text().strip():
                QMessageBox.warning(self, "Recurso externo", "Informe nome e empresa.")
                return
            state["externos"].append({
                "nome": f"{nome.text().strip()} · {empresa.text().strip()}",
                "matricula": f"EXT-{uuid4().hex[:8]}", "uf": uf.currentText(),
                "lider": lider.currentText(), "area": self.area,
            })
        elif action == "Remover":
            labels = [nome_completo(pessoa) for pessoa in locais]
            removido, ok = QInputDialog.getItem(self, "Remover recurso", "Recurso", labels, editable=False)
            if not ok or QMessageBox.question(
                self, "Remover recurso", "Remover o recurso e todos os seus lançamentos?"
            ) != QMessageBox.StandardButton.Yes:
                return
            state["externos"].remove(locais[labels.index(removido)])
            area_salva = state["areas"].get(self.area)
            if area_salva:
                area_salva["dados"] = [item for item in area_salva["dados"] if item["nome"] != removido]
                area_salva["versao"] += 1
        else:
            return
        if self.gravar(state):
            if removido:
                self.registros[:] = [item for item in self.registros if item["nome"] != removido]
            self.render()

    def closeEvent(self, event):
        if self.confirmar_descarte():
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    path = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "PGD1-Portfolio" / "dados.json"
    try:
        painel = Painel(Storage(path))
    except (OSError, ValueError) as error:
        QMessageBox.critical(None, "Erro ao abrir dados locais", str(error))
        sys.exit(1)
    painel.show()
    sys.exit(app.exec())
