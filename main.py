import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


df = pd.read_csv('transacoes.csv', encoding='latin1')


df['valor'] = df.groupby('estado_cliente')['valor'].transform(
    lambda x: x.fillna(x.median())
)


df['plataforma'] = 'Mobile'



df['data_transacao'] = pd.to_datetime(df['data_transacao'])
df['data_transacao'] = df['data_transacao'].dt.tz_localize('America/Sao_Paulo')


df['dia_semana'] = df['data_transacao'].dt.day_name()
df['mes'] = df['data_transacao'].dt.month


df = df.drop_duplicates()



filtro = (
    (df['mes'] == 9)
    & ((df['estado_cliente'] == 'SP') | (df['estado_cliente'] == 'RJ'))
    & (df['valor'] > 5000)
)
df_setembro = df[filtro]



risco_dict = {
    'C100': 'Baixo',
    'C101': 'Alto',
    'C102': 'Médio',
    'C103': 'Alto',
    'C104': 'Baixo',
}

df['nivel_risco'] = df['id_cliente'].map(risco_dict)

tabela_pivot = pd.pivot_table(
    df,
    values='valor',
    index='mes',
    columns='nivel_risco',
    aggfunc='sum',
    margins=True,
    margins_name='Total',
)

print('Tabela Dinâmica:')
print(tabela_pivot)



media_estado = df.groupby('estado_cliente')['valor'].transform('mean')
desvio_estado = df.groupby('estado_cliente')['valor'].transform('std')

df['z_score'] = (df['valor'] - media_estado) / desvio_estado


anomalias = df[df['z_score'] > 2.5]
print('\nAnomalias encontradas:')
print(anomalias[['id_cliente', 'estado_cliente', 'valor', 'z_score']])



df['data_dia'] = df['data_transacao'].dt.date
diario = df.groupby('data_dia')['valor'].sum().reset_index()


diario['media_movel'] = diario['valor'].rolling(7).mean()


fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(diario['data_dia'], diario['valor'], label='Valor Diário')
ax.plot(
    diario['data_dia'], diario['media_movel'], label='Média Móvel (7 dias)'
)

ax.set_ylim(bottom=0)
ax.set_title('Desempenho Diário de Transações')
ax.set_xlabel('Data')
ax.set_ylabel('Valor Total (R$)')
ax.legend()
ax.grid(True)

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()