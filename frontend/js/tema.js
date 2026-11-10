/* =====================================================================
   tema.js — vai no <head> SEM defer, de propósito.

   Ele escreve no <html> o tema ANTES da primeira pintura. Com defer, a
   tela piscaria clara antes de escurecer, na cara de quem já está lendo.
   Qualquer escolha nova que mude o layout entra aqui, não no base.js.

   O aparelho decide por padrão (prefers-color-scheme); o atributo só
   aparece quando a pessoa escolheu — e aí vence nos dois sentidos.
   ===================================================================== */
(function (janela, documento) {
  'use strict';

  var RAIZ = documento.documentElement;
  var CHAVE_TEMA = 'arenahub:tema';

  function lembrado(chave) {
    try {
      return janela.localStorage.getItem(chave);
    } catch (e) {
      return null;  // navegação privada: segue com o padrão do aparelho
    }
  }

  function guardar(chave, valor) {
    try {
      if (valor) janela.localStorage.setItem(chave, valor);
      else janela.localStorage.removeItem(chave);
    } catch (e) { /* sem onde guardar: a escolha vale só nesta página */ }
  }

  function aplicarTema(tema) {
    if (tema === 'claro' || tema === 'escuro') RAIZ.setAttribute('data-tema', tema);
    else RAIZ.removeAttribute('data-tema');
  }

  /* ---- antes da primeira pintura ---- */
  aplicarTema(lembrado(CHAVE_TEMA));

  function temaAtual() {
    var escolhido = RAIZ.getAttribute('data-tema');
    if (escolhido) return escolhido;
    return janela.matchMedia && janela.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'escuro' : 'claro';
  }

  janela.HubTema = {
    atual: temaAtual,
    alternar: function () {
      var novo = temaAtual() === 'escuro' ? 'claro' : 'escuro';
      aplicarTema(novo);
      guardar(CHAVE_TEMA, novo);
      return novo;
    }
  };
})(window, document);
