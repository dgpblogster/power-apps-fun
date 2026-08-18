# Appends the hamburger menu overlay controls to a curve screen .pa.yaml.
# Usage: .\add-menu.ps1 -File <path> -Prefix Lis -Active Lis
param(
    [Parameter(Mandatory)][string]$File,
    [Parameter(Mandatory)][string]$Prefix,
    [Parameter(Mandatory)][string]$Active
)

$items = @(
    @{ Key = "Home"; Text = "Home";            Target = "Screen1";      Accent = "RGBA(255, 255, 255, 1)" },
    @{ Key = "Lis";  Text = "Lissajous Curve"; Target = "Lissajous";    Accent = "RGBA(79, 195, 247, 1)" },
    @{ Key = "Ros";  Text = "Rose Curve";      Target = "Rose";         Accent = "RGBA(255, 107, 157, 1)" },
    @{ Key = "Spi";  Text = "Spiral";          Target = "Spiral";       Accent = "RGBA(255, 200, 87, 1)" },
    @{ Key = "Hyp";  Text = "Hypotrochoid";    Target = "Hypotrochoid"; Accent = "RGBA(124, 227, 139, 1)" }
)

$sb = [System.Text.StringBuilder]::new()
[void]$sb.AppendLine(@"
  - rec${Prefix}Scrim:
      Control: Rectangle
      Properties:
        X: =0
        Y: =0
        Width: =1366
        Height: =768
        Fill: =RGBA(0, 0, 0, 0.45)
        BorderThickness: =0
        Visible: =ctx${Prefix}Menu
        OnSelect: '=UpdateContext({ctx${Prefix}Menu: false})'
  - rec${Prefix}MenuBg:
      Control: Rectangle
      Properties:
        X: =0
        Y: =0
        Width: =300
        Height: =768
        Fill: =RGBA(24, 29, 46, 1)
        BorderThickness: =0
        Visible: =ctx${Prefix}Menu
  - lbl${Prefix}MnuTitle:
      Control: Label
      Properties:
        Text: ="Parametric Motions"
        X: =24
        Y: =28
        Width: =252
        Height: =32
        Size: =16
        FontWeight: =FontWeight.Bold
        Color: =RGBA(255, 255, 255, 1)
        Visible: =ctx${Prefix}Menu
"@)

$y = 100
foreach ($it in $items) {
    $isActive = ($it.Key -eq $Active)
    $fill = if ($isActive) { "RGBA(255, 255, 255, 0.08)" } else { "RGBA(0, 0, 0, 0)" }
    $onSelect = if ($isActive) { "'=UpdateContext({ctx${Prefix}Menu: false})'" } else { "=Navigate($($it.Target), ScreenTransition.None)" }
    [void]$sb.AppendLine(@"
  - btn${Prefix}Mnu$($it.Key):
      Control: Classic/Button
      Properties:
        Text: ="$($it.Text)"
        X: =12
        Y: =$y
        Width: =276
        Height: =48
        Size: =15
        Align: =Align.Left
        Fill: =$fill
        Color: =$($it.Accent)
        HoverFill: =RGBA(255, 255, 255, 0.12)
        HoverColor: =$($it.Accent)
        PressedFill: =RGBA(255, 255, 255, 0.05)
        PressedColor: =$($it.Accent)
        BorderThickness: =0
        RadiusTopLeft: =8
        RadiusTopRight: =8
        RadiusBottomLeft: =8
        RadiusBottomRight: =8
        Visible: =ctx${Prefix}Menu
        OnSelect: $onSelect
"@)
    $y += 56
}

Add-Content -Path $File -Value $sb.ToString().TrimEnd() -Encoding utf8NoBOM
Write-Host "Menu appended to $File"
