# Network_Containment — README

This folder contains an example CrowdStrike Falcon Workflow and supporting files to automatically contain a Windows host when a Critical detection fires, run a short pre-containment cleanup, and notify the end user on screen.

## How the workflow operates

At a high level:

- **Trigger:** An `Investigatable/EPP` signal with Critical severity (5) starts the workflow.  
- **Platform check:** The workflow proceeds only for Windows sensors.  
- **Pre-containment cleanup:** The workflow puts and runs `CS_pre-containment_cleanup.exe` on the device.  
- **Stage notification assets:** It uploads three files to `C:\Windows\TEMP\`:
    - `CS_company_logo.png`
    - `CS_notify_network_containment.html`
    - `CS_notify_network_containment.cmd`  
    Once staged, it puts and runs `CS_notify_network_containment.exe`.  
- **Containment:** After a short delay, the device is network-contained.

Key timings & actions used by the workflow:

- `PutAndRunFile2` → runs the cleanup EXE, then waits 10 s before staging notification files and running the notification EXE.  
- `PutFile4/5/6` → place the HTML, CMD, and PNG into `C:\Windows\TEMP\`.  
- `PutAndRunFile3` → runs the notification EXE, then Sleep (5 s) → `ContainDevice`.

The workflow file is `Network_Containment.yaml` (an exported Falcon Workflow). The header warns that editing the YAML directly is not recommended — import it into Falcon and edit there if needed.

## Files explained

- `Network_Containment.yaml`  
    Falcon Workflow that wires everything together: it triggers on Critical EPP events, gates on Windows, run the cleanup EXE, stage the notification assets (`.html`, `.cmd`, `.png`), run the notification EXE, and finally contain the device. It also sets sleep intervals to ensure ordering.

- `CS_notify_network_containment.html`  
    Full-screen, dark-themed page shown to the user indicating the device was contained for security reasons, instructing them not to power off or disconnect, and asking them to contact IT. It displays a company logo and includes a placeholder contact phone, `(00) 1234-5678`, and the placeholder name “Empresa” in the footer.

- `CS_notify_network_containment.cmd`  
    Helper script placed in `C:\Windows\TEMP\` whose purpose is to launch the HTML notification (e.g., via the default browser) using local paths. It’s staged alongside the HTML and logo and can be invoked if desired.

- `CS_pre-containment_cleanup.ps1` → compiled to `CS_pre-containment_cleanup.exe`  
    PowerShell script intended to run before containment. Typical uses include stopping services/processes, removing transient network sessions, notifying EDR, or logging a breadcrumb. The workflow puts and runs the compiled EXE as the first action on the endpoint.

- `CS_notify_network_containment.ps1` → compiled to `CS_notify_network_containment.exe`  
    PowerShell script that likely opens the notification (HTML) and/or ensures it’s prominent to the end user after cleanup completes. The workflow runs this EXE after staging the HTML/CMD/PNG.

- `CS_company_logo.png`  
    Logo displayed at the top of the HTML notification. The file is uploaded to `C:\Windows\TEMP\` and referenced by the HTML.

- `CS_icon.ico`  
    Icon used when compiling the `.ps1` scripts into `.exe` files.

## Building the .exe files (using ps2exe)

Use `ps2exe` (PowerShell) to compile the two scripts into 64-bit executables with custom icon/metadata. Example commands:

```
ps2exe -inputFile .\CS_pre-containment_cleanup.ps1 `
             -outputFile .\CS_pre-containment_cleanup.exe `
             -x64 `
             -iconFile .\CS_icon.ico `
             -title "Falcon pre-containment Cleanup" `
             -company "SuaEmpresa" `
             -description "Falcon - limpeza antes network containment" `
             -Verbose

ps2exe -inputFile .\CS_notify_network_containment.ps1 `
             -outputFile .\CS_notify_network_containment.exe `
             -x64 `
             -iconFile .\CS_icon.ico `
             -title "Falcon Notification" `
             -company "SuaEmpresa" `
             -description "Notificação Falcon - network containment" `
             -Verbose
```

Place the resulting EXEs (and the `.html`, `.cmd` and `.png` files) where your Falcon workflow can `PutFile` / `PutAndRunFile` them, using the same filenames referenced in `Network_Containment.yaml`.

## Customization required (important)

- Replace all “Empresa” placeholders with your actual company name (it appears in the HTML footer and in the logo alt text).  
- Update the phone number in the HTML (`(00) 1234-5678`) to your IT Service Desk contact.  
- When compiling with `ps2exe`, set `-company` to your company (e.g., `"SuaEmpresa"` → `"AcmeCorp"`).

## Deployment tips

- Logo path: The HTML expects `CS_company_logo.png` in the same folder as the HTML; the workflow places both into `C:\Windows\TEMP\`.
- Order of operations: The sleeps (10 s before notification; 5 s before containment) are part of the workflow — adjust them in Falcon if your environment needs more or less time for the EXEs to complete.

## Testing

- Import `Network_Containment.yaml` into a test Falcon environment and trigger with a synthetic Critical event.
- Confirm the HTML renders and shows your updated company name and phone number.  
- Verify the host becomes contained at the end.

## AI Disclaimer

- This document was generated with the assistance of AI and may contain errors or omissions.
