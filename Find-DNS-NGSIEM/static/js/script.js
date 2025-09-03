document.addEventListener('DOMContentLoaded', function() {
    const refreshButton = document.getElementById('refresh-button');
    const alertButton = document.getElementById('alert-button'); // Novo botão
    const statusContainer = document.getElementById('status-container');
    const statusBar = document.getElementById('progress-bar');
    const statusMessage = document.getElementById('status-message');

    if (!refreshButton) return;

    // Função para enviar alertas de vencimento
    function sendAlerts() {
        if (alertButton) {
            alertButton.disabled = true;
            alertButton.textContent = 'Enviando Alertas...';
        }
        statusContainer.style.display = 'block';
        statusMessage.textContent = 'Verificando certificados a vencer e enviando e-mails...';
        statusBar.style.width = '0%';
        statusBar.style.backgroundColor = '#388bfd';
        statusMessage.style.color = '#8b949e';

        fetch('/alertar-vencimentos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            statusMessage.textContent = data.message;
            statusBar.style.width = '100%';
            statusBar.style.backgroundColor = '#28a745'; // Green for success
            if (alertButton) {
                alertButton.disabled = false;
                alertButton.textContent = 'Alertar Vencimentos';
            }
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        })
        .catch(error => {
            console.error('Erro ao enviar alertas:', error);
            statusMessage.textContent = 'Erro ao enviar alertas de vencimento.';
            statusBar.style.width = '100%';
            statusBar.style.backgroundColor = '#F87171'; // Red for error
            if (alertButton) {
                alertButton.disabled = false;
                alertButton.textContent = 'Alertar Vencimentos';
            }
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        });
    }

    refreshButton.addEventListener('click', function() {
        this.disabled = true;
        this.textContent = 'Atualizando...';
        if (alertButton) {
            alertButton.disabled = true; // Desabilita o botão de alerta durante a atualização
        }
        statusContainer.style.display = 'block';
        statusMessage.textContent = 'Iniciando conexão com o servidor...';
        statusBar.style.width = '0%';
        statusBar.style.backgroundColor = '#388bfd'; // Reset color on new run
        statusMessage.style.color = '#8b949e'; // Reset color

        const eventSource = new EventSource('/stream-refresh');

        eventSource.addEventListener('message', function(event) {
            statusMessage.textContent = event.data;
        });

        eventSource.addEventListener('progress', function(event) {
            const data = JSON.parse(event.data);
            const progress = data.progress;
            const domain = data.domain;
            const domainData = data.data; // Dados completos do domínio
            
            statusBar.style.width = progress + '%';
            statusMessage.textContent = `Escaneando: ${domain} (${progress.toFixed(1)}%)`;

            if (domainData) {
                const tableBody = document.querySelector('#logs-table tbody');
                let row = tableBody.querySelector(`tr[data-domain="${domainData.dominio}"]`);
                if (!row) {
                    row = tableBody.insertRow(0); // Adiciona no início para ver os novos
                    row.setAttribute('data-domain', domainData.dominio);
                    row.innerHTML = "\
                        <td>${domainData.dominio}</td>\
                        <td>${domainData.emitido_em}</td>\
                        <td style=\"color: ${domainData.status_color};\">${domainData.vence_em}</td>\
                        <td>${domainData.email}</td>\
                        <td>${domainData.porta}</td>\
                        <td>${domainData.autoridade_certificadora}</td>\
                    ";
                } else {
                    // Atualiza a linha existente se o domínio já estiver na tabela
                    row.cells[1].textContent = domainData.emitido_em;
                    row.cells[2].textContent = domainData.vence_em;
                    row.cells[2].style.color = domainData.status_color;
                    row.cells[3].textContent = domainData.email;
                    row.cells[4].textContent = domainData.porta;
                    row.cells[5].textContent = domainData.autoridade_certificadora;
                }
            } else if (data.discarded) {
                // Se o domínio foi descartado, ainda atualiza o progresso, mas sem dados
                progress = (i + 1) / len(domains) * 100;
                yield `event: progress\ndata: ${json.dumps({'progress': progress, 'domain': domain, 'discarded': True})}\n\n`;
            }
        });

        eventSource.addEventListener('email_update', function(event) {
            const data = JSON.parse(event.data);
            const domain = data.domain;
            const email = data.email;
            const tableBody = document.querySelector('#logs-table tbody');
            const row = tableBody.querySelector(`tr[data-domain="${domain}"]`);
            if (row) {
                // A coluna de e-mail é a 4ª (índice 3) após a remoção do Owner
                row.cells[3].textContent = email;
            }
        });

        eventSource.addEventListener('finished', function(event) {
            statusMessage.textContent = event.data;
            statusBar.style.width = '100%';
            eventSource.close();

            // Após a atualização dos dados, envia os alertas de vencimento
            sendAlerts();

            refreshButton.disabled = false;
            refreshButton.textContent = 'Atualizar Dados (Últimos 7 Dias)';
            if (alertButton) {
                alertButton.disabled = false;
            }
        });

        eventSource.addEventListener('error', function(event) {
            const errorMessage = event.data ? event.data : 'Ocorreu um erro ao atualizar os dados.';
            statusMessage.textContent = `Erro: ${errorMessage}`;
            statusMessage.style.color = '#F87171';
            statusBar.style.backgroundColor = '#F87171';
            statusBar.style.width = '100%';
            
            eventSource.close();

            refreshButton.disabled = false;
            refreshButton.textContent = 'Tentar Novamente';
            if (alertButton) {
                alertButton.disabled = false;
            }
        });
    });

    // Event listener para o novo botão "Alertar Vencimentos"
    if (alertButton) {
        alertButton.addEventListener('click', sendAlerts);
    }
});
