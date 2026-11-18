import datetime
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QApplication,
    QTabWidget,
    QDialog,
    QLineEdit,
    QComboBox,
    QFormLayout,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer

from ui.calendario_ano import CalendarioAno
from dados.json_storage import carregar_dados, caminho_padrao_json, cadastrar_feriado

from dados.db_repository import salvar_nova_versao, buscar_dados_atuais

from PyQt6.QtGui import QIntValidator

from pathlib import Path




class TelaPrincipal(QWidget):
    def __init__(self, dados, sigla):
        super().__init__()

        self.sigla = sigla

        resultado = buscar_dados_atuais(self.sigla)

        if resultado:
            self.versao_atual = resultado["versao"]
        else:
            self.versao_atual = "N/A"

        self.setGeometry(100, 100, 1600, 700)

        self.dados = dados

        # self.label_json_topo = QLabel()
        # self.label_json_topo.setStyleSheet("font-size: 10px; color: #555;")
        # self.label_json_topo.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        # JSON SEMPRE no caminho padrão por usuário
        caminho_json = Path(caminho_padrao_json(self.sigla))
        caminho_json_inicial = str(caminho_json)

        self.caminho_json = caminho_json

        self.atualizar_titulo_janela()

        # self.label_json_topo.setText(f"JSON: {caminho_json_inicial}")
        # self.label_json_topo.setToolTip(caminho_json_inicial)

        json_local = carregar_dados(self.sigla)
        self.versao_json = json_local["versao"]
        self.dados_salvos = self._filtrar_dados_sigla(json_local["dados"])
        self.ano_atual = datetime.date.today().year
        anos = {item["ano"] for item in self.dados_salvos}
        self.calendario = CalendarioAno(
            self.dados, self.dados_salvos, self.sigla, self.ano_atual,
            caminho_json=caminho_json_inicial, anos_disponiveis=anos,
        )
        self.calendario.dados_alterados.connect(self.atualizar_dados)

        btn_salvar = QPushButton("Salvar")
        self.btn_consultar = QPushButton("Consultar")
        btn_exportar = QPushButton("Exportar CSV")

        btn_salvar.clicked.connect(self.on_salvar_click)
        self.btn_consultar.clicked.connect(self.on_consultar_click)
        btn_exportar.setEnabled(False)
        btn_exportar.setToolTip("Exportação desativada na demonstração local.")

        # Layout principal da janela
        layout_principal = QVBoxLayout(self)

        # Cria o componente de abas
        self.tabs = QTabWidget()

        # ABA 1 - PAINEL PRINCIPAL

        aba_painel = QWidget()
        layout_aba_painel = QVBoxLayout(aba_painel)

        # Layout dos botões
        layout_botoes = QHBoxLayout()
        layout_botoes.addWidget(btn_salvar)
        layout_botoes.addWidget(self.btn_consultar)
        layout_botoes.addWidget(btn_exportar)

        btn_feriados = QPushButton("Feriados")
        layout_botoes.addWidget(btn_feriados)
        btn_feriados.clicked.connect(self.abrir_tela_feriados)


        layout_topo = QHBoxLayout()
        layout_topo.addLayout(layout_botoes)
        layout_topo.addStretch()

        # Adiciona topo na aba principal
        layout_aba_painel.addLayout(layout_topo)

        # Adiciona os calendários na aba principal
        layout_aba_painel.addWidget(self.calendario)


        # ABA 2 - EM BRANCO

        aba_nova = QWidget()
        layout_aba_nova = QVBoxLayout(aba_nova)

        label_em_branco = QLabel("Em preparo...")
        label_em_branco.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_aba_nova.addWidget(label_em_branco)

        # Adiciona as abas no QTabWidget
        self.tabs.addTab(aba_painel, "Indisponibilidades")
        self.tabs.addTab(aba_nova, "Capacidade")

        # Adiciona o QTabWidget na janela principal
        layout_principal.addWidget(self.tabs)

        self.setLayout(layout_principal)

        # Define cor inicial do botão Consultar
        resultado = buscar_dados_atuais(self.sigla)
        versao_banco = resultado["versao"] if resultado else None

        # Se não existe nada no JSON local pra essa sigla, não pode estar "desatualizado"
        if versao_banco is None:
            self.atualizar_status_consultar(False)
            self.btn_consultar.setToolTip(
                "Não existem dados salvos no JSON local para esta área"
            )
        else:
            desatualizado = self.versao_json != versao_banco
            self.atualizar_status_consultar(desatualizado)

        self.timer_verificacao = QTimer(self)
        self.timer_verificacao.timeout.connect(self.verificar_versao_banco)
        self.timer_verificacao.start(45000)  # 5 segundos

    def atualizar_dados(self, novos_dados):
        self.dados_salvos = novos_dados

    def _filtrar_dados_sigla(self, dados: list[dict]) -> list[dict]:
        s = (self.sigla or "").upper().strip()
        filtrado = []
        for item in dados or []:
            sig = (item.get("sigla") or "").upper().strip()
            if sig == s:
                filtrado.append(item)
        return filtrado

    def abrir_tela_feriados(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Cadastro de Feriados")
        dialog.setModal(True)
        dialog.resize(420, 280)

        layout_principal = QVBoxLayout(dialog)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(14)

        label_titulo = QLabel("Cadastrar Feriado")
        label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_titulo.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 8px;
        """)
        layout_principal.addWidget(label_titulo)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(12)

        input_dia = QLineEdit()
        input_dia.setFixedWidth(90)
        input_dia.setFixedHeight(32)
        input_dia.setMaxLength(2)
        input_dia.setPlaceholderText("Ex: 7")
        input_dia.setValidator(QIntValidator(1, 31))

        combo_mes = QComboBox()
        combo_mes.setFixedWidth(180)
        combo_mes.setFixedHeight(32)
        combo_mes.addItems([
            "Janeiro", "Fevereiro", "Março", "Abril",
            "Maio", "Junho", "Julho", "Agosto",
            "Setembro", "Outubro", "Novembro", "Dezembro"
        ])

        input_ano = QLineEdit()
        input_ano.setFixedWidth(120)
        input_ano.setFixedHeight(32)
        input_ano.setMaxLength(4)
        input_ano.setPlaceholderText("Ex: 2026")
        input_ano.setValidator(QIntValidator(1900, 2100))

        combo_tipo = QComboBox()
        combo_tipo.setFixedWidth(180)
        combo_tipo.setFixedHeight(32)
        combo_tipo.addItems(["nacional", "local"])

        combo_uf = QComboBox()
        combo_uf.setFixedWidth(180)
        combo_uf.setFixedHeight(32)
        combo_uf.addItems(["SC", "PB", "RN", "RJ", "DF", "CE"])
        combo_uf.setEnabled(False)

        form_layout.addRow("Dia:", input_dia)
        form_layout.addRow("Mês:", combo_mes)
        form_layout.addRow("Ano:", input_ano)
        form_layout.addRow("Tipo:", combo_tipo)
        form_layout.addRow("UF:", combo_uf)

        layout_principal.addLayout(form_layout)

        def alternar_uf():
            combo_uf.setEnabled(combo_tipo.currentText() == "local")

        combo_tipo.currentIndexChanged.connect(alternar_uf)

        btn_cadastrar = QPushButton("Cadastrar")
        btn_cadastrar.setFixedHeight(36)
        btn_cadastrar.setMinimumWidth(180)
        btn_cadastrar.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                padding: 6px 12px;
            }
        """)

        layout_botao = QHBoxLayout()
        layout_botao.addStretch()
        layout_botao.addWidget(btn_cadastrar)
        layout_botao.addStretch()

        layout_principal.addLayout(layout_botao)

        def salvar_feriado():
            try:
                dia = int(input_dia.text())
                mes = combo_mes.currentIndex() + 1
                ano = int(input_ano.text())
                tipo = combo_tipo.currentText()

                if tipo == "local":
                    uf = combo_uf.currentText()
                else:
                    uf = None

                datetime.date(ano, mes, dia)
                cadastrar_feriado(self.sigla, dia, mes, ano, tipo, uf)

                self.calendario.atualizar_dados(self.dados_salvos)

                QMessageBox.information(dialog, "Sucesso", "Feriado cadastrado com sucesso!")
                dialog.accept()

            except ValueError:
                QMessageBox.warning(dialog, "Erro", "Informe uma data válida.")
            except OSError as erro:
                QMessageBox.critical(dialog, "Erro ao salvar feriado", str(erro))

        btn_cadastrar.clicked.connect(salvar_feriado)

        dialog.exec()

    def on_salvar_click(self):
        cursor_ativo = False

        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            cursor_ativo = True

            # 0) Dados que o usuário quer salvar (da tela)
            dados_para_salvar = self._filtrar_dados_sigla(self.dados_salvos)

            # 1) Pega o que já está no JSON local hoje
            atual = buscar_dados_atuais(self.sigla)
            dados_banco = self._filtrar_dados_sigla(atual["dados"]) if atual else []
            versao_banco = atual["versao"] if atual else None

            # 2) Se for igual, não cria versão nova
            if self._normalizar_registros(dados_para_salvar) == self._normalizar_registros(dados_banco):
                self.atualizar_status_consultar(False)

                QApplication.restoreOverrideCursor()
                cursor_ativo = False

                QMessageBox.information(
                    self,
                    "Nada para salvar",
                    f"Nenhuma alteração foi detectada.\n"
                    f"A área {self.sigla} já está sincronizada com o banco."
                    + (f"\nVersão atual: {versao_banco}" if versao_banco is not None else "")
                )
                return

            # 3) Se mudou, salva no JSON local (gera NOVA versão)
            salvar_nova_versao(area=self.sigla, dados=dados_para_salvar)

            # 4) Busca a versão oficial recém-criada
            resultado = buscar_dados_atuais(self.sigla)
            versao = resultado["versao"]

            self.versao_atual = versao
            self.versao_json = versao
            self.atualizar_titulo_janela()

            self.atualizar_status_consultar(False)

            QApplication.restoreOverrideCursor()
            cursor_ativo = False

            QMessageBox.information(
                self,
                "Sucesso",
                f"Dados salvos com sucesso!\nÁrea: {self.sigla}\nVersão: {versao}",
            )

        except Exception as e:
            if cursor_ativo:
                QApplication.restoreOverrideCursor()
                cursor_ativo = False

            QMessageBox.critical(self, "Erro ao salvar", str(e))

        finally:
            if cursor_ativo:
                QApplication.restoreOverrideCursor()


    def _normalizar_registros(self, registros: list[dict]) -> list[dict]:
        """
        Normaliza para comparar "conteúdo", ignorando diferenças bobas (ordem, espaços).
        Ajuste as chaves conforme seu dict real.
        """
        def norm_str(v):
            return v.strip() if isinstance(v, str) else v

        normalizado = []
        for r in (registros or []):
            item = {
                "sigla": (norm_str(r.get("sigla")) or "").upper(),
                "nome": (norm_str(r.get("nome")) or "").upper(),
                "ano": int(r.get("ano")) if r.get("ano") is not None else None,
                "mes": int(r.get("mes")) if r.get("mes") is not None else None,
                "dia": int(r.get("dia")) if r.get("dia") is not None else None,
                "valor": (norm_str(r.get("valor")) or "").upper(),
            }
            normalizado.append(item)

        normalizado.sort(key=lambda x: (
            x["sigla"], x["nome"],
            x["ano"] or 0, x["mes"] or 0, x["dia"] or 0,
            x["valor"]
        ))
        return normalizado


    def on_consultar_click(self):
        try:
            resultado = carregar_dados(self.sigla)
            dados = self._filtrar_dados_sigla(resultado["dados"])
            if self._normalizar_registros(dados) != self._normalizar_registros(self.dados_salvos):
                resposta = QMessageBox.question(
                    self, "Consultar",
                    "Recarregar o JSON local e descartar os lançamentos ainda não salvos?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if resposta != QMessageBox.StandardButton.Yes:
                    return
            self.dados_salvos = dados
            self.versao_atual = self.versao_json = resultado["versao"]
            self.calendario.atualizar_dados(dados)
            self.atualizar_status_consultar(False)
            self.atualizar_titulo_janela()
            QMessageBox.information(self, "Consulta", "Dados recarregados do JSON local.")
        except (OSError, ValueError) as erro:
            QMessageBox.critical(self, "Erro na consulta", str(erro))

    def verificar_versao_banco(self):
        resultado = buscar_dados_atuais(self.sigla)

        # Se não existe nada no JSON local pra essa área, deixa verde/neutro + tooltip certo
        if not resultado:
            self.atualizar_status_consultar(False)
            self.btn_consultar.setToolTip(
                "Não existem dados salvos no JSON local para esta área"
            )
            return

        versao_banco = resultado["versao"]

        if self.versao_json != versao_banco:
            self.atualizar_status_consultar(True)  # Vermelho
        else:
            self.atualizar_status_consultar(False)  # Verde

    def atualizar_status_consultar(self, desatualizada: bool):
        if desatualizada:
            self.btn_consultar.setStyleSheet(
                """
                background-color: #d32f2f;
                color: white;
                font-weight: bold;
            """
            )
            self.btn_consultar.setToolTip("Existe uma versão mais recente no JSON local")
        else:
            self.btn_consultar.setStyleSheet(
                """
                background-color: #2e7d32;
                color: white;
                font-weight: bold;
            """
            )
            self.btn_consultar.setToolTip("Você está usando a versão mais recente")

    def atualizar_titulo_janela(self):
        caminho_completo = str(self.caminho_json) if hasattr(self, "caminho_json") else "N/A"

        self.setWindowTitle(
            f"PGD - Painel Gestão de Dados ({self.sigla}) "
            f"- Versão local: {self.versao_atual} "
            f" || JSON: {caminho_completo}"
        )
