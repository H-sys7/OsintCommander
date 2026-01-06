[Setup]
AppName=OsintCommander
AppVersion=1.0
DefaultDirName={pf}\OsintCommander
DefaultGroupName=OsintCommander
OutputDir=installer
OutputBaseFilename=OsintCommander_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=icon.ico

[Files]
Source: "dist\OsintCommander.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\OsintCommander"; Filename: "{app}\OsintCommander.exe"
Name: "{commondesktop}\OsintCommander"; Filename: "{app}\OsintCommander.exe"

[Run]
Filename: "{app}\OsintCommander.exe"; Description: "Lancer OsintCommander"; Flags: nowait postinstall skipifsilent
