"""
Simulador de Escalonamento de Processos
Autor: Heder Dorneles Soares

Descrição:
    Este programa simula o escalonamento de processos utilizando quatro 
    algoritmos diferentes: FCFS, SPN, SRT e Round Robin.
"""

import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QAction, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QHBoxLayout, QPushButton, QLineEdit, QComboBox, QMessageBox, QMenuBar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Simulador de Escalonamento de Processos')
        
        self.setGeometry(100, 100, 800, 400)
        
        # Layouts
        main_layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        
        # Cria a barra de menu
        self.create_menu_bar()

        # Adiciona a barra de menu ao layout
        main_layout.setMenuBar(self.menu_bar)
        
        # Campo de texto para visualizar o nome do processo atual
        self.process_name_label = QLabel('Processo Atual: A')
        main_layout.addWidget(self.process_name_label)
        
        # Campo de entrada para tempo de chegada
        self.arrival_input = QLineEdit()
        self.arrival_input.setPlaceholderText('Tempo de Chegada')
        input_layout.addWidget(self.arrival_input)
        
        # Campo de entrada para tempo de execução
        self.execution_input = QLineEdit()
        self.execution_input.setPlaceholderText('Tempo de Execução')
        input_layout.addWidget(self.execution_input)
        
        # ComboBox para escolher o algoritmo de escalonamento
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItem("FCFS")
        self.algorithm_combo.addItem("SPN")
        self.algorithm_combo.addItem("SRT")
        self.algorithm_combo.addItem("Round Robin")
        input_layout.addWidget(self.algorithm_combo)

        # Campo de entrada para o quantum (Round Robin)
        self.quantum_input = QLineEdit()
        self.quantum_input.setPlaceholderText('Quantum')
        input_layout.addWidget(self.quantum_input)
        
        main_layout.addLayout(input_layout)
        
        # Botão para adicionar processo à tabela
        self.add_button = QPushButton('Adicionar Processo')
        self.add_button.clicked.connect(self.add_process)
        main_layout.addWidget(self.add_button)
        
        # Tabela para exibir os processos
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(3)
        self.process_table.setHorizontalHeaderLabels(['Nome', 'Tempo de Chegada', 'Tempo de Execução'])
        main_layout.addWidget(self.process_table)
        
        # Botão para executar o escalonamento
        self.execute_button = QPushButton('Executar')
        self.execute_button.clicked.connect(self.execute_scheduling)
        main_layout.addWidget(self.execute_button)
        
        # Botão para limpar a simulação
        self.clear_button = QPushButton('Limpar')
        self.clear_button.clicked.connect(self.clear_simulation)
        main_layout.addWidget(self.clear_button)
        
        # Figura para o gráfico de barras
        self.bar_chart = plt.figure()
        self.bar_chart_canvas = FigureCanvas(self.bar_chart)
        main_layout.addWidget(self.bar_chart_canvas)
        
        self.setLayout(main_layout)
        
        # Variável para controlar o nome do próximo processo
        self.next_process_name = 'A'
        
    def create_menu_bar(self):
        # Cria a barra de menu
        self.menu_bar = QMenuBar()

        # Cria o menu "Arquivo" e adiciona a ação "Sair"
        file_menu = self.menu_bar.addMenu('Arquivo')
        exit_action = QAction('Sair', self)
        exit_action.setShortcut('Esc')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Cria o menu "Ajuda" e adiciona a ação "Sobre"
        help_menu = self.menu_bar.addMenu('Ajuda')
        about_action = QAction('Sobre', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
    def show_about_dialog(self):
        about_text = "Escalonador de processos 1.0\nAutor: Heder Dorneles Soares\n \
        Curso de Análise e Desenvolvimento de Sistemas."
        QMessageBox.about(self, 'Sobre', about_text)
        
    def add_process(self):
        # Obter os dados do processo dos campos de entrada
        name = self.next_process_name
        arrival_time = self.arrival_input.text()
        execution_time = self.execution_input.text()
        
        # Inserir os dados na tabela de processos
        row_position = self.process_table.rowCount()
        self.process_table.insertRow(row_position)
        self.process_table.setItem(row_position, 0, QTableWidgetItem(name))
        self.process_table.setItem(row_position, 1, QTableWidgetItem(arrival_time))
        self.process_table.setItem(row_position, 2, QTableWidgetItem(execution_time))
        
        # Atualizar o nome do próximo processo
        self.next_process_name = chr(ord(self.next_process_name) + 1)
        
        # Atualizar o campo de texto para visualizar o nome do processo atual
        self.process_name_label.setText(f'Processo Atual: {self.next_process_name}')

        # Limpar os campos de entrada
        self.arrival_input.clear()
        self.execution_input.clear()
        
    def execute_scheduling(self):
        algorithm = self.algorithm_combo.currentText()  # Obtém o algoritmo selecionado
        
        # # Remove o campo de entrada para o quantum caso o algoritmo selecionado não seja Round Robin
        # if algorithm != "Round Robin" and hasattr(self, 'quantum_input'):
        #     self.quantum_input.deleteLater()
        #     del self.quantum_input
        
        # Adiciona o campo de entrada para o quantum caso o algoritmo selecionado seja Round Robin
        if algorithm == "Round Robin" and not hasattr(self, 'quantum_input'):
            self.quantum_input = QLineEdit()
            self.quantum_input.setPlaceholderText('Quantum')
            self.input_layout.addWidget(self.quantum_input)
        
        # Limpa o gráfico antes de executar o novo escalonador
        self.bar_chart.clear()
        
        # Execução do escalonamento de acordo com o algoritmo escolhido
        if algorithm == "FCFS":
            execution_steps = self.execute_fcfs()
        elif algorithm == "SPN":
            execution_steps = self.execute_spn()
        elif algorithm == "SRT":
            execution_steps = self.execute_srt()
        elif algorithm == "Round Robin":
            if not hasattr(self, 'quantum_input'):
                # Se o usuário não especificou o quantum, não podemos continuar
                return
            quantum = int(self.quantum_input.text())
            execution_steps = self.execute_round_robin(quantum)
        
        # Atualiza o gráfico de barras com os processos em execução em cada passo de tempo
        self.update_bar_chart(execution_steps)

    def execute_fcfs(self):
        # Obtém os dados dos processos da tabela de entrada
        processes = self.get_processes_data()
        
        # Ordena os processos pelo tempo de chegada
        processes.sort(key=lambda x: x[1])
        
        # Executa o escalonamento FCFS
        return self.run_scheduling(processes)
        
    def execute_spn(self):
        # Obtém os dados dos processos da tabela de entrada
        processes = self.get_processes_data()
        
        # Ordena os processos pelo tempo de chegada
        processes.sort(key=lambda x: x[1])
        
        # Executa o escalonamento SPN
        return self.run_scheduling(processes, shortest_remaining_time=True)
        
    def execute_srt(self):
        # Obtém os dados dos processos da tabela de entrada
        processes = self.get_processes_data()
        
        # Executa o escalonamento SRT
        return self.run_scheduling(processes, shortest_remaining_time=True)
        
    def execute_round_robin(self, quantum):
        # Obtém os dados dos processos da tabela de entrada
        processes = self.get_processes_data()
        
        # Calcula o tempo total de execução
        total_execution_time = sum(process[2] for process in processes)
        
        # Executa o escalonamento Round Robin
        return self.run_round_robin(processes, total_execution_time, quantum)
    
    def run_scheduling(self, processes, shortest_remaining_time=False):
        # Cria uma lista para armazenar os processos em execução a cada passo de tempo
        execution_steps = [[] for _ in range(10)]
        
        # Executa o escalonamento
        current_time = 0
        while processes:
            available_processes = [process for process in processes if process[1] <= current_time]
            if available_processes:
                if shortest_remaining_time:
                    shortest_process = min(available_processes, key=lambda x: x[2])
                else:
                    shortest_process = available_processes[0]  # First come, first served
                process_name, arrival_time, execution_time = shortest_process
                processes.remove(shortest_process)
                for _ in range(execution_time):
                    execution_steps[current_time].append(process_name)
                    current_time += 1
            else:
                current_time += 1
        
        return execution_steps

    def run_round_robin(self, processes, total_execution_time, quantum):
        # Cria uma lista para armazenar os processos em execução a cada passo de tempo
        execution_steps = [[] for _ in range(total_execution_time)]
        
        # Copia dos processos para evitar modificar a lista original
        processes = processes.copy()
        
        # Executa o escalonamento Round Robin
        current_time = 0
        while processes:
            executed_any_process = False  # Variável para verificar se algum processo foi executado neste passo de tempo
            for process in list(processes):  # Itera sobre uma cópia da lista de processos
                process_name, arrival_time, execution_time = process
                if arrival_time <= current_time and execution_time > 0:
                    executed_any_process = True
                    for _ in range(min(execution_time, quantum)):
                        if current_time < total_execution_time:
                            execution_steps[current_time].append(process_name)
                        execution_time -= 1
                        current_time += 1
                    if execution_time <= 0:
                        processes.remove(process)
            if not executed_any_process:
                current_time += 1
            if current_time >= total_execution_time:  # Verifica se ultrapassamos o tempo total de execução
                break
                    
        return execution_steps

    def update_bar_chart(self, execution_steps):
        ax = self.bar_chart.add_subplot(111)
        ax.clear()  # Limpa o gráfico anterior
        
        # Extrai os nomes dos processos
        process_names = sorted({process for step in execution_steps for process in step}, reverse=True)
        
        # Define os eixos
        ax.set_yticks(range(len(process_names)))
        ax.set_yticklabels(process_names)
        ax.set_xlabel('Tempo')
        ax.set_ylabel('Processos')
        ax.set_title('Execução dos Processos')
        
        # Cria uma paleta de cores para os processos
        colors = plt.cm.viridis(np.linspace(0, 1, len(process_names)))
        color_dict = {process: color for process, color in zip(process_names, colors)}
        
        # Plota as barras de execução
        for time, step in enumerate(execution_steps):
            for i, process in enumerate(process_names):
                if process in step:
                    ax.bar(time, 1, bottom=len(process_names) - i - 1, align='center', color=color_dict[process])
        
        # Redesenha o gráfico
        self.bar_chart_canvas.draw()

    def clear_simulation(self):
        # Limpa a tabela de processos
        self.process_table.clearContents()
        self.process_table.setRowCount(0)
        
        # Limpa o gráfico de barras
        self.bar_chart.clear()
        self.bar_chart_canvas.draw()
        
        # Reinicia o nome do próximo processo
        self.next_process_name = 'A'
        
        # Reinicia o texto do processo atual
        self.process_name_label.setText('Processo Atual: A')
        
    def get_processes_data(self):
        processes = []
        for row in range(self.process_table.rowCount()):
            process_name = self.process_table.item(row, 0).text()
            arrival_time = int(self.process_table.item(row, 1).text())
            execution_time = int(self.process_table.item(row, 2).text())
            processes.append((process_name, arrival_time, execution_time))
        return processes

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
