'''
    Bruno Gandolfi de Souza RA 196799
    Projeto 1 PO - Designação
'''
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import pandas as pd

#Criando a nossa classe de modelo
modelo = gp.Model("Problema_da_Designação_Projeto_1")

#Definindo os arâmetros do problema (Dados de entrada)
#Arquivo de dados de entrada
arquivo = "BD designação.txt"

# Numero de periodos
p = 4

# Numero de trabalhadores mínimos para fazer a tarefa j
b = np.loadtxt(arquivo, skiprows=1, usecols=1,  max_rows=15)
#b = [2,3,2,2,2,3,4,4,5,2,1,2,1,3,1]

#Custo de designar um trabalhador i a tarefa j
c = np.loadtxt(arquivo, skiprows=19, usecols=range(1, 16), max_rows=60)

#Custo de contratação do trabalhador i
h = np.loadtxt(arquivo, skiprows=82, usecols=1)

m, n = c.shape

#Definindo as variáveis de decisão
x = {}
for i in range(m):
    for j in range(n):
        for t in range(p):
            x[i,j,t]= modelo.addVar(vtype= gp.GRB.BINARY, name = "x%d%d%d"%(i,j,t))
        
y = {}
for i in range(m):
    y[i] = modelo.addVar(vtype= gp.GRB.BINARY, name = "y%d"%(i))
        
#Função-Objetivo
custo_min = modelo.setObjective(gp.quicksum(h[i] * y[i] for i in range(m)) +
                   gp.quicksum(c[i][j] * x[i, j, t] for i in range(m) for j in range(n) for t in range(p)),
                   GRB.MINIMIZE)

# Restrição 1: Número mínimo de trabalhadores por tarefa
for j in range(n):
    for t in range(p):
        modelo.addConstr(gp.quicksum(x[i, j, t] for i in range(m)) >= b[j])

# Restrição 2: Trabalhador só é designado se for contratado
for i in range(m):
    for j in range(n):
        for t in range(p):
            modelo.addConstr(x[i, j, t] <= y[i])
            
# Restrição 3: Trabalhador contratado é designado em todos os períodos
for i in range(m):
    for t in range(p):
        modelo.addConstr(gp.quicksum(x[i, j, t] for j in range(n)) >= y[i])
        
# Restrição 4: Trabalhador não pode repetir a mesma tarefa em períodos consecutivos
for i in range(m):
    for j in range(n):
        for t in range(p - 1):
            modelo.addConstr(x[i, j, t] + x[i, j, t+1] <= 1)
            
# Otimizar
modelo.optimize()

# Impressão dos resultados
if modelo.status == GRB.OPTIMAL:
    #Imprimir o valor da função objetivo
    print("\nSolução Ótima:")
    print(f"Custo mínimo: {modelo.ObjVal}")
    for i in range(m):
        if y[i].x == 1:
            print(f"Trabalhador {i+1} contratado.")
            for j in range(n):
                for t in range(p):
                    if x[i, j, t].x == 1:
                        print(f"  - Designado para tarefa {j+1} no período {t+1}.")
                        
    print("\nTrabalhadores contratado: ", end='')
    for i in range(m):
        if y[i].x == 1:
            print(f"{i+1}, ", end='')

    #Adicional para exibição de forma clara e compreensivel
    resultados = {t: [] for t in range(p)} 
    trabalhadores_contratados = set()  

    for t in range(p):
        
        for j in range(n):
            for i in range(m):
                if x[i, j, t].x == 1:
                    custo_designacao = c[i][j]
                    
                    # Adiciona o custo de contratação somente se este trabalhador ainda não foi registrado como contratado
                    if i not in trabalhadores_contratados:
                        custo_contratacao = h[i]
                        trabalhadores_contratados.add(i)  
                    else:
                        custo_contratacao = 0
                    
                    custo_total = custo_contratacao + custo_designacao
                    
                    # Armazena os dados no dicionário para o DataFrame
                    resultados[t].append({
                        "Trabalhador": i + 1,
                        "Tarefa": j + 1,
                        "Custo Designação": custo_designacao,
                        "Custo Contratação": custo_contratacao,
                        "Custo Total": custo_total
                    })

   # Salvar dados no aquivo xlsx ( Comentado para não criar o arquivo assim que rodar)
    '''with pd.ExcelWriter("resultados_designacao.xlsx") as writer:
        startcol = 0  
        for t in range(p):
            df_periodo = pd.DataFrame(resultados[t])
            df_periodo.to_excel(writer, sheet_name="Resultados", startcol=startcol, index=False)
            startcol += df_periodo.shape[1] + 1 '''