# Script para inserir médico na API
# Uso: .\inserir_medico.ps1

$body = @{
    nome = "Dr. João Silva"
    CRM = "12345-SP"
    especialidade = "Cardiologia"
    horario = "08:00-12:00"
    genero = "M"
} | ConvertTo-Json

Write-Host "Enviando requisição..." -ForegroundColor Yellow
Write-Host "Body: $body" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri http://localhost:5000/medicos -Method POST -ContentType "application/json" -Body $body
    Write-Host "`nSucesso!" -ForegroundColor Green
    Write-Host ($response | ConvertTo-Json -Depth 10)
} catch {
    Write-Host "`nErro:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    if ($_.ErrorDetails.Message) {
        Write-Host $_.ErrorDetails.Message
    }
}

