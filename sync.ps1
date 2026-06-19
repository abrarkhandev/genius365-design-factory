# Genius365 Design Factory - install or update every design profile (Windows PowerShell).
# First run installs all profiles + aliases; later runs update them.
# Run it after every `git pull`.
#   PS> .\sync.ps1

$repo = $PSScriptRoot
$profiles = @(
  "landing-page-studio", "business-pack-studio", "linkedin-studio",
  "email-newsletter-studio", "print-editorial-studio", "image-prompter",
  "image-asset-lab", "intake-strategist", "design-director", "design-qa"
)

foreach ($p in $profiles) {
  hermes profile info $p *> $null
  if ($LASTEXITCODE -eq 0) {
    Write-Host "==> updating $p"
    hermes profile update $p -y
  } else {
    Write-Host "==> installing $p"
    hermes profile install "$repo\profiles\$p" --alias -y
  }
}

Write-Host ""
Write-Host "Done. On a fresh machine, also copy .env.example to ~/.hermes/.env and paste the keys."
Write-Host "Your installed profiles now also appear in the Hermes desktop app."
