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
        main_layout.setMenuBar(self.menu_bar)
        
        # Campo de texto para visualizar o nome do processo atual
        self.process_name_label = QLabel('Processo Atual: A')
        main_layout.addWidget(self.process_name_label)
        
        # Campos de entrada
        self.arrival_input = QLineEdit()
        self.arrival_input.setPlaceholderText('Tempo de Chegada')
        input_layout.addWidget(self.arrival_input)
        
        self.execution_input = QLineEdit()
        self.execution_input.setPlaceholderText('Tempo de Execução')
        input_layout.addWidget(self.execution_input)
        
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["FCFS", "SPN", "SRT", "Round Robin"])
        input_layout.addWidget(self.algorithm_combo)

        self.quantum_input = QLineEdit()
        self.quantum_input.setPlaceholderText('Quantum')
        input_layout.addWidget(self.quantum_input)
        
        main_layout.addLayout(input_layout)
        
        # Botões
        self.add_button = QPushButton('Adicionar Processo')
        self.add_button.clicked.connect(self.add_process)
        main_layout.addWidget(self.add_button)
        
        self.execute_button = QPushButton('Executar')
        self.execute_button.clicked.connect(self.execute_scheduling)
        main_layout.addWidget(self.execute_button)
        
        self.clear_button = QPushButton('Limpar')
        self.clear_button.clicked.connect(self.clear_simulation)
        main_layout.addWidget(self.clear_button)
        
        # Tabela de processos
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(3)
        self.process_table.setHorizontalHeaderLabels(['Nome', 'Tempo de Chegada', 'Tempo de Execução'])
        main_layout.addWidget(self.process_table)
        
        # Gráfico de barras
        self.bar_chart = plt.figure()
        self.bar_chart_canvas = FigureCanvas(self.bar_chart)
        main_layout.addWidget(self.bar_chart_canvas)
        
        self.setLayout(main_layout)
        self.next_process_name = 'A'
        
    def create_menu_bar(self):
        self.menu_bar = QMenuBar()
        file_menu = self.menu_bar.addMenu('Arquivo')
        exit_action = QAction('Sair', self)
        exit_action.setShortcut('Esc')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = self.menu_bar.addMenu('Ajuda')
        about_action = QAction('Sobre', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
    def show_about_dialog(self):
        about_text = "Escalonador de processos 1.0\nAutor: Heder Dorneles Soares\nCurso de Análise e Desenvolvimento de Sistemas."
        QMessageBox.about(self, 'Sobre', about_text)
        
    def add_process(self):
        name = self.next_process_name
        arrival_time = self.arrival_input.text()
        execution_time = self.execution_input.text()
        
        row_position = self.process_table.rowCount()
        self.process_table.insertRow(row_position)
        self.process_table.setItem(row_position, 0, QTableWidgetItem(name))
        self.process_table.setItem(row_position, 1, QTableWidgetItem(arrival_time))
        self.process_table.setItem(row_position, 2, QTableWidgetItem(execution_time))
        
        self.next_process_name = chr(ord(self.next_process_name) + 1)
        self.process_name_label.setText(f'Processo Atual: {self.next_process_name}')
        
        self.arrival_input.clear()
        self.execution_input.clear()
        
    def execute_scheduling(self):
        algorithm = self.algorithm_combo.currentText()
        
        if algorithm == "Round Robin" and not self.quantum_input.text():
            return
        
        self.bar_chart.clear()
        
        if algorithm == "FCFS":
            execution_steps = self.execute_fcfs()
        elif algorithm == "SPN":
            execution_steps = self.execute_spn()
        elif algorithm == "SRT":
            execution_steps = self.execute_srt()
        elif algorithm == "Round Robin":
            quantum = int(self.quantum_input.text())
            execution_steps = self.execute_round_robin(quantum)
        
        self.update_bar_chart(execution_steps)

    def execute_fcfs(self):
        processes = self.get_processes_data()
        processes.sort(key=lambda x: x[1])
        return self.run_scheduling(processes)
        
    def execute_spn(self):
        processes = self.get_processes_data()
        processes.sort(key=lambda x: x[1])
        return self.run_scheduling(processes, shortest_remaining_time=True)
        
    def execute_srt(self):
        processes = self.get_processes_data()
        return self.run_scheduling(processes, shortest_remaining_time=True)
        
    def execute_round_robin(self, quantum):
        processes = self.get_processes_data()
        total_execution_time = sum(process[2] for process in processes)
        return self.run_round_robin(processes, total_execution_time, quantum)
    
    def run_scheduling(self, processes, shortest_remaining_time=False):
        execution_steps = [[] for _ in range(10)]
        current_time = 0
        while processes:
            available_processes = [process for process in processes if process[1] <= current_time]
            if available_processes:
                if shortest_remaining_time:
                    shortest_process = min(available_processes, key=lambda x: x[2])
                else:
                    shortest_process = available_processes[0]
                process_name, arrival_time, execution_time = shortest_process
                processes.remove(shortest_process)
                for _ in range(execution_time):
                    execution_steps[current_time].append(process_name)
                    current_time += 1
            else:
                current_time += 1
        return execution_steps

    def run_round_robin(self, processes, total_execution_time, quantum):
        execution_steps = [[] for _ in range(total_execution_time)]
        processes = processes.copy()
        current_time = 0
        while processes:
            executed_any_process = False
            for process in list(processes):
                process_name, arrival_time, execution_time = process
                if arrival_time <= current_time and execution_time > 0:
                    executed_any_process = True
                    time_slice = min(execution_time, quantum)
                    for _ in range(time_slice):
                        if current_time < total_execution_time:
                            execution_steps[current_time].append(process_name)
                        current_time += 1
                    execution_time -= time_slice
                    if execution_time <= 0:
                        processes.remove(process)
                    else:
                        idx = processes.index(process)
                        processes[idx] = (process_name, arrival_time, execution_time)
            if not executed_any_process:
                current_time += 1
            if current_time >= total_execution_time:
                break
        return execution_steps

    def update_bar_chart(self, execution_steps):
        ax = self.bar_chart.add_subplot(111)
        ax.clear()
        process_names = sorted({process for step in execution_steps for process in step}, reverse=True)
        ax.set_yticks(range(len(process_names)))
        ax.set_yticklabels(process_names)
        ax.set_xticks(range(len(execution_steps) + 1))
        ax.set_xlabel('Tempo')
        ax.set_ylabel('Processos')
        ax.set_title('Execução dos Processos')
        ax.grid(which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.7)
        colors = plt.cm.viridis(np.linspace(0, 1, len(process_names)))
        color_dict = {process: color for process, color in zip(process_names, colors)}
        
        # Ajusta a altura dos intervalos de dados do eixo y para serem iguais
        bar_height = 1 / len(process_names)
        
        for time, step in enumerate(execution_steps):
            for process in step:
                process_index = process_names.index(process)
                ax.bar(time + 0.5, bar_height, bottom=process_index * bar_height, align='center', width=1, color=color_dict[process])
        
        ax.set_xlim(0, len(execution_steps))
        ax.set_ylim(0, 1)
        self.bar_chart_canvas.draw()

    def clear_simulation(self):
        self.process_table.clearContents()
        self.process_table.setRowCount(0)
        self.bar_chart.clear()
        self.bar_chart_canvas.draw()
        self.next_process_name = 'A'
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
