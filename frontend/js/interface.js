/* =====================================================================
   interface.js — a camada de acabamento.

   Carrega DEPOIS do base.js e acrescenta três coisas ao HubUI:

     HubUI.esqueleto(forma, quantas)   → o DESENHO do que está chegando
     HubUI.esperando(id, forma, ...)   → põe esse desenho no lugar exato

   E uma que não tem nome: a **barra de progresso do topo**, que acende
   sozinha em toda chamada à API. Ela envolve o HubUI.api — por isso
   este arquivo vem depois do base.js e antes do script da página.

   Duas regras herdadas do base.js, e que aqui apertam:
   - NENHUM estilo escrito por JavaScript. Largura de esqueleto é
     classe; estado da barra é `data-estado`. A CSP bloqueia
     element.style, e falha calada.
   - NENHUMA cor literal.
   ===================================================================== */
(function (janela, documento) {
  'use strict';

  var HubUI = janela.HubUI;
  if (!HubUI) return;

  /* ===================================================================
     1. O esqueleto — o desenho do que está chegando

     A tela nunca fica em branco esperando o servidor, e nada pula
     quando o dado chega: o esqueleto tem a MESMA estrutura da coisa
     real (mesma tabela, mesmas colunas, mesma altura de linha).
     =================================================================== */

  /* As larguras são classes, não style: variedade suficiente para o
     esqueleto não parecer um código de barras. */
  var LARGURAS = ['g', 'm', 'p', 'm', 'g', 'p'];

  function linhas(quantas, colunas) {
    var saida = '';
    for (var i = 0; i < quantas; i++) {
      var celulas = '';
      for (var c = 0; c < colunas; c++) {
        celulas += '<span class="esq-barra ' + LARGURAS[(i + c) % LARGURAS.length] + '"></span>';
      }
      saida += '<div class="esq-linha">' + celulas + '</div>';
    }
    return saida;
  }

  function esqueleto(forma, quantas) {
    quantas = quantas || 3;
    if (forma === 'cartoes') {
      var cartoes = '';
      for (var i = 0; i < quantas; i++) {
        cartoes += '<div class="esq-cartao">' +
                     '<span class="esq-barra p"></span>' +
                     '<span class="esq-barra numero"></span>' +
                     '<span class="esq-barra m"></span>' +
                   '</div>';
      }
      return '<div class="esqueleto cartoes" aria-hidden="true">' + cartoes + '</div>';
    }
    if (forma === 'lista') {
      return '<div class="esqueleto lista" aria-hidden="true">' + linhas(quantas, 2) + '</div>';
    }
    if (forma === 'texto') {
      return '<div class="esqueleto texto" aria-hidden="true">' + linhas(quantas, 1) + '</div>';
    }
    // 'tabela' é o padrão: cabeçalho + linhas, como a tabela real
    return '<div class="esqueleto tabela" aria-hidden="true">' +
             '<div class="esq-linha cabecalho">' +
               '<span class="esq-barra p"></span><span class="esq-barra m"></span>' +
               '<span class="esq-barra m"></span><span class="esq-barra p"></span>' +
             '</div>' +
             linhas(quantas, 4) +
           '</div>';
  }

  function esperando(id, forma, quantas) {
    var alvo = typeof id === 'string' ? documento.getElementById(id) : id;
    if (!alvo) return null;
    alvo.setAttribute('aria-busy', 'true');
    alvo.innerHTML = esqueleto(forma, quantas);

    /* O aria-busy se desliga sozinho quando o conteúdo real entra.
       Deixar isso a cargo de quem chama seria esquecer: quem escreve
       `lista.innerHTML = tabela` não lembra de desmarcar, e o leitor de
       tela segue anunciando a região como ocupada para sempre. */
    if (janela.MutationObserver) {
      var observador = new janela.MutationObserver(function () {
        if (alvo.querySelector('.esqueleto')) return;
        alvo.removeAttribute('aria-busy');
        observador.disconnect();
      });
      observador.observe(alvo, { childList: true, subtree: true });
    }
    return alvo;
  }

  /* ===================================================================
     2. A barra de progresso do topo

     Acende em toda chamada à API, com 120ms de atraso: resposta rápida
     não vira lampejo. Conta as chamadas em voo, porque a página faz
     várias em paralelo e a barra tem que esperar a última.
     =================================================================== */

  var barra = null;
  var emVoo = 0;
  var timerAcender = null;
  var timerApagar = null;

  function garantirBarra() {
    if (barra) return barra;
    barra = documento.createElement('div');
    barra.className = 'barra-progresso';
    barra.setAttribute('role', 'progressbar');
    barra.setAttribute('aria-label', 'Carregando');
    barra.dataset.estado = 'parada';
    documento.body.appendChild(barra);
    return barra;
  }

  function acender() {
    var b = garantirBarra();
    janela.clearTimeout(timerApagar);
    b.dataset.estado = 'iniciando';
    // o próximo quadro: sem isto o navegador junta os dois estados e
    // a barra salta direto para o fim, sem transição nenhuma
    janela.requestAnimationFrame(function () {
      janela.requestAnimationFrame(function () {
        if (emVoo > 0) b.dataset.estado = 'andando';
      });
    });
  }

  function apagar() {
    var b = garantirBarra();
    b.dataset.estado = 'fim';
    timerApagar = janela.setTimeout(function () {
      if (emVoo === 0) b.dataset.estado = 'parada';
    }, 400);
  }

  var apiOriginal = HubUI.api;

  HubUI.api = function (url, opcoes) {
    emVoo++;
    if (emVoo === 1) {
      timerAcender = janela.setTimeout(function () {
        if (emVoo > 0) acender();
      }, 120);
    }
    return apiOriginal(url, opcoes).finally(function () {
      emVoo--;
      if (emVoo === 0) {
        janela.clearTimeout(timerAcender);
        if (barra && barra.dataset.estado !== 'parada') apagar();
      }
    });
  };

  HubUI.esqueleto = esqueleto;
  HubUI.esperando = esperando;
})(window, document);
