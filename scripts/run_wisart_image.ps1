$ErrorActionPreference = "Stop"
$WisartBaseUrl = "https://wisart.kuaileshifu.com/v1"

# Keep imagegen's GNU-style arguments out of PowerShell parameter binding.
# This is required because Windows PowerShell 5.1 treats --out as a common
# parameter abbreviation before ValueFromRemainingArguments can capture it.
$ImageGenArgs = @($args | ForEach-Object { [string]$_ })
$Check = ($ImageGenArgs.Count -eq 1 -and ($ImageGenArgs[0] -ieq "-Check" -or $ImageGenArgs[0] -ieq "--Check"))
if ($Check) {
    $ImageGenArgs = @()
}

function Get-ScopedEnvironmentValue {
    param([Parameter(Mandatory = $true)][string]$Name)

    foreach ($scope in @("Process", "User", "Machine")) {
        $value = [Environment]::GetEnvironmentVariable(
            $Name,
            [EnvironmentVariableTarget]::$scope
        )
        if (-not [string]::IsNullOrWhiteSpace($value)) {
            return [PSCustomObject]@{ Value = $value; Scope = $scope }
        }
    }
    return $null
}

function Get-CodexHome {
    $configured = Get-ScopedEnvironmentValue -Name "CODEX_HOME"
    if ($configured) {
        return $configured.Value
    }
    return (Join-Path $HOME ".codex")
}

$credential = Get-ScopedEnvironmentValue -Name "WISART_API_KEY"
if (-not $credential) {
    throw "WisArt is not configured. Set WISART_API_KEY as a Process, User, or Machine environment variable, then run this launcher again."
}
$credential.Value = $credential.Value.Trim()

$imageGenCli = Join-Path (Get-CodexHome) "skills\.system\imagegen\scripts\image_gen.py"
if (-not (Test-Path -LiteralPath $imageGenCli -PathType Leaf)) {
    throw "Bundled imagegen CLI was not found: $imageGenCli"
}

$pythonSetting = Get-ScopedEnvironmentValue -Name "WISART_PYTHON"
if (-not $pythonSetting) {
    $pythonSetting = Get-ScopedEnvironmentValue -Name "PYTHON"
}
$python = if ($pythonSetting) { $pythonSetting.Value } else { "python" }
$savedWisartKey = $env:WISART_API_KEY
$savedProbeBaseUrl = $env:OPENAI_BASE_URL
$savedProbeApiKey = $env:OPENAI_API_KEY
function Test-OpenAiSdk {
    param([Parameter(Mandatory = $true)][string]$Python)

    try {
        & $Python -c "import openai" *> $null
        return ($LASTEXITCODE -eq 0)
    }
    catch {
        return $false
    }
}

$openAiAvailable = $false
try {
    # Do not expose provider credentials or endpoints to the dependency probe.
    Remove-Item Env:WISART_API_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:OPENAI_BASE_URL -ErrorAction SilentlyContinue
    Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
    $openAiAvailable = Test-OpenAiSdk -Python $python
}
finally {
    if ($null -eq $savedWisartKey) { Remove-Item Env:WISART_API_KEY -ErrorAction SilentlyContinue }
    else { $env:WISART_API_KEY = $savedWisartKey }
    if ($null -eq $savedProbeBaseUrl) { Remove-Item Env:OPENAI_BASE_URL -ErrorAction SilentlyContinue }
    else { $env:OPENAI_BASE_URL = $savedProbeBaseUrl }
    if ($null -eq $savedProbeApiKey) { Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue }
    else { $env:OPENAI_API_KEY = $savedProbeApiKey }
}
if ($Check) {
    $sdkStatus = if ($openAiAvailable) { "available" } else { "missing (install openai in the interpreter selected by PYTHON)" }
    Write-Output "WisArt launcher configuration: credential source=$($credential.Scope); provider=https://wisart.kuaileshifu.com/v1; imagegen CLI found; openai SDK=$sdkStatus."
    exit 0
}

if (-not $ImageGenArgs -or $ImageGenArgs.Count -eq 0) {
    throw "Pass an imagegen command after the launcher, for example: generate --prompt-file <path> --size 3840x2160 --quality high --n 1 --out <path>"
}

if ($ImageGenArgs[0] -ieq "generate-batch") {
    throw "WisArt launcher does not accept generate-batch because its JSONL jobs can exceed WisArt's n limit; invoke generate separately with n between 1 and 5."
}

for ($index = 0; $index -lt $ImageGenArgs.Count; $index++) {
    $argument = $ImageGenArgs[$index]
    if ($argument -eq "--n") {
        if ($index + 1 -ge $ImageGenArgs.Count) {
            throw "WisArt n must be an integer between 1 and 5."
        }
        $rawCount = $ImageGenArgs[$index + 1]
    }
    elseif ($argument -like "--n=*") {
        $rawCount = $argument.Substring(4)
    }
    else {
        continue
    }

    [int]$count = 0
    if (-not [int]::TryParse($rawCount, [ref]$count) -or $count -lt 1 -or $count -gt 5) {
        throw "WisArt n must be an integer between 1 and 5."
    }
}

$savedBaseUrl = $env:OPENAI_BASE_URL
$savedApiKey = $env:OPENAI_API_KEY
$exitCode = 1

if (($ImageGenArgs -notcontains "--dry-run") -and -not $openAiAvailable) {
    throw "The selected Python interpreter cannot import openai. Install it in that environment (for example: uv pip install openai) or set PYTHON to an interpreter that already has the package."
}

try {
    # Restrict the provider and credential to this launcher process and its child.
    $env:OPENAI_BASE_URL = $WisartBaseUrl
    $env:OPENAI_API_KEY = $credential.Value
    Remove-Item Env:WISART_API_KEY -ErrorAction SilentlyContinue
    & $python $imageGenCli @ImageGenArgs
    $exitCode = $LASTEXITCODE
}
finally {
    if ($null -eq $savedBaseUrl) { Remove-Item Env:OPENAI_BASE_URL -ErrorAction SilentlyContinue }
    else { $env:OPENAI_BASE_URL = $savedBaseUrl }
    if ($null -eq $savedApiKey) { Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue }
    else { $env:OPENAI_API_KEY = $savedApiKey }
    if ($null -eq $savedWisartKey) { Remove-Item Env:WISART_API_KEY -ErrorAction SilentlyContinue }
    else { $env:WISART_API_KEY = $savedWisartKey }
}

exit $exitCode
