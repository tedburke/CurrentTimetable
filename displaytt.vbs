' This is a Windows Scripting Host script to launch
' the Windows image viewer and display all of the
' images in a predefined directory in a repeating
' sequence. The images are displayed in full screen
' mode. The script launches the image viewer, then
' sends an F11 keystroke to it to enter full screen
' mode, then sends a right arrow keystroke once
' every second to move on to the next image, for as
' long as the image viewer remains open.
'
' Version 0.01 - written by Ted Burke, 16/9/2009

Set objshell = WScript.CreateObject("WScript.Shell")
Set ImageViewer = objshell.Exec("rundll32.exe C:\WINDOWS\system32\shimgvw.dll,ImageView_Fullscreen C:\Documents and Settings\Administrator\Desktop\wtt")

' Wait until image viewer is open and ready to receive keystrokes
Do Until objShell.AppActivate(ImageViewer.processID)
    Wscript.Sleep 100
Loop

' Set image viewer to full screen
objshell.SendKeys "{F11}"
Wscript.Sleep 1000

' Keep "pressing" right arrow key as long as the image viewer is open
do while objShell.AppActivate(ImageViewer.processID)
	objshell.SendKeys "{RIGHT}"
    Wscript.Sleep 1000
Loop

Wscript.Echo "Image display script exiting because image viewer has closed."
