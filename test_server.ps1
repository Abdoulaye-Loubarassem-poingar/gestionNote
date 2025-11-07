# test_server.ps1
# Usage: Ouvre PowerShell dans ton projet (ex: C:\flask\gestionNote) et lance:
#   ./test_server.ps1
# (Si exécution bloquée, lancer: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)

$outfile = "audit-results.txt"
"--- Audit démarré: $(Get-Date) ---`n" | Out-File $outfile -Encoding utf8

function writeln($label, $text) {
    ("`n== $label ==`n") | Out-File $outfile -Append -Encoding utf8
    $text | Out-File $outfile -Append -Encoding utf8
}

# 1) Curl (utilise le binaire curl.exe pour éviter l'alias PowerShell)
writeln "curl.exe - HTTPS headers (https://127.0.0.1:5000/)" (try { curl.exe -I -k https://127.0.0.1:5000/ 2>&1 } catch { $_ })
writeln "curl.exe - HTTP headers (http://127.0.0.1:5000/)" (try { curl.exe -I -k http://127.0.0.1:5000/ 2>&1 } catch { $_ })
writeln "curl.exe - full response (https https + body first lines)" (try { curl.exe -i -k https://127.0.0.1:5000/ -m 10 2>&1 | Select-Object -First 200 } catch { $_ })

# 2) netstat: qui écoute sur le port 5000
writeln "netstat -ano | findstr :5000" (try { netstat -ano | findstr :5000 2>&1 } catch { $_ })

# 3) Liste des processus python ou le PID trouvé (si netstat renvoie PID)
$net = netstat -ano | findstr :5000
writeln "Raw netstat output (again) for parsing" $net
if ($net -match '\s+(\d+)$') {
    $pid = $Matches[1]
    writeln "PID detected" $pid
    try {
        $tl = tasklist /FI "PID eq $pid"
        writeln "tasklist for PID" $tl
    } catch { writeln "tasklist error" $_ }
} else {
    writeln "PID detected" "No PID parsed from netstat output. If nothing listens on :5000, server may not be running."
}

# 4) Vérifier si openssl est présent et tenter handshake (si openssl installé)
try {
    $opensslVersion = & openssl version 2>$null
    if ($LASTEXITCODE -eq 0 -or $opensslVersion) {
        writeln "openssl version" $opensslVersion
        writeln "openssl s_client test" (& openssl s_client -connect 127.0.0.1:5000 -servername 127.0.0.1 2>&1 | Select-Object -First 200)
    } else {
        writeln "openssl test" "openssl not found in PATH"
    }
} catch {
    writeln "openssl test" "openssl not found or error: $_"
}

# 5) Check proxy system
try {
    $proxy = netsh winhttp show proxy 2>&1
    writeln "netsh winhttp show proxy" $proxy
} catch { writeln "netsh proxy check error" $_ }

# 6) Get system proxy env (Chrome/Edge use system)
writeln "Environment proxy variables" (Get-ChildItem Env:HTTP_PROXY, Env:HTTPS_PROXY | Format-List | Out-String)

# 7) Firewall profiles status (read-only)
try {
    $fw = Get-NetFirewallProfile | Format-Table Name,Enabled -AutoSize | Out-String
    writeln "Get-NetFirewallProfile" $fw
} catch {
    writeln "Get-NetFirewallProfile" "Requires admin rights or PowerShell version; fallback to netsh advfirewall:"
    $fw2 = netsh advfirewall show allprofiles 2>&1
    writeln "netsh advfirewall show allprofiles" $fw2
}

# 8) Check hosts file contains 127.0.0.1 mapping for localhost
try {
    $hosts = Get-Content "$env:SystemRoot\System32\drivers\etc\hosts" -ErrorAction Stop
    writeln "hosts file (last 50 lines)" ($hosts | Select-Object -Last 50)
} catch { writeln "hosts file" "Cannot read hosts file: $_" }

# 9) Show Python version & which python executable
try {
    $py = python --version 2>&1
    $which = where.exe python 2>&1
    writeln "python --version" $py
    writeln "where python" $which
} catch { writeln "python info" $_ }

writeln "--- Audit terminé: $(Get-Date) ---" ""
Write-Host "Audit terminé. Résultats dans $outfile"
