// Exemplo simples de renderização e captura do valor
function criarEstrelasAvaliacao() {
  const container = document.getElementById('container-estrelas');
  
  for (let i = 1; i <= 5; i++) {
    const estrela = document.createElement('span');
    estrela.className = 'estrela';
    estrela.innerHTML = '&#9733;'; // Caractere HTML da estrela cheia
    
    // Adiciona o evento de clique
    estrela.addEventListener('click', () => {
      // Valor capturado (1 a 5)
      const notaSelecionada = i;
      alert(`Você selecionou ${notaSelecionada} estrelas!`);
      
      // Chamar a função para enviar para o servidor
      enviarAvaliacao(notaSelecionada);
    });
    
    container.appendChild(estrela);
  }
}

// Função para enviar os dados para o seu banco de dados
function enviarAvaliacao(nota) {
  const idPontoTuristico = 123; // Exemplo de ID do Ponto Turístico
  const comentario = "Comentário de exemplo";

  // Usando Fetch API para enviar os dados para a sua API (POST)
  fetch('/api/avaliar', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      id_ponto_turistico: idPontoTuristico,
      nota: nota,
      comentario: comentario
    })
  })
  .then(response => response.json())
  .then(data => {
    // Tratar o sucesso (ex: atualizar a média na tela)
    console.log('Avaliação enviada com sucesso:', data);
  })
  .catch(error => {
    // Tratar o erro (ex: mostrar mensagem de erro)
    console.error('Erro ao enviar avaliação:', error);
  });
}

// Iniciar o processo
criarEstrelasAvaliacao();