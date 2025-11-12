# Comandos curl para inserir dados na API de Médicos

## Windows PowerShell

### Opção 1: Usando aspas duplas com escape de backtick
```powershell
curl -X POST http://localhost:5000/medicos -H "Content-Type: application/json" -d "{\"nome\": \"Dr. João Silva\", \"CRM\": \"12345-SP\", \"especialidade\": \"Cardiologia\", \"horario\": \"08:00-12:00\", \"genero\": \"M\"}"
```

### Opção 2: Usando variável (RECOMENDADO)
```powershell
$body = @{
    nome = "Dr. João Silva"
    CRM = "12345-SP"
    especialidade = "Cardiologia"
    horario = "08:00-12:00"
    genero = "M"
} | ConvertTo-Json

curl -X POST http://localhost:5000/medicos -H "Content-Type: application/json" -d $body
```

### Opção 3: Usando Invoke-RestMethod (PowerShell nativo)
```powershell
$body = @{
    nome = "Dr. João Silva"
    CRM = "12345-SP"
    especialidade = "Cardiologia"
    horario = "08:00-12:00"
    genero = "M"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:5000/medicos -Method POST -ContentType "application/json" -Body $body
```

### Opção 4: Usando arquivo JSON
Crie um arquivo `medico.json`:
```json
{
    "nome": "Dr. João Silva",
    "CRM": "12345-SP",
    "especialidade": "Cardiologia",
    "horario": "08:00-12:00",
    "genero": "M"
}
```

Depois execute:
```powershell
curl -X POST http://localhost:5000/medicos -H "Content-Type: application/json" -d "@medico.json"
```

## Linux/Mac/Git Bash

```bash
curl -X POST http://localhost:5000/medicos \
  -H "Content-Type: application/json" \
  -d '{"nome": "Dr. João Silva", "CRM": "12345-SP", "especialidade": "Cardiologia", "horario": "08:00-12:00", "genero": "M"}'
```

