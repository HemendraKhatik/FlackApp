# Author:		kaloneh <kaloneh@gmail.com>
# Github:		https://github.com/kaloneh
# Description:	This script runs the FlackApp (link: https//github.com/HemendraKhatik/FlackApp)


param (
	[Hashtable] $DotEnvConfig = @{},
	[string] $DotEnvFile = '.\.env',
	[string] $RequirementsFile = 'requirements.txt',
	[Switch] $Help,
	[Switch] $Install,
	[Switch] $Run,
	[Switch] $Test
)



function Set-Environments {
	if (($DotEnvConfig -NE $null) -AND ($DotEnvConfig.Keys.Length -GT 0)){
		$DotEnvConfig.Keys | foreach {
			[Environment]::SetEnvironmentVariable($_,$DotEnvConfig['$_'])
		}
	} elseif (Test-Path $DotEnvFile) {
		cat $DotEnvFile | foreach {if(![string]::IsNullOrEmpty($_.Trim())){
			try{
				[string]$k,[string]$v = $_.Split("=")
				[Environment]::SetEnvironmentVariable($k.Trim(),$v.Trim())
			} catch {<#TO DO#>
			}
		}}
	}
}

function Find-PyExecutableInPath {
	$env:Path.Split(";") | foreach {
		if((Test-Path (Join-Path $_ "python.exe")) -OR (Test-Path (Join-Path $_ "python3*.exe"))){
			if(Test-Path (Join-Path $_ "python3*.exe")){
				$exe=(ls (Join-Path $_ "python3*.exe"))[0].FullName
			} else{$exe=(Join-Path $_ "python.exe")}
			try{
				if(([Int32](iex "$exe -c 'import sys; print(sys.version_info.major)'") -eq 3) -AND
					([Int32](iex "$exe -c 'import sys; print(sys.version_info.minor)'") -ge 6)){return $exe}
			} catch {<#TO DO#>
			}
		}
	}
	$null
}

function Get-PyExecutable {
	$PyEXE = Find-PyExecutableInPath
	if ($PyEXE -eq $null){
		$msg = @("The Python executable`'s missed in the path.",
				"If you want to download and install it automatically confirm `nwith y(es)",
				"unless after setting the path environment variable run this script again. `[y(es)/N(o)`]")
		$y = Read-Host "$msg"
		if ($y -match "[Yy](?:es)?") {
			$ExecutableProcess = Download-Python
			Handle-Process -ExecutableProcess $ExecutableProcess
			$PyEXE = Find-PyExecutableInPath
		}
	}
	$PyEXE
}

function Download-Python {
	[string]$url = "https://www.python.org/downloads/release/python-2717/"
	Write-Warning "Downloading Executable Python From:`t$url"
	if ($env:TEMP -eq $null) {$env:TEMP = Join-Path $env:SystemDrive 'temp'}
	$flackappTempDir = Join-Path $env:TEMP "flackapp"
	$tempDir = Join-Path $flackTempDir "flackapp"
	if (![System.IO.Directory]::Exists($tempDir)) {[void][System.IO.Directory]::CreateDirectory($tempDir)}
	$PyEXE = Join-Path $tempDir "python3.exe"

	$wc = new-object System.Net.WebClient
	$defaultCreds = [System.Net.CredentialCache]::DefaultCredentials
	if ($defaultCreds -ne $null) {
		$wc.Credentials = $defaultCreds
	}
	$wc.DownloadFile($url, $PyEXE)
}

<#
	.SYNOPSIS
	Install an executable python file and don't interact with user during installation.
	
	.PARAMETER ExecutableProcess
	Python msi/exe file that is contains all requirements' builtins to init a python project.
	
	.PARAMETER $Params
	Python installation parameters
#>
function Handle-Process {
	param ($ExecutableProcess,$Params="")
	try{
		$process = New-Object System.Diagnostics.Process
		$process.StartInfo = New-Object System.Diagnostics.ProcessStartInfo($ExecutableProcess, $Params)
		$process.StartInfo.RedirectStandardOutput = $true
		$process.StartInfo.UseShellExecute = $false
		$process.StartInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
		$process.Start() | Out-Null
		$process.BeginOutputReadLine()
		$process.WaitForExit()
		$exitCode = $process.ExitCode
		$process.Dispose()
		if($exitCode -ne $null){
			throw "The process throws a non-zero code, that is, the installation process is unfinished.`nTo install manually run `'$output`'"
		}
		return $true
	} catch{<#TO DO#>
	}
	$false
}

function Install-Requirements {
	param ($PyEXE)
	try{
		if($PyEXE -ne $null){
			iex "$PyEXE -c 'import pip;print(pip3.__version__)'" -OutVariable __version__ > $NOP
			if($__version__ -match "^\d+[\.\d]*$"){
				iex "pip install -r $RequirementsFile"
			} else {
				Write-Output "FindingPIP..."
				$JFPIP = Start-Job -Name "FindingPIP" -ScriptBlock {NOP}
				icm -ScriptBlock {Get-PIP -PyEXE $PyEXE} -OutVariable $pip
				Wait-Job -Job $JFPIP
				Get-Job | foreach{if($_.Name -eq "FindingPIP"){Remove-Job $_}}
				iex "pip install -r $RequirementsFile"
			}
		} else {Write-Output "PyEXE is null!"}
	} catch {<#TO DO #>
		Write-Debug "Install-Requirements thrown an exception:"
		Write-Error $Error[0]
	}
}

