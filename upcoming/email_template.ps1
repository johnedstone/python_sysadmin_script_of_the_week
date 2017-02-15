<#  .Description
    Template script for sending mail
    Converted from code stolen shamelessly from https://docs.python.org/2/library/email-examples.html
    .Example
    email_template.ps1 -Message 'boo hoo'
    .Example
    email_template.ps1 -Recipient someone@somewhere.com -Sender me@mydomain.com -Message 'boo hoo' -Link 'test.com' -SmtpServer smtp-server.yourcompany.com -Verbose
#>
[CmdletBinding()]
param(
    ## Recipient(s) to whom to send message
    [string[]]$Recipient = 'yourname@yourcompany.com',
    ## Sender from whom the message should appear to come
    [string]$Sender = 'yourname@yourcompany.com',
    ## Sample message to include in the email
    [Alias("Msg")]$Message = 'hello world',
    ## Sample link to include in the email
    [string]$Link = 'www.google.com',
    ## SMTP server through which to send email (defaults to "localhost") -- added here in case machine running this code is not running an SMTP server
    [string]$SmtpServer = "localhost"
) ## end param

begin {
    ## PowerShell debugging is generally done in a bit different way, but, adding some verbose output here in case someone wants to check params in the same way the Python script does it
    Write-Verbose "args:`n$($PSBoundParameters | Format-Table -AutoSize | Out-String)"
} ## end begin

process {
    foreach ($oThisRecipient in $Recipient) {
        ## Create hastable with message params; this will be used for the Send-MailMessage call, using the parameter "splatting" technique (see 'Get-Help -Full about_Splatting')
        $hshMsgParams = @{
            From = $Sender
            SmtpServer = $SmtpServer
            Subject = 'sample email'
            To = $oThisRecipient
        } ## end hashtable

        # Create the body of the message (a plain-text and an HTML version).
        $text = @'
Hi!
How are you {0}?
Here is the link you wanted: https://{1}
'@ -f $oThisRecipient, $Link

        $html = @'
<html>
<head></head>
    <body>
    <div style="margin:0;padding:0;font-family:Calibri, Arial, sans-serif;font-color:#333399">
        <p style="margin:0;padding:0;">
           Hello {0}<br>
           This is a sample <a href="https://{1}">link</a>.<br>
           This is a sample message: {2}.<br>
           Spanish 'my goodness': ¡Dios mío!<br>
           <br>
           This message is an example of a python mail script.<br>
           <br>
           Get this script at <a href="file:///\\samba-server\data\python_sysadmin_script_of_the_week\upcoming">\\samba-server\data\python_sysadmin_script_of_the_week\upcoming</a><br>
           and run it in PowerShell (getting help via, 'Get-Help email_template.ps1')
        </p>
        <p style="color: #ccc;">
            Converted to PS from Py code stolen shamelessly from <a
            style="color: #ccc;"
            href="https://docs.python.org/2/library/email-examples.html">https://docs.python.org/2/library/email-examples.html</a>
        </p>
    </div>
    </body>
</html>
'@ -f $oThisRecipient, $Link, $Message

        ## could use IO.MemoryStream for adding strings from memory as attachments to email, as illustrated at https://social.technet.microsoft.com/Forums/windowsserver/en-US/3aae6d9a-adbb-4af3-a0fe-c83e6fdbc65a/creating-inmemory-mail-attachments?forum=winserverpowershell, but for this example, opted for the "use temporary files for the attachments" route
        ##  using a GUID as the folder name in the given temp dir, so as to avoid file naming collision
        $strSomeGuid = ([System.Guid]::NewGuid()).Guid
        $oNewTempDir = New-Item -ItemType Directory -Path "${env:\temp}\$strSomeGuid"
        $strTxtAttachmentFilespec = "${env:\temp}\$strSomeGuid\textVersion.txt"
        $strHtmlAttachmentFilespec = "${env:\temp}\$strSomeGuid\htmlVersion.html"
        $text | Out-File -Encoding utf8 -FilePath $strTxtAttachmentFilespec
        $html | Out-File -Encoding utf8 -FilePath $strHtmlAttachmentFilespec

        $hshMsgParams["Attachments"] = $strTxtAttachmentFilespec,$strHtmlAttachmentFilespec
        Write-Verbose "Sending to recipient '$oThisRecipient'"
        ## send the message to this recipient
        Send-MailMessage @hshMsgParams
        ## remove the temp dir and its contents
        Write-Verbose "Removing temp dir '$($oNewTempDir.FullName)'"
        $oNewTempDir | Remove-Item -Recurse
    } ## end foreach
} ## end process
