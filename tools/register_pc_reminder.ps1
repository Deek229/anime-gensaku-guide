# 毎朝9時に gsc_reminder.py を実行（Hotmail SMTP / 自宅PC用）
$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent
$Python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $Python) { $Python = 'python' }

$Action = New-ScheduledTaskAction `
    -Execute $Python `
    -Argument "tools\gsc_reminder.py" `
    -WorkingDirectory $Root

$Trigger = New-ScheduledTaskTrigger -Daily -At '09:00'
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable

Register-ScheduledTask `
    -TaskName 'AnimeGensakuDailyReminder' `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description 'アニメ原作ガイド 毎朝タスクメール' `
    -Force | Out-Null

Write-Host '登録完了: 毎朝 9:00 に PC からメール送信'
Write-Host ".env に SMTP_USER / SMTP_PASSWORD を設定してください"
