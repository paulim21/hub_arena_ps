/* =====================================================================
   lgpd.js — o portão do consentimento (Lei 13.709/2018).

   Carrega DEPOIS do base.js e do interface.js, e por último de propósito:
   ele envolve o HubUI.api para SEGURAR toda chamada até o aceite existir.
   Envolvendo por fora da barra de progresso, a barra não acende enquanto
   o aviso está na tela — não há nada carregando, há alguém lendo.

   NADA passa pelo portão por causa da URL. As chamadas do próprio
   portão (política, verificação, aceite, revogação) usam a função
   interna, de dentro deste arquivo, e por isso não precisam de isenção.

   Isentar por prefixo era o caminho óbvio e estava errado: a regra
   `/api/consentimentos/*` também liberava `/api/consentimentos/relatorio`,
   que é dado do sistema como qualquer outro — o relatório carregava
   ANTES do aceite. Uma isenção por URL isenta o que ninguém lembrou de
   excluir.

   A única isenção é de PÁGINA: `/termos` não é bloqueada. Exigir aceite
   para LER a política seria pedir consentimento no escuro, e
   consentimento sem informação é nulo (Art. 8º, § 4º).

   O identificador é aleatório e não tem relação com nome ou e-mail: ele
   só liga ESTE navegador ao aceite registrado no banco.
   ===================================================================== */
(function (janela, documento) {
  'use strict';

  var HubUI = janela.HubUI;
  if (!HubUI) return;

  var CHAVE = 'arenahub:consentimento';
  var PAGINA_TERMOS = '/termos';

  var liberado = false;
  var abrirPortao;
  var portao = new janela.Promise(function (resolver) { abrirPortao = resolver; });

  /* ---------------- identificador do aparelho ---------------- */

  function sortearId() {
    if (janela.crypto && janela.crypto.randomUUID) return janela.crypto.randomUUID();
    var bytes = new Uint8Array(16);
    (janela.crypto || {}).getRandomValues
      ? janela.crypto.getRandomValues(bytes)
      : bytes.forEach(function (_, i) { bytes[i] = Math.floor(Math.random() * 256); });
    return Array.prototype.map.call(bytes, function (b) {
      return b.toString(16).padStart(2, '0');
    }).join('');
  }

  function identificador() {
    try {
      var guardado = janela.localStorage.getItem(CHAVE);
      if (guardado) return guardado;
      var novo = sortearId();
      janela.localStorage.setItem(CHAVE, novo);
      return novo;
    } catch (e) {
      /* Navegação privada: o aceite vale só enquanto esta aba viver. É
         menos cômodo e mais honesto do que fingir que foi guardado. */
      if (!janela.__idEfemero) janela.__idEfemero = sortearId();
      return janela.__idEfemero;
    }
  }

  /* ---------------- o portão ---------------- */

  var apiInterna = HubUI.api;

  HubUI.api = function (url, opcoes) {
    if (liberado) return apiInterna(url, opcoes);
    return portao.then(function () { return apiInterna(url, opcoes); });
  };

  function liberar() {
    liberado = true;
    abrirPortao();
  }

  /* ---------------- consultas ---------------- */

  function situacao() {
    return apiInterna('/api/consentimentos/vigente?identificador=' +
                      encodeURIComponent(identificador()));
  }

  function politica() {
    return apiInterna('/api/consentimentos/politica');
  }

  function aceitar(chaves) {
    return apiInterna('/api/consentimentos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        identificador: identificador(),
        versao_termos: chaves.versao,
        finalidades: chaves.finalidades
      })
    });
  }

  function revogar() {
    return apiInterna('/api/consentimentos/revogar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ identificador: identificador() })
    });
  }

  /* ---------------- o aviso de aceite ---------------- */

  function montarAviso(p) {
    var dlg = documento.createElement('dialog');
    dlg.className = 'modal modal-lgpd';
    dlg.setAttribute('aria-labelledby', 'lgpd-titulo');
    dlg.innerHTML =
      '<div class="modal-icone">' + HubUI.ico('i-escudo', 'ico-grande') + '</div>' +
      '<h3 id="lgpd-titulo">Antes de começar</h3>' +
      '<p>O ArenaHub trata dados pessoais para funcionar. Você precisa saber ' +
        'quais e para quê antes de aceitar — é isso que a LGPD chama de ' +
        'consentimento informado.</p>' +
      '<ul class="lgpd-finalidades">' +
        p.finalidades.map(function (f) {
          return '<li>' + HubUI.ico('i-ok') +
                   '<div><strong>' + HubUI.esc(f.nome) + '</strong>' +
                   '<span class="ajuda">' + HubUI.esc(f.detalhe) + '</span>' +
                   '<span class="selo">' + HubUI.esc(f.base_legal) + '</span></div>' +
                 '</li>';
        }).join('') +
      '</ul>' +
      '<label class="caixa-aceite">' +
        '<input type="checkbox" id="lgpd-li">' +
        '<span>Li e concordo com os <a href="' + PAGINA_TERMOS + '" target="_blank" ' +
          'rel="noopener">termos de uso e a política de privacidade</a> ' +
          '(versão ' + HubUI.esc(p.versao) + '). Tenho 18 anos ou mais.</span>' +
      '</label>' +
      '<div class="modal-acoes">' +
        '<button type="button" class="botao-texto" data-acao="recusar">Não aceito</button>' +
        '<button type="button" class="principal" data-acao="aceitar" disabled>' +
          'Aceitar e continuar</button>' +
      '</div>';
    documento.body.appendChild(dlg);

    /* O aviso não fecha no Esc nem no clique fora: fechar sem decidir
       deixaria a pessoa diante de uma tela que não responde, sem dizer
       por quê. A saída existe, e é o botão "Não aceito". */
    dlg.addEventListener('cancel', function (e) { e.preventDefault(); });

    var caixa = dlg.querySelector('#lgpd-li');
    var btnAceitar = dlg.querySelector('[data-acao="aceitar"]');
    caixa.addEventListener('change', function () {
      btnAceitar.disabled = !caixa.checked;
    });

    btnAceitar.addEventListener('click', async function () {
      HubUI.carregando(btnAceitar, true);
      try {
        await aceitar({ versao: p.versao, finalidades: p.chaves });
        dlg.close();
        dlg.remove();
        liberar();
        HubUI.toast('Consentimento registrado. Bom jogo.');
      } catch (e) {
        HubUI.carregando(btnAceitar, false);
        var erro = dlg.querySelector('.erro-form');
        if (!erro) {
          erro = documento.createElement('div');
          erro.className = 'erro-form';
          dlg.querySelector('.modal-acoes').before(erro);
        }
        erro.innerHTML = HubUI.ico('i-alerta') + '<span></span>';
        erro.querySelector('span').textContent = e.message;
      }
    });

    dlg.querySelector('[data-acao="recusar"]').addEventListener('click', function () {
      mostrarRecusa(dlg, p);
    });

    dlg.showModal();
    caixa.focus();
    return dlg;
  }

  /* Recusar é um direito, e a consequência tem que estar escrita
     (Art. 9º, I e § 3º): sem o aceite não há como operar o sistema. */
  function mostrarRecusa(dlg, p) {
    dlg.innerHTML =
      '<div class="modal-icone">' + HubUI.ico('i-barrado', 'ico-grande') + '</div>' +
      '<h3>Sem o aceite, o sistema não abre</h3>' +
      '<p>As duas finalidades são o que faz a plataforma funcionar: sem elas ' +
        'não há cadastro, não há reserva e não há como comprovar o que foi ' +
        'combinado. Você pode ler os termos inteiros e decidir com calma.</p>' +
      '<div class="modal-acoes">' +
        '<a class="botao-link" href="' + PAGINA_TERMOS + '" target="_blank" rel="noopener">' +
          'Ler os termos' + HubUI.ico('i-seta') + '</a>' +
        '<button type="button" class="principal" data-acao="voltar">Voltar</button>' +
      '</div>';
    dlg.querySelector('[data-acao="voltar"]').addEventListener('click', function () {
      dlg.close();
      dlg.remove();
      montarAviso(p);
    });
  }

  /* ---------------- partida ---------------- */

  async function iniciar() {
    // A página dos termos nunca é bloqueada: é onde a pessoa se informa.
    if (janela.location.pathname === PAGINA_TERMOS) { liberar(); return; }
    try {
      var atual = await situacao();
      if (atual && atual.vigente) { liberar(); return; }
      montarAviso(await politica());
    } catch (e) {
      /* Sem resposta do servidor não dá para saber se há consentimento.
         O portão fica fechado — e o erro aparece, para não virar uma tela
         parada sem explicação. */
      HubUI.erroTopo('Não foi possível verificar o consentimento: ' + e.message);
    }
  }

  if (documento.readyState === 'loading') {
    documento.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }

  janela.HubLGPD = {
    identificador: identificador,
    situacao: situacao,
    politica: politica,
    revogar: revogar
  };
})(window, document);
