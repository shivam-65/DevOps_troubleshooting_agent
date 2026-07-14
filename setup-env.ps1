# Environment Setup Script for AI DevOps Incident Commander
# Run this script in PowerShell as Administrator for permanent setup

Write-Host "=== AI DevOps Incident Commander - Environment Setup ===" -ForegroundColor Cyan
Write-Host ""

# Function to check if a path exists
function Test-PathExists {
    param([string]$Path, [string]$Name)
    if (Test-Path $Path) {
        Write-Host "Found $Name at: $Path" -ForegroundColor Green
        return $true
    } else {
        Write-Host "$Name not found at: $Path" -ForegroundColor Red
        return $false
    }
}

# Check common installation paths
$javaPaths = @(
    "C:\Program Files\Java\jdk-17.0.19",
    "C:\Program Files\Java\jdk-17",
    "C:\Program Files\Eclipse Adoptium\jdk-17.0.19-hotspot",
    "C:\Program Files\Eclipse Adoptium\jdk-17"
)

$mavenPaths = @(
    "C:\Program Files\Apache\maven\apache-maven-3.9.9",
    "C:\Program Files\Apache\maven\apache-maven-3.9.8",
    "C:\Program Files\Apache\maven\apache-maven-3.9.7",
    "C:\Program Files\Apache\maven\apache-maven-3.9.6",
    "C:\Program Files\Apache\maven"
)

$dockerPaths = @(
    "C:\Program Files\Docker\Docker\resources\bin",
    "C:\Program Files\Docker\Docker"
)

# Find Java
$javaPath = $null
foreach ($path in $javaPaths) {
    if (Test-PathExists $path "Java") {
        $javaPath = $path
        break
    }
}

# Find Maven
$mavenPath = $null
foreach ($path in $mavenPaths) {
    if (Test-PathExists $path "Maven") {
        $mavenPath = $path
        break
    }
}

# Find Docker
$dockerPath = $null
foreach ($path in $dockerPaths) {
    if (Test-PathExists $path "Docker") {
        $dockerPath = $path
        break
    }
}

Write-Host ""
Write-Host "=== Setting up Environment Variables ===" -ForegroundColor Cyan
Write-Host ""

# Set JAVA_HOME
if ($javaPath) {
    [Environment]::SetEnvironmentVariable("JAVA_HOME", $javaPath, "User")
    Write-Host "Set JAVA_HOME to: $javaPath" -ForegroundColor Green
    
    # Add to PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $javaBinPath = "$javaPath\bin"
    if ($currentPath -notlike "*$javaBinPath*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$javaBinPath", "User")
        Write-Host "Added $javaBinPath to PATH" -ForegroundColor Green
    } else {
        Write-Host "$javaBinPath already in PATH" -ForegroundColor Yellow
    }
} else {
    Write-Host "Java not found. Please install Java 17 and update JAVA_HOME manually." -ForegroundColor Yellow
}

# Set MAVEN_HOME
if ($mavenPath) {
    [Environment]::SetEnvironmentVariable("MAVEN_HOME", $mavenPath, "User")
    Write-Host "Set MAVEN_HOME to: $mavenPath" -ForegroundColor Green
    
    # Add to PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $mavenBinPath = "$mavenPath\bin"
    if ($currentPath -notlike "*$mavenBinPath*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$mavenBinPath", "User")
        Write-Host "Added $mavenBinPath to PATH" -ForegroundColor Green
    } else {
        Write-Host "$mavenBinPath already in PATH" -ForegroundColor Yellow
    }
} else {
    Write-Host "Maven not found. Please install Maven 3.9+ and update MAVEN_HOME manually." -ForegroundColor Yellow
}

# Add Docker to PATH
if ($dockerPath) {
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -notlike "*$dockerPath*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$dockerPath", "User")
        Write-Host "Added $dockerPath to PATH" -ForegroundColor Green
    } else {
        Write-Host "$dockerPath already in PATH" -ForegroundColor Yellow
    }
} else {
    Write-Host "Docker not found. Please install Docker Desktop." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup Complete" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Close and reopen your terminal for changes to take effect!" -ForegroundColor Yellow
Write-Host ""
Write-Host "After reopening, verify installations with:" -ForegroundColor White
Write-Host "  java -version"
Write-Host "  mvn -version"
Write-Host "  docker --version"
Write-Host "  docker-compose --version"
Write-Host "  node --version"
Write-Host "  python --version"
