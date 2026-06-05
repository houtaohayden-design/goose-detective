; installer.iss — Inno Setup script for 鹅探长 (Goose Detective)
; Compile on Windows with Inno Setup 6+: iscc installer.iss
; Expects PyInstaller output at ..\dist\GooseDetective\ (from goose_detective.spec)

#define MyAppName "鹅探长"
#define MyAppNameEn "GooseDetective"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Goose Detective"
#define MyAppExeName "GooseDetective.exe"

[Setup]
AppId={{B7E3A1C4-9F2D-4E8A-9C1B-6D5F0A2E7B3C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppNameEn}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Install per-user by default so no admin rights needed
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist\installer
OutputBaseFilename=鹅探长-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; Chinese UI
; (Default English used if Chinese isl unavailable on the build machine)

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Bundle the entire PyInstaller one-folder output
Source: "..\dist\GooseDetective\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
