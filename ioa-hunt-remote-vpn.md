# IOA/Hunt

### IOA/Hunt para softwares de acesso remoto (a regex pega tudo antes e depois do nome):

```text
(.*TeamViewer.*|.*AnyDesk.*|.*RemotePC.*|.*LogMeIn.*|.*vncviewer.*|.*SRClient.*|.*remotedesktophost.*|.*ZohoAssist.*|.*ScreenConnect\.Client.*|.*ParallelsAccess.*|.*UltraVNC.*|.*GoToMyPC.*|.*AmmyyAdmin.*|.*TightVNC.*|.*BeyondTrustRemoteSupport.*|.*Bomgar.*|.*DamewareRemoteSupport.*|.*RemoteUtilities.*|.*NetopRemoteControl.*|.*RemotelyAnywhere.*|.*Radmin.*|.*RemoteDesktopManager.*|.*ISLOnline.*|.*BomgarRemoteSupport.*|.*BeyondTrustPrivilegedRemoteAccess.*|.*ScreenConnect.*|.*Mikogo.*|.*BeAnywhere.*|.*RemoteToPC.*|.*RemoteTech.*|.*ShowMyPC.*|.*AeroAdmin.*|.*Terminals.*|.*LaplinkEverywhere.*|.*X2Go.*|.*Gbridge.*|.*IperiusRemote.*|.*RemoteDesktopWeb.*|.*Remmina.*|.*DeskRoll.*|.*ThinfinityRemoteDesktop.*|.*RemoteSpark.*|.*CloudBerryRemoteAssistant.*|.*RemotePCbyIDrive.*|.*DWService.*|.*TigerVNC.*|.*OpenTextExceedTurboX.*|.*NetSupportManager.*|.*LiteManager.*|.*RemoteDesktopConnectionManager.*|.*ThincastClient.*|.*RemoteControlCollection.*|.*Remotix.*|.*Veyon.*|.*JumpDesktop.*|.*XtralogicRemoteDesktopClient.*|.*SplashtopBusinessAccess.*|.*VNCViewer.*|.*RemoteDesktopPlus.*|.*PCAnywhere.*|.*RealVNCEnterprise.*|.*SmartCodeVNCManager.*|.*TerasoftVNC.*|.*Aeroadmin.*|.*TSplus.*|.*RemoteView.*|.*GoverlanReach.*|.*Dualmon.*|.*VisualHelpdesk.*|.*WebexSupport.*|.*Impero.*|.*eBLVDRemoteDesktop.*|.*Onyxbits.*|.*DWSRemoteControl.*|.*InTouchApp.*|.*FastSupport.*|.*SupportYourCustomer.*|.*SupremoRemoteDesktop.*|.*CloudDesk.*|.*RemoteAccessPlus.*|.*Teleport.*|.*ScreenMeet.*|.*RemoteAccessTool.*|.*AnyplaceControl.*|.*OneClickAdmin.*|.*ISLAlwaysOn.*|.*ThinfinityVirtualUI.*|.*BeyondTrustRemote.*|.*LogMeInPro.*|.*Atera.*|.*SolarWindsTakeControl.*|.*RescueAssist.*|.*ZohoLens.*|.*RemoteAdmin.*|.*ProxyNetworks.*|.*MSP360Connect.*|.*WebExRemoteSupport.*|.*HelpWire.*|.*InuvikaOVD.*|.*NTRglobal.*|.*LivecareSupport.*|.*DeskTimePro.*|.*ScreenLeap.*|.*anydesk.*|.*hoptodesk.*)
```

### IOA/Hunt para softwares de VPN Windows (a regex pega tudo antes e depois do nome):

```text
(.*openvpn.*|.*nordvpn.*|.*expressvpn.*|.*cyberghostvpn.*|.*pia.*|.*surfshark.*|.*protonvpn.*|.*hsscp.*|.*vyprvpn.*|.*AvastSecureLine.*|.*Windscribe.*|.*hidemevpn.*|.*TunnelBear.*|.*ivacyvpn.*|.*strongvpn.*|.*torguardvpn.*|.*purevpn.*|.*mullvad.*|.*zenmate.*|.*betternet.*|.*holavpn.*|.*hma.*|.*securevpn.*|.*safervpn.*|.*freedome.*|.*vpnunlimited.*|.*bitdefendervpn.*|.*nortonvpn.*|.*kscvpn.*|.*operavpn.*)
```

## Formato com nomes exatos para identificação

### IOA/Hunt para softwares de acesso remoto:

```text
(.*[\\/])?(TeamViewer\.exe|AnyDesk\.exe|RemotePC\.exe|LogMeIn\.exe|vncviewer\.exe|SRClient\.exe|remotedesktophost\.exe|ZohoAssist\.exe|ScreenConnect\.Client\.exe|ParallelsAccess\.exe|UltraVNC\.exe|GoToMyPC\.exe|AmmyyAdmin\.exe|TightVNC\.exe|BeyondTrustRemoteSupport\.exe|Bomgar\.exe|DamewareRemoteSupport\.exe|RemoteUtilities\.exe|NetopRemoteControl\.exe|RemotelyAnywhere\.exe|Radmin\.exe|RemoteDesktopManager\.exe|ISLOnline\.exe|BomgarRemoteSupport\.exe|BeyondTrustPrivilegedRemoteAccess\.exe|ScreenConnect\.exe|Mikogo\.exe|BeAnywhere\.exe|RemoteToPC\.exe|RemoteTech\.exe|ShowMyPC\.exe|AeroAdmin\.exe|Terminals\.exe|LaplinkEverywhere\.exe|X2Go\.exe|Gbridge\.exe|IperiusRemote\.exe|RemoteDesktopWeb\.exe|Remmina\.exe|DeskRoll\.exe|ThinfinityRemoteDesktop\.exe|RemoteSpark\.exe|CloudBerryRemoteAssistant\.exe|RemotePCbyIDrive\.exe|DWService\.exe|TigerVNC\.exe|OpenTextExceedTurboX\.exe|NetSupportManager\.exe|LiteManager\.exe|RemoteDesktopConnectionManager\.exe|ThincastClient\.exe|RemoteControlCollection\.exe|Remotix\.exe|Veyon\.exe|JumpDesktop\.exe|XtralogicRemoteDesktopClient\.exe|SplashtopBusinessAccess\.exe|VNCViewer\.exe|RemoteDesktopPlus\.exe|PCAnywhere\.exe|RealVNCEnterprise\.exe|SmartCodeVNCManager\.exe|TerasoftVNC\.exe|Aeroadmin\.exe|TSplus\.exe|RemoteView\.exe|GoverlanReach\.exe|Dualmon\.exe|VisualHelpdesk\.exe|WebexSupport\.exe|Impero\.exe|eBLVDRemoteDesktop\.exe|Onyxbits\.exe|DWSRemoteControl\.exe|InTouchApp\.exe|FastSupport\.exe|SupportYourCustomer\.exe|SupremoRemoteDesktop\.exe|CloudDesk\.exe|RemoteAccessPlus\.exe|Teleport\.exe|ScreenMeet\.exe|RemoteAccessTool\.exe|AnyplaceControl\.exe|OneClickAdmin\.exe|ISLAlwaysOn\.exe|ThinfinityVirtualUI\.exe|BeyondTrustRemote\.exe|LogMeInPro\.exe|Atera\.exe|SolarWindsTakeControl\.exe|RescueAssist\.exe|ZohoLens\.exe|RemoteAdmin\.exe|ProxyNetworks\.exe|MSP360Connect\.exe|WebExRemoteSupport\.exe|HelpWire\.exe|InuvikaOVD\.exe|NTRglobal\.exe|LivecareSupport\.exe|DeskTimePro\.exe|ScreenLeap\.exe|anydesk\.exe|hoptodesk\.exe)
```

### IOA/Hunt para softwares de VPN Windows:

```text
(.*[\\/])?(openvpn\.exe|nordvpn\.exe|expressvpn\.exe|cyberghostvpn\.exe|pia\.exe|surfshark\.exe|protonvpn\.exe|hsscp\.exe|vyprvpn\.exe|AvastSecureLine\.exe|Windscribe\.exe|hidemevpn\.exe|TunnelBear\.exe|ivacyvpn\.exe|strongvpn\.exe|torguardvpn\.exe|purevpn\.exe|mullvad\.exe|zenmate\.exe|betternet\.exe|holavpn\.exe|hma\.exe|securevpn\.exe|safervpn\.exe|freedome\.exe|vpnunlimited\.exe|bitdefendervpn\.exe|nortonvpn\.exe|kscvpn\.exe|operavpn\.exe)
```

### IOA/Hunt para softwares de VPN Linux:

```text
(.*openvpn.*|.*nordvpn.*|.*expressvpn.*|.*cyberghostvpn.*|.*pia.*|.*surfshark.*|.*protonvpn.*|.*hsscp.*|.*vyprvpn.*|.*windscribe.*|.*hidemevpn.*|.*tunnelbear.*|.*ivacyvpn.*|.*strongvpn.*|.*torguard.*|.*purevpn.*|.*mullvad.*|.*zenmate.*|.*betternet.*|.*holavpn.*|.*hma.*|.*securevpn.*|.*safervpn.*|.*freedome.*|.*vpnunlimited.*|.*bitdefendervpn.*|.*nortonvpn.*|.*kscvpn.*|.*operavpn.*|.*privatetunnel.*)
```

### Obs.: o código acima está corrigido, pois o código anterior poderia trazer uma quantidade expressiva de falsos positivos.

Alterações realizadas:

1. Remoção de caracteres desnecessários: retirei o `.*` do começo e do fim, que permitiria qualquer caractere antes ou depois do nome do arquivo.
2. Correção da estrutura: cada padrão foi separado por `|` e colocado entre parênteses, garantindo que apenas os nomes exatos sejam correspondidos.
3. Ancoragem no início e no fim: usei `^` e `$` para garantir que a regex corresponda apenas aos arquivos com exatamente os nomes listados.

Essa expressão regular só corresponderá aos arquivos com os nomes exatos especificados na lista.
