;ConsoleWrite($CmdLine[1])
;opt("SendKeyDelay",50)
Run("vpktool.exe")
if WinWaitActive("Quick and dirty Bloodlines Tools v3.9","",5) then
	Send("{LEFT}")
	Send("{LEFT}")
	Send("{LEFT}")
	Send("{LEFT}")
	Send("{ENTER}")
	Send("{TAB}")
	Send("{ENTER}")
	if WinWaitActive("Texture to convert","",5) then
		Send($CmdLine[1])
		Send("{ENTER}")
		if WinWaitActive("Quick and dirty Bloodlines Tools v3.9","",5) then
			Send("{TAB}")
			Send("{TAB}")
			Send("{ENTER}")
		EndIf
	EndIf
EndIf
sleep(2000)
ProcessClose("vpktool.exe")
