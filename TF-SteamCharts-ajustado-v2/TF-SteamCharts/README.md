# TF - SteamCharts

Instruções rápidas para preparar o ambiente e executar `analise.py` (PowerShell - Windows).

Pré-requisitos
- Python 3.8+ instalado e disponível como `python` no PATH.

Passos (PowerShell):

1) Criar e ativar um ambiente virtual (recomendado):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Instalar dependências:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3) Executar o script:

```powershell
python .\analise.py
```

Observações
- Garanta que `steamcharts.csv` esteja no mesmo diretório de `analise.py`.
- O script usa Plotly; ao executar em um ambiente sem interface gráfica, `fig.show()` pode abrir uma janela do navegador ou não dependendo do renderer padrão. Para exportar imagens sem abrir o browser, instale `kaleido` e use `fig.write_image(...)` (o script atual usa `fig.show()`).

Se quiser, eu posso: criar um script `run.ps1` para automatizar esses passos, ou tentar instalar as dependências automaticamente aqui no workspace e executar um teste simples de importação. Diga o que prefere.