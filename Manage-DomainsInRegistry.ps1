# Function to check if the registry path exists
function Test-RegistryPath {
    $path = "HKLM:\SOFTWARE\Policies\BraveSoftware\Brave\URLBlocklist"
    if (Test-Path $path) {
        $output = "Registry path found: $path"
    } else {
        $output = "Registry path not found. You can add the directory to the registry by adding a domain using the interface."
    }
    Write-Output $output
}

# Function to fetch existing domain strings from the registry
function Get-ExistingDomainsFromRegistry {
    param (
        [string]$outputFormat = "values"  # Default output format is "values"
    )
    try {
        $path = "HKLM:\SOFTWARE\Policies\BraveSoftware\Brave\URLBlocklist"
        $domainProperties = Get-ItemProperty -Path $path

        $domainInfo = @()
        foreach ($property in $domainProperties.PSObject.Properties) {
            if ($property.Name -ne "PSPath" -and $property.Name -ne "PSParentPath" -and $property.Name -ne "PSChildName" -and $property.Name -ne "PSDrive" -and $property.Name -ne "PSProvider") {
                $domainInfo += @{
                    Name = $property.Name
                    Value = $property.Value
                }
            }
        }

        if ($outputFormat -eq "names") {
            # Return domain names with TLD
            $jsonOutput = $domainInfo.Name | ConvertTo-Json -Compress
            Write-Output $jsonOutput
        } elseif ($outputFormat -eq "values") {
            # Return domain values
            $jsonOutput = $domainInfo.Value | ConvertTo-Json -Compress
            Write-Output $jsonOutput
        } elseif ($outputFormat -eq "namesAndValues") {
            # Return both names and values
            $jsonOutput = $domainInfo | ConvertTo-Json -Compress
            Write-Output $jsonOutput
        } else {
            Write-Output "Invalid output format specified."
        }
    } catch {
        Write-Output "Failed to fetch existing domain strings from the registry: $_"
    }
}

# Function to get the next available name for a new registry entry using modified binary search
function Get-NextAvailableName {
    $path = "HKLM:\SOFTWARE\Policies\BraveSoftware\Brave\URLBlocklist"
    $existingNames = Get-ItemProperty -Path $path | ForEach-Object { $_.PSObject.Properties.Name } | Where-Object { $_ -ne "(Default)" -and $_ -match '^\d+$' }

    if ($existingNames) {
        # Convert names to integers and sort them
        $existingIndexes = $existingNames | ForEach-Object { [int]$_ } | Sort-Object

        # Modified binary search algorithm to find the lowest available name
        $left = 0
        $right = $existingIndexes.Count - 1

        while ($left -le $right) {
            $mid = [math]::floor(($left + $right) / 2)

            if ($existingIndexes[$mid] -eq $mid + 1) {
                $left = $mid + 1
            } else {
                $right = $mid - 1
            }
        }

        $nextName = $left + 1
        return $nextName.ToString()
    } else {
        Write-Output "No existing names found, starting from 1"
        return "1"  # Start from 1 if no existing names found
    }
}

# Function to add domain string to the registry
function Add-DomainToRegistry {
    param (
        [string]$domainToAdd
    )

    if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Host "This script needs to be run with administrative privileges to modify the registry. Please run the script as an administrator."
        return
    }

    if ($domainToAdd) {
        try {
            $path = "HKLM:\SOFTWARE\Policies\BraveSoftware\Brave\URLBlocklist"

            # Check if the registry path exists, create it if it doesn't
            if (-not (Test-Path $path)) {
                New-Item -Path $path -Force | Out-Null
            }

            # Fetch existing domains
            $existingDomainsJson = Get-ExistingDomainsFromRegistry -outputFormat "values"
            $existingDomains = $existingDomainsJson | ConvertFrom-Json

            # Check if domain already exists
            if ($existingDomains -contains $domainToAdd) {
                Write-Host "Domain '$domainToAdd' already exists in the registry."
                return
            }

            # Generate next available name
            $newValueName = Get-NextAvailableName
            Write-Host "Adding domain '$domainToAdd' to the registry..."

            # Create a new registry property under the newly created key
            New-ItemProperty -Path $path -Name $newValueName -PropertyType String -Value $domainToAdd -Force

            $existingDomainsJson = Get-ExistingDomainsFromRegistry
            $existingDomains = $existingDomainsJson | ConvertFrom-Json

            if ($existingDomains -contains $domainToAdd) {
                Write-Host "Domain '$domainToAdd' added successfully to the registry."
            }
        } catch {
            Write-Host "Failed to add domain '$domainToAdd' to the registry: $_"
        }
    }
}


# Function to remove domain string from the registry
function Remove-DomainFromRegistry {
    param (
        [string]$indexToRemove
    )
    if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Host "This script needs to be run with administrative privileges to modify the registry. Please run the script as an administrator."
        return
    }
    if ($indexToRemove) {
        try {
            $path = "HKLM:\SOFTWARE\Policies\BraveSoftware\Brave\URLBlocklist"
            $existingDomainsJson = Get-ExistingDomainsFromRegistry -outputFormat "namesAndValues"
            $existingDomains = $existingDomainsJson | ConvertFrom-Json

            # Find the domain to remove by index
            $domainToRemove = $existingDomains | Where-Object { $_.Value -eq $indexToRemove }

            if ($domainToRemove) {
                Remove-ItemProperty -Path $path -Name $domainToRemove.Name -ErrorAction Stop
                return "Domain '$($domainToRemove.Value)' removed successfully from the registry."
            } else {
                return "No domain found at index '$indexToRemove'."
            }
        } catch {
            return "Failed to remove domain at index '$indexToRemove' from the registry: $_"
        }
    } else {
        return "No index provided to remove domain."
    }
}

# Function to check if Brave is installed
function Test-BraveInstallation {
    $braveRegistryPath = "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    $braveKey = Get-ChildItem $braveRegistryPath | Where-Object { $_.GetValue("DisplayName") -eq "Brave" }

    if ($null -ne $braveKey) {
        return $true
    } else {
        return $false
    }
}

# Main script logic
$action = $args[0]

switch ($action) {
    "1" {
        # Fetch existing domain strings from the registry
        $jsonResult = Get-ExistingDomainsFromRegistry
        Write-Output $jsonResult
    }
    "2" {
        # Add domain string to the registry
        $domainToAdd = $args[1]
        Add-DomainToRegistry $domainToAdd
    }
    "3" {
        # Remove domain string from the registry
        $indexToRemove = $args[1]
        Remove-DomainFromRegistry $indexToRemove
    }
    "4" {
        # Check if Brave is installed
        $braveInstalled = Test-BraveInstallation
        if ($braveInstalled) {
            Write-Output "Brave is installed on this system."
        } else {
            Write-Output "Brave is not installed on this system."
        }
    }
    "5" {
        # Check if the registry path exists
        $registryPathCheckResult = Test-RegistryPath
        Write-Output $registryPathCheckResult
    }
    default {
        return "Invalid action parameter. Please provide a valid action: 1 (Fetch), 2 (Add), 3 (Remove), 4 (Check Brave installation), or 5 (Check registry path)."
    }
}
