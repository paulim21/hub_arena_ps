/* =====================================================================
   interface.js — a camada de acabamento.

   Carrega DEPOIS do base.js e acrescenta três coisas ao HubUI:

     HubUI.esqueleto(forma, quantas)   → o DESENHO do que está chegando
     HubUI.esperando(id, forma, ...)   → põe esse desenho no lugar exato
     HubUI.abrirBusca()                → a paleta do Ctrl+K

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

  /* ===================================================================
     3. A paleta do Ctrl+K

     Montada A CADA ABERTURA a partir do próprio menu da página: ela
     nunca oferece um lugar que a página não oferece. Leva também o que
     a página FAZ (tema, densidade), e toda ação dali aciona um botão
     que já existe no cabeçalho — a paleta é caminho de teclado, nunca
     uma porta que só ela abre.

     NÃO existe grupo "Recentes", e é decisão, não esquecimento. Com 6
     destinos e 2 ações, a lista inteira cabe na tela: um grupo de
     recentes repetia no topo itens visíveis dois centímetros abaixo —
     "Reservas" duas vezes, "Usar tema claro" duas vezes — e ainda
     empurrava o resto para fora, obrigando a rolar. Recência só se paga
     quando a lista não cabe; aqui ela só confundia. A ordem é a do
     cabeçalho, que é previsível e não muda debaixo do dedo.
     =================================================================== */

  var paleta = null;
  var itens = [];
  var focado = -1;

  /* Lê o cabeçalho da página. Nada é inventado aqui. */
  function recolher() {
    var lista = [];

    documento.querySelectorAll('header nav a').forEach(function (a) {
      lista.push({
        grupo: 'Ir para',
        nome: a.textContent.trim(),
        ico: a.dataset.ico || 'i-seta',
        atual: a.classList.contains('ativo'),
        acionar: function () { a.click(); }
      });
    });

    documento.querySelectorAll('header .sessao-nav button').forEach(function (b) {
      if (b.classList.contains('botao-busca')) return;  // seria uma porta para si mesma
      var nome = b.getAttribute('aria-label');
      if (!nome) return;
      var usa = b.querySelector('use');
      lista.push({
        grupo: 'Fazer',
        nome: nome,
        ico: usa ? usa.getAttribute('href').slice(1) : 'i-faisca',
        acionar: function () { b.click(); }
      });
    });

    return lista;
  }

  function normalizar(t) {
    return String(t || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  }

  /* Realça o trecho casado — sem innerHTML cru vindo do texto da página */
  function comRealce(nome, termo) {
    if (!termo) return HubUI.esc(nome);
    var i = normalizar(nome).indexOf(normalizar(termo));
    if (i < 0) return HubUI.esc(nome);
    return HubUI.esc(nome.slice(0, i)) +
           '<mark>' + HubUI.esc(nome.slice(i, i + termo.length)) + '</mark>' +
           HubUI.esc(nome.slice(i + termo.length));
  }

  function montarPaleta() {
    if (paleta) return paleta;
    paleta = documento.createElement('dialog');
    paleta.className = 'modal paleta';
    paleta.innerHTML =
      '<div class="paleta-campo">' +
        HubUI.ico('i-busca') +
        '<input type="search" class="paleta-entrada" autocomplete="off" ' +
          'placeholder="Buscar uma tela ou uma ação…" aria-label="Buscar">' +
        '<kbd>Esc</kbd>' +
      '</div>' +
      '<div class="paleta-lista" role="listbox"></div>';
    documento.body.appendChild(paleta);

    var entrada = paleta.querySelector('.paleta-entrada');
    entrada.addEventListener('input', function () { pintar(entrada.value.trim()); });
    entrada.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        mover(e.key === 'ArrowDown' ? 1 : -1);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        escolher(focado);
      }
    });
    paleta.addEventListener('close', function () { itens = []; focado = -1; });
    paleta.addEventListener('click', function (e) {
      if (e.target === paleta) paleta.close();  // clique no véu
    });
    return paleta;
  }

  function pintar(termo) {
    var lista = paleta.querySelector('.paleta-lista');
    var todos = recolher();
    var casados = termo
      ? todos.filter(function (i) { return normalizar(i.nome).indexOf(normalizar(termo)) >= 0; })
      : todos;

    var grupos = [];
    ['Ir para', 'Fazer'].forEach(function (g) {
      var doGrupo = casados.filter(function (i) { return i.grupo === g; });
      if (doGrupo.length) grupos.push({ nome: g, itens: doGrupo });
    });

    itens = [];
    if (!grupos.length) {
      lista.innerHTML = '<p class="vazio">' + HubUI.ico('i-busca-vazia', 'ico-grande') +
                        'Nada com esse nome.</p>';
      return;
    }

    lista.innerHTML = grupos.map(function (g) {
      return '<div class="paleta-grupo"><span class="rotulo">' + HubUI.esc(g.nome) + '</span>' +
        g.itens.map(function (item) {
          var i = itens.push(item) - 1;
          return '<button type="button" class="paleta-item" role="option" data-i="' + i + '">' +
                   HubUI.ico(item.ico) +
                   '<span>' + comRealce(item.nome, termo) + '</span>' +
                   (item.atual ? '<span class="paleta-aqui">aqui</span>' : '') +
                 '</button>';
        }).join('') +
      '</div>';
    }).join('');

    lista.querySelectorAll('.paleta-item').forEach(function (btn) {
      btn.addEventListener('click', function () { escolher(parseInt(btn.dataset.i, 10)); });
      btn.addEventListener('mousemove', function () { focar(parseInt(btn.dataset.i, 10)); });
    });
    focar(0);
  }

  function focar(i) {
    focado = i;
    paleta.querySelectorAll('.paleta-item').forEach(function (btn) {
      var ativo = parseInt(btn.dataset.i, 10) === i;
      btn.classList.toggle('focado', ativo);
      btn.setAttribute('aria-selected', ativo ? 'true' : 'false');
      if (ativo) btn.scrollIntoView({ block: 'nearest' });
    });
  }

  function mover(passo) {
    if (!itens.length) return;
    focar((focado + passo + itens.length) % itens.length);
  }

  function escolher(i) {
    var item = itens[i];
    if (!item) return;
    var ehAcao = item.grupo === 'Fazer';
    if (!ehAcao) paleta.close();
    item.acionar();
    if (ehAcao) pintar(paleta.querySelector('.paleta-entrada').value.trim());
  }

  function abrirBusca() {
    var p = montarPaleta();
    if (p.open) { p.close(); return; }
    var entrada = p.querySelector('.paleta-entrada');
    entrada.value = '';
    pintar('');
    p.showModal();
    entrada.focus();
  }

  documento.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      abrirBusca();
    }
  });

  function ligarBotaoBusca() {
    var btn = documento.querySelector('.botao-busca');
    if (!btn) return;
    btn.innerHTML = HubUI.ico('i-busca');
    btn.setAttribute('aria-label', 'Buscar (Ctrl+K)');
    btn.setAttribute('title', 'Buscar (Ctrl+K)');
    btn.addEventListener('click', abrirBusca);
  }

  if (documento.readyState === 'loading') {
    documento.addEventListener('DOMContentLoaded', ligarBotaoBusca);
  } else {
    ligarBotaoBusca();
  }

  HubUI.esqueleto = esqueleto;
  HubUI.esperando = esperando;
  HubUI.abrirBusca = abrirBusca;
})(window, document);
