function Invoke-IcmpDownload
{
    [CmdletBinding()] Param(
        [Parameter(Position = 0, Mandatory = $true)]
        [String]
        $IPAddress,
        [Parameter(Position = 1, Mandatory = $true)]
        [String]
        $output
    )
    $ICMPClient = New-Object System.Net.NetworkInformation.Ping
    $PingOptions = New-Object System.Net.NetworkInformation.PingOptions
    $PingOptions.DontFragment = $True
    echo "Downloading file, please wait..."
    while ($true)
    {
        $sendbytes = ([text.encoding]::ASCII).GetBytes('')
        $reply = $ICMPClient.Send($IPAddress, 1000, $sendbytes, $PingOptions)
        
        if ($reply.Buffer)
        {
            $response = ([text.encoding]::ASCII).GetString($reply.Buffer)
            if ($response -eq "done")
            {
                echo "File transfer complete; EXITING."
                break;
            }
            else
            {
                $bytes = $reply.Buffer
                add-content -value $bytes -encoding byte -path $output
            }
        }
    }
}
