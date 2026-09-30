# Run script to setup virtualenv, install deps and run analise.py
# Usage: In PowerShell run: .\run.ps1
# If execution policy blocks, run: powershell -ExecutionPolicy Bypass -File .\run.ps1

# Allow this script to run for this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

try {
    $venvPath = ".\.venv"

    if (-Not (Test-Path $venvPath)) {
        Write-Output "Criando virtualenv em .venv..."
        python -m venv .venv
    } else {
        Write-Output "Virtualenv já existe: .venv"
    }

    Write-Output "Ativando virtualenv..."
    & .\.venv\Scripts\Activate.ps1

    Write-Output "Atualizando pip e instalando dependências..."
    python -m pip install --upgrade pip
    python -m pip install -r .\requirements.txt

    Write-Output "Rodando analise.py..."
    python .\analise.py
    Write-Output "Fim. Se o plot não aparecer, confira o renderer do Plotly ou instale 'kaleido' para exportar imagens." 
}
catch {
    Write-Error "Erro ao executar: $_"
    exit 1
}
