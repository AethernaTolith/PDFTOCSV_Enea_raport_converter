# PDF to CSV Conversion App - Auto Installer and Launcher
# This PowerShell script automates the setup and launch of the PDF to CSV Conversion App

# Script Configuration
$appName = "PDF to CSV Conversion App"
$repoUrl = "https://github.com/AethernaTolith/PDFTOCSV_Enea_raport_converter.git"  # Update this with your actual repo URL
$requiredPythonVersion = "3.13.2"
$appDirectory = "$env:USERPROFILE\pdf-to-csv-app"
$pythonCommand = "python"
$pipCommand = "pip"
$envFile = "$appDirectory\.env"

# Function to check if a command exists
function Test-Command($command) {
    try {
        Get-Command $command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Function to check Python version
function Get-PythonVersion {
    try {
        $versionString = & $pythonCommand --version 2>&1
        if ($versionString -match '(\d+)\.(\d+)\.(\d+)') {
            return [version]"$($Matches[1]).$($Matches[2]).$($Matches[3])"
        }
        return $null
    } catch {
        return $null
    }
}

# Function to display colorful messages
function Write-ColorOutput($foregroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $foregroundColor
    if ($args) {
        Write-Output $args
    }
    else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Display banner
Clear-Host
Write-ColorOutput "Green" "====================================================="
Write-ColorOutput "Green" "         $appName - Installer and Launcher          "
Write-ColorOutput "Green" "====================================================="
Write-ColorOutput "Cyan" "This script will set up and run the PDF to CSV Conversion App"
Write-ColorOutput "Green" "====================================================="

# Step 1: Check for Python installation
Write-Output "`n[1/6] Checking Python installation..."
if (-not (Test-Command $pythonCommand)) {
    Write-ColorOutput "Yellow" "Python is not installed or not in PATH."
    Write-ColorOutput "Yellow" "Please install Python $requiredPythonVersion or higher from https://www.python.org/downloads/"
    Write-ColorOutput "Yellow" "Make sure to check 'Add Python to PATH' during installation."
    Write-Output "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

$pythonVersion = Get-PythonVersion
if ($pythonVersion -lt [version]$requiredPythonVersion) {
    Write-ColorOutput "Yellow" "Python version $pythonVersion detected, but version $requiredPythonVersion or higher is required."
    Write-ColorOutput "Yellow" "Please upgrade Python from https://www.python.org/downloads/"
    Write-Output "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

Write-ColorOutput "Green" "✓ Python $pythonVersion detected."

# Step 2: Create or update application directory
Write-Output "`n[2/6] Setting up application directory..."
if (Test-Path $appDirectory) {
    Write-Output "Application directory already exists."
    $updateChoice = Read-Host "Do you want to update the application? (Y/N)"
    if ($updateChoice -eq "Y" -or $updateChoice -eq "y") {
        if (Test-Path "$appDirectory\.git") {
            Set-Location $appDirectory
            git pull
            Write-ColorOutput "Green" "✓ Application updated successfully."
        } else {
            Write-ColorOutput "Yellow" "Directory exists but is not a git repository."
            $removeChoice = Read-Host "Do you want to remove and recreate it? (Y/N)"
            if ($removeChoice -eq "Y" -or $removeChoice -eq "y") {
                Remove-Item -Recurse -Force $appDirectory
                git clone $repoUrl $appDirectory
                Write-ColorOutput "Green" "✓ Repository cloned successfully."
            } else {
                Write-ColorOutput "Yellow" "Using existing directory without update."
            }
        }
    }
} else {
    # Clone the repository
    if (Test-Command "git") {
        git clone $repoUrl $appDirectory
        Write-ColorOutput "Green" "✓ Repository cloned successfully."
    } else {
        Write-ColorOutput "Yellow" "Git is not installed. Downloading ZIP archive instead."
        # Extract repo name from URL
        $repoName = $repoUrl -replace '.*/(.*?)\.git$', '$1'
        $zipUrl = $repoUrl -replace '\.git$', '/archive/refs/heads/main.zip'
        $zipPath = "$env:TEMP\$repoName.zip"
        
        # Download and extract
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath
        Expand-Archive -Path $zipPath -DestinationPath "$env:TEMP"
        New-Item -ItemType Directory -Path $appDirectory -Force | Out-Null
        Copy-Item -Path "$env:TEMP\$repoName-main\*" -Destination $appDirectory -Recurse -Force
        Remove-Item -Path $zipPath -Force
        Write-ColorOutput "Green" "✓ Application files downloaded and extracted."
    }
}

# Step 3: Set up virtual environment
Write-Output "`n[3/6] Setting up virtual environment..."
Set-Location $appDirectory
if (-not (Test-Path "$appDirectory\venv")) {
    & $pythonCommand -m venv venv
    Write-ColorOutput "Green" "✓ Virtual environment created."
} else {
    Write-Output "Virtual environment already exists."
}

# Step 4: Activate virtual environment and install requirements
Write-Output "`n[4/6] Installing required packages..."
$venvActivate = "$appDirectory\venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    . $venvActivate
    & $pipCommand install -r requirements.txt
    Write-ColorOutput "Green" "✓ Dependencies installed successfully."
} else {
    Write-ColorOutput "Red" "× Failed to activate virtual environment. Script may not work correctly."
}

# Step 5: Configure environment file
Write-Output "`n[5/6] Setting up environment file..."
if (-not (Test-Path $envFile)) {
    $apiKey = Read-Host "Enter your Gemini API key (or press Enter to skip)" -MaskInput
    if ($apiKey) {
        "GEMINI_API_KEY=$apiKey" | Out-File -FilePath $envFile -Encoding utf8
        Write-ColorOutput "Green" "✓ Environment file created with API key."
    } else {
        "GEMINI_API_KEY=" | Out-File -FilePath $envFile -Encoding utf8
        Write-ColorOutput "Yellow" "Environment file created without API key. You'll need to enter it in the app."
    }
} else {
    $updateEnvFile = Read-Host "Environment file already exists. Update API key? (Y/N)"
    if ($updateEnvFile -eq "Y" -or $updateEnvFile -eq "y") {
        $apiKey = Read-Host "Enter your Gemini API key" -MaskInput
        "GEMINI_API_KEY=$apiKey" | Out-File -FilePath $envFile -Encoding utf8
        Write-ColorOutput "Green" "✓ API key updated in environment file."
    }
}

# Step 6: Create a launcher script
Write-Output "`n[6/6] Creating launcher script..."
$launcherContent = @"
@echo off
echo Starting $appName...
cd /d "$appDirectory"
call venv\Scripts\activate.bat
streamlit run improved-pdf-to-csv.py
pause
"@

$launcherPath = "$appDirectory\Launch-PDF-to-CSV.bat"
$launcherContent | Out-File -FilePath $launcherPath -Encoding ascii
Write-ColorOutput "Green" "✓ Launcher script created."

# Create a desktop shortcut
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = "$desktopPath\PDF to CSV Conversion.lnk"
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $launcherPath
$Shortcut.WorkingDirectory = $appDirectory
$Shortcut.IconLocation = "powershell.exe"
$Shortcut.Save()
Write-ColorOutput "Green" "✓ Desktop shortcut created."

# Final message and launch option
Write-ColorOutput "Green" "`n====================================================="
Write-ColorOutput "Green" "Installation Complete! You can now run the application."
Write-ColorOutput "Green" "====================================================="
$runNow = Read-Host "Do you want to run the application now? (Y/N)"
if ($runNow -eq "Y" -or $runNow -eq "y") {
    Write-Output "Launching application..."
    & $launcherPath
} else {
    Write-ColorOutput "Cyan" "You can run the application later by:"
    Write-ColorOutput "Cyan" "1. Using the desktop shortcut 'PDF to CSV Conversion'"
    Write-ColorOutput "Cyan" "2. Running the Launch-PDF-to-CSV.bat file in $appDirectory"
}

Write-ColorOutput "Green" "`nThank you for installing $appName!"
Write-Output "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