function Get-PIP {
	param ($PyEXE)
	$JFPIP2 = Start-Job -Name "GettingPIP" -ScriptBlock {NOP}
	iex "$PyEXE -c 'import pip; print(pip4.__spec__.name)'" -OutVariable pip
	Wait-Job -Job $JFPIP2
	Get-Job | foreach {if($_.Name -eq "GettingPIP"){Remove-Job $_}}
	Get-Job
	if(-not ($pip -match "pip[3]?")){
		if(-NOT(Test-Path $env:TEMP)){$env:TEMP="tmp"}
		try {
			Write-Warning "Downloading get-pip to `t`"($($env:TEMP))`""
			iex 'curl -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "$($env:TEMP)\get-pip.py" -Credential $env:USERNAME'
			iex "$PyEXE $($env:TEMP)\get-pip.py"
			return 'pip'
		} catch{<#TO DO#>
		}
	}
	return 'pip'
}

function Run-Test {
	# TO DO
	iex "pytest"
}

<#

		
		.SYNOPSIS
		Running Flask Application
		
		.DESCRIPTION
		It's gonna set the required environment variable and then install required packages.
		Finally, if everythings go fine it runs the flask application.

		.PARAMETER DotEnvConfig
		The `Hashtable` environment key-value pairs required by flask application.

		.PARAMETER DotEnvFile
		If DotEnvConfig isn't set it's looking for config file in which contains key-value pairs. The default value is .env file.
		
		.PARAMETER RequirementsFile
		The file with required packages to run flask application.
		
		.PARAMETER Help
		Show help messages
		
		.PARAMETER Install
		If the Install flag is on, it means before running the flask application the requirements should have installed.
		
		.PARAMETER Run
		If it's applied without Install flag it runs the Flask application without checking the requirements.
		
		.PARAMETER Test
		Test the Flask application by executing `pytest` that is necessary to be listed in requirements file.

		.OUTPUTS
		System.String in seperate line of standard output and System.Process in user kernel to run the application.
		
		.EXAMPLE
		C:\FlackApp> .\runapp.ps1 -Help
		Print a full list of arguments and examples

		.EXAMPLE
		C:\FlackApp> .\runapp.ps1 -Install -Run
		Installing requirements and the run the application

		.EXAMPLE
		C:\FlackApp> .\runapp.ps1 -DotEnvConfig @{FLASK_APP=application.py;DATABASE_URL=postgres://username:password@host:port/database} -Run
		It sets the environment variable from the DotEnvConfig Hashtable and then run the Flask application.

		.EXAMPLE
		C:\FlackApp> .\runapp.ps1 -DotEnvFile .env_example -RequirementsFile requirements.txt -Install -Run
		It sets the environment variables from .env_example file and then install requirements
		from requirements.txt and finally, it runs the Flask application

		.LINK
		https://github.com/HemendraKhatik/FlackApp
		https://github.com/kaloneh/FlackApp

		.LINK
		Set-ExecutionPolicy
		Invoke-Command
#>
function Run-FlackApp {
	# TO DO
	<#
		.FORWARDHELPTARGETNAME Get-Help
		.FORWARDHELPCATEGORY Cmdlet
	#>
	[CmdletBinding(DefaultParameterSetName='AllUsersView')]
	# param(
		# [Parameter(Position=0, ValueFromPipelineByPropertyName=$true)]
		# [System.String]
		# ${Name}
	# )
	param (
		[Hashtable] $DotEnvConfig = @{},
		[string] $DotEnvFile = '.\.env',
		[string] $RequirementsFile = 'requirements.txt',
		[Switch] $Help,
		[Switch] $Install,
		[Switch] $Run,
		[Switch] $Test
	)
}

function Invoke-All {
	if($Run -OR $Install -OR $Test){
		try{
			Write-Output "Setting Environment Variables ..."
			Set-Environments
			Write-Output "Looking for a Python executable instance ..."
			$JFP = Start-Job -Name "FindingPython" -ScriptBlock {NOP}
			icm -ScriptBlock {Get-PyExecutable} -OutVariable PyEXE
			Wait-Job -Job $JFP #-Name "FindingPython"
			Get-Job | foreach{if($_.Name -eq 'FindingPython'){Remove-Job $_}}
			Write-Output "Python executable is set to `"$PyEXE`""
			if ($PyEXE -ne $null){ 
				if ($Install) {
					Write-Output "Installing Requirements ..."
					icm -ScriptBlock {Install-Requirements -PyEXE $PyEXE}
				}
				if($Run) {
					Write-Output "Running Flack ..."
					iex "flask run"
				} elseif ($Test) {
					Write-Output "Running pytest ..."
					Run-Test
				}
				
			}
		} catch {<#TO DO#>
			Write-Debug "Invoke-All thrown an exception:"
			Write-Output $Error[0]
		}
	} elseif($Help) {
		Get-Help Run-FlackApp -Full | more
	} else {
		Get-Help Run-FlackApp -Examples | more
	}
}

Invoke-All
# Get-PyExecutable