# Network_Containment — README

Esta pasta contém um exemplo de workflow do Fusion SOAR da CrowdStrike e os arquivos de suporte para conter automaticamente um host Windows quando uma detecção crítica for acionada, executar uma limpeza rápida antes da contenção e notificar o usuário final na tela.

## Como o fluxo de trabalho opera

Em alto nível:

- **Gatilho:** um sinal `Investigatable/EPP` com severidade crítica (5) inicia o fluxo de trabalho.  
- **Verificação de plataforma:** o fluxo de trabalho só prossegue para sensores Windows.  
- **Limpeza pré-contenção:** o fluxo de trabalho envia e executa `CS_pre-containment_cleanup.exe` no dispositivo.  
- **Preparação dos arquivos de notificação:** o fluxo envia três arquivos para `C:\Windows\TEMP\`:
    - `CS_company_logo.png`
    - `CS_notify_network_containment.html`
    - `CS_notify_network_containment.cmd`  
    Com os arquivos no lugar, ele envia e executa `CS_notify_network_containment.exe`.  
- **Contenção:** após um curto intervalo, o dispositivo é colocado em contenção de rede.

Tempos e ações principais usados pelo fluxo de trabalho:

- `PutAndRunFile2` → executa o EXE de limpeza e depois espera 10 s antes de enviar os arquivos de notificação e executar o EXE de notificação.  
- `PutFile4/5/6` → coloca o HTML, CMD e PNG em `C:\Windows\TEMP\`.  
- `PutAndRunFile3` → executa o EXE de notificação e depois Sleep (5 s) → `ContainDevice`.

O arquivo do fluxo é `Network_Containment.yaml` (um Falcon Workflow exportado). O cabeçalho avisa que não é recomendado editar o YAML diretamente: importe-o no Falcon e edite lá, se necessário.

## Arquivos explicados

- `Network_Containment.yaml`  
    Falcon Workflow que conecta tudo: é acionado por eventos EPP críticos, restringe a execução a Windows, executa o EXE de limpeza, envia os arquivos de notificação (`.html`, `.cmd`, `.png`), executa o EXE de notificação e, finalmente, contém o dispositivo. Também configura intervalos de espera para garantir a ordem das etapas.

- `CS_notify_network_containment.html`  
    Página em tela cheia, com tema escuro, exibida ao usuário para informar que o dispositivo foi contido por motivos de segurança, orientar que ele não desligue nem desconecte o equipamento e pedir que entre em contato com a TI. Exibe o logo da empresa e inclui um telefone de contato fictício, `(00) 1234-5678`, e o nome fictício “Empresa” no rodapé.

- `CS_notify_network_containment.cmd`  
    Script auxiliar copiado para `C:\Windows\TEMP\` cuja finalidade é abrir a notificação HTML (por exemplo, no navegador padrão) usando caminhos locais. É enviado junto com o HTML e o logo e pode ser chamado conforme necessário.

- `CS_pre-containment_cleanup.ps1` → compilado para `CS_pre-containment_cleanup.exe`  
    Script PowerShell destinado a ser executado antes da contenção. Usos típicos incluem parar serviços/processos, remover sessões de rede transitórias, notificar o EDR ou deixar um registro (breadcrumb). O fluxo de trabalho envia e executa o EXE compilado como a primeira ação no endpoint.

- `CS_notify_network_containment.ps1` → compilado para `CS_notify_network_containment.exe`  
    Script PowerShell que provavelmente abre a notificação (HTML) e/ou garante que ela fique em destaque para o usuário final após a conclusão da limpeza. O fluxo de trabalho executa esse EXE depois de enviar o HTML/CMD/PNG.

- `CS_company_logo.png`  
    Logo exibido no topo da notificação HTML. O arquivo é enviado para `C:\Windows\TEMP\` e referenciado pelo HTML.

- `CS_icon.ico`  
    Ícone usado ao compilar os scripts `.ps1` em arquivos `.exe`.

## Construindo os arquivos .exe (usando ps2exe)

Use o `ps2exe` (PowerShell) para compilar os dois scripts em executáveis de 64 bits com ícone e metadados personalizados. Exemplos de comandos:

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

Disponibilize os EXEs gerados (e os arquivos `.html`, `.cmd` e `.png`) onde o seu workflow do Falcon consiga usá-los com `PutFile` / `PutAndRunFile`, com os mesmos nomes de arquivo referenciados em `Network_Containment.yaml`.

## Personalização necessária (importante)

- Substitua todas as ocorrências do nome fictício “Empresa” pelo nome real da sua empresa (ele aparece no rodapé do HTML e no texto alternativo do logo).  
- Atualize o número de telefone no HTML (`(00) 1234-5678`) para o contato do seu Service Desk de TI.  
- Ao compilar com `ps2exe`, defina `-company` para sua empresa (por exemplo, `"SuaEmpresa"` → `"AcmeCorp"`).

## Dicas de implantação

- Caminho do logo: o HTML espera `CS_company_logo.png` na mesma pasta do HTML; o fluxo de trabalho coloca ambos em `C:\Windows\TEMP\`.  
- Ordem das operações: as pausas (10 s antes da notificação; 5 s antes da contenção) fazem parte do fluxo de trabalho. Ajuste-as no Falcon se o seu ambiente precisar de mais ou menos tempo para os EXEs terminarem.

## Testes

- Importe `Network_Containment.yaml` em um ambiente Falcon de teste e acione-o com um evento crítico sintético.  
- Confirme que o HTML é renderizado e mostra o nome da empresa e o telefone atualizados.  
- Verifique se o host fica contido ao final.

## Aviso sobre o uso de IA

- Este documento foi gerado com o auxílio de IA e pode conter erros ou omissões.
