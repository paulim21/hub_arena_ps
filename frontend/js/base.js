/* =====================================================================
   base.js — biblioteca compartilhada do front-end (HTML + JS puro)

   O painel não usa Jinja2: cada página chama as rotas /api/... via
   fetch e monta o HTML no navegador. Aqui ficam:
   - HubUI.api()           → wrapper do fetch (erros da API viram exceção)
   - HubUI.melhorar()      → dropdowns, data/hora e multi-select premium
   - HubUI.confirmar()     → modal de confirmação
   - HubUI.animarNumeros() → contagem animada do dashboard
   - HubUI.erroTopo(), esc(), moeda(), dataHora() → utilitários
   ===================================================================== */
window.HubUI = (function () {
  'use strict';

  /* ===== Utilitários ===== */

  async function api(url, opcoes) {
    var resposta = await fetch(url, opcoes);
    var dados = null;
    try { dados = await resposta.json(); } catch (e) { /* corpo vazio */ }
    if (!resposta.ok) throw new Error((dados && dados.erro) || 'Falha ao comunicar com a API.');
    return dados;
  }

  function esc(t) {
    var d = document.createElement('div');
    d.textContent = (t === null || t === undefined) ? '' : t;
    return d.innerHTML;
  }

  function moeda(v) {
    return 'R$ ' + Number(v || 0).toLocaleString('pt-BR', {
      minimumFractionDigits: 2, maximumFractionDigits: 2
    });
  }

  function dataHora(t) { return esc(String(t || '').replace('T', ' · ')); }

  function erroTopo(msg) {
    var antigo = document.querySelector('.erro-topo');
    if (antigo) antigo.remove();
    if (!msg) return;
    var div = document.createElement('div');
    div.className = 'erro-topo';
    div.textContent = '🚫 ' + msg;
    var main = document.querySelector('main');
    main.insertBefore(div, main.firstChild);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function animarNumeros() {
    document.querySelectorAll('.numero[data-valor]').forEach(function (el) {
      if (el.dataset.animado) return;
      el.dataset.animado = '1';
      var alvo = parseFloat(el.dataset.valor) || 0;
      var prefixo = el.dataset.prefixo || '';
      var decimais = el.dataset.decimais ? parseInt(el.dataset.decimais) : 0;
      var inicio = null, duracao = 900;
      function passo(ts) {
        if (!inicio) inicio = ts;
        var p = Math.min((ts - inicio) / duracao, 1);
        var suave = 1 - Math.pow(1 - p, 3); // ease-out cúbico
        el.textContent = prefixo + (alvo * suave).toLocaleString('pt-BR', {
          minimumFractionDigits: decimais, maximumFractionDigits: decimais
        });
        if (p < 1) requestAnimationFrame(passo);
      }
      requestAnimationFrame(passo);
    });
  }

  /* ===== Dropdown premium (substitui os <select>) ===== */
  var SETA = '<svg viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>';
  var CHECK = '<svg viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg>';
  var abertoAgora = null;

  function fecharDd(dd) {
    if (!dd) return;
    dd.classList.remove('aberto');
    if (abertoAgora === dd) abertoAgora = null;
  }

  function melhorarSelect(sel) {
    var dd = document.createElement('div');
    dd.className = 'dd';
    sel.parentNode.insertBefore(dd, sel);
    dd.appendChild(sel);

    var gatilho = document.createElement('button');
    gatilho.type = 'button';
    gatilho.className = 'dd-gatilho';
    gatilho.setAttribute('aria-haspopup', 'listbox');
    gatilho.innerHTML = '<span class="dd-valor"></span><span class="dd-seta">' + SETA + '</span>';
    dd.appendChild(gatilho);

    var painel = document.createElement('div');
    painel.className = 'dd-painel';
    painel.setAttribute('role', 'listbox');
    dd.appendChild(painel);

    var valor = gatilho.querySelector('.dd-valor');
    var opcoes = [];

    Array.prototype.forEach.call(sel.options, function (opt, i) {
      var el = document.createElement('div');
      el.className = 'dd-opcao' + (opt.value === '' ? ' placeholder' : '');
      el.setAttribute('role', 'option');
      el.style.setProperty('--i', i);
      el.dataset.valor = opt.value;
      el.innerHTML = '<span></span><span class="dd-check">' + CHECK + '</span>';
      el.firstChild.textContent = opt.textContent.replace(/\s+/g, ' ').trim();
      el.addEventListener('click', function () {
        escolher(i);
        fecharDd(dd);
        gatilho.focus();
      });
      painel.appendChild(el);
      opcoes.push(el);
    });

    function sincronizar() {
      var i = sel.selectedIndex;
      opcoes.forEach(function (el, j) { el.classList.toggle('selecionada', j === i); });
      var texto = i >= 0 ? opcoes[i].firstChild.textContent : '';
      valor.textContent = texto;
      valor.classList.toggle('dd-vazio', i < 0 || sel.options[i].value === '');
    }

    function escolher(i) {
      if (sel.selectedIndex !== i) {
        sel.selectedIndex = i;
        sel.dispatchEvent(new Event('change', { bubbles: true }));
      }
      sincronizar();
    }

    function focar(i) {
      opcoes.forEach(function (el, j) { el.classList.toggle('focada', j === i); });
      if (opcoes[i]) opcoes[i].scrollIntoView({ block: 'nearest' });
    }

    function alternar() {
      if (dd.classList.contains('aberto')) { fecharDd(dd); return; }
      if (abertoAgora) fecharDd(abertoAgora);
      var r = gatilho.getBoundingClientRect();
      dd.classList.toggle('acima', window.innerHeight - r.bottom < 300 && r.top > 300);
      dd.classList.add('aberto');
      abertoAgora = dd;
      focar(Math.max(sel.selectedIndex, 0));
    }

    gatilho.addEventListener('click', alternar);
    gatilho.addEventListener('keydown', function (e) {
      var aberto = dd.classList.contains('aberto');
      var focada = opcoes.findIndex(function (el) { return el.classList.contains('focada'); });
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        if (!aberto) { alternar(); return; }
        var passo = e.key === 'ArrowDown' ? 1 : -1;
        focar(Math.min(Math.max(focada + passo, 0), opcoes.length - 1));
      } else if ((e.key === 'Enter' || e.key === ' ') && aberto) {
        e.preventDefault();
        if (focada >= 0) escolher(focada);
        fecharDd(dd);
      } else if (e.key === 'Escape' && aberto) {
        e.preventDefault();
        fecharDd(dd);
      } else if (e.key === 'Home' && aberto) { e.preventDefault(); focar(0); }
      else if (e.key === 'End' && aberto) { e.preventDefault(); focar(opcoes.length - 1); }
    });

    sel.addEventListener('change', sincronizar);
    sel.addEventListener('invalid', function () { gatilho.focus(); });
    sincronizar();
  }

  /* ===== Seletor de data & hora premium (substitui os datetime-local) ===== */
  var ICONE_CAL = '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>';
  var SETA_ESQ = '<svg viewBox="0 0 24 24"><path d="M15 18l-6-6 6-6"/></svg>';
  var SETA_DIR = '<svg viewBox="0 0 24 24"><path d="M9 6l6 6-6 6"/></svg>';
  var DIAS_SEMANA = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S'];
  var abertoDtp = null;

  function pad(n) { return String(n).padStart(2, '0'); }
  function mesmoDia(a, b) {
    return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
  }
  function fecharDtp(dtp) {
    if (!dtp) return;
    dtp.classList.remove('aberto');
    if (abertoDtp === dtp) abertoDtp = null;
  }

  function melhorarData(inp) {
    var dtp = document.createElement('div');
    dtp.className = 'dd dtp';
    inp.parentNode.insertBefore(dtp, inp);
    dtp.appendChild(inp);

    var gatilho = document.createElement('button');
    gatilho.type = 'button';
    gatilho.className = 'dd-gatilho';
    gatilho.innerHTML = '<span class="dd-valor"></span><span class="dd-seta">' + ICONE_CAL + '</span>';
    dtp.appendChild(gatilho);

    var painel = document.createElement('div');
    painel.className = 'dd-painel dtp-painel';
    painel.innerHTML =
      '<div class="dtp-cal">' +
        '<div class="dtp-topo">' +
          '<button type="button" class="dtp-nav" data-passo="-1" aria-label="Mês anterior">' + SETA_ESQ + '</button>' +
          '<span class="dtp-mes"></span>' +
          '<button type="button" class="dtp-nav" data-passo="1" aria-label="Próximo mês">' + SETA_DIR + '</button>' +
        '</div>' +
        '<div class="dtp-semana">' + DIAS_SEMANA.map(function (d) { return '<span>' + d + '</span>'; }).join('') + '</div>' +
        '<div class="dtp-grade"></div>' +
      '</div>' +
      '<div class="dtp-tempo">' +
        '<div class="dtp-col"><b>HORA</b><div class="dtp-rolagem" data-col="h"></div></div>' +
        '<div class="dtp-col"><b>MIN</b><div class="dtp-rolagem" data-col="m"></div></div>' +
      '</div>' +
      '<div class="dtp-rodape">' +
        '<button type="button" class="dtp-botao" data-acao="limpar">Limpar</button>' +
        '<button type="button" class="dtp-botao" data-acao="agora">Agora</button>' +
        '<span class="dtp-espaco"></span>' +
        '<button type="button" class="dtp-botao principal" data-acao="ok">OK</button>' +
      '</div>';
    dtp.appendChild(painel);

    var valor = gatilho.querySelector('.dd-valor');
    var rotuloMes = painel.querySelector('.dtp-mes');
    var grade = painel.querySelector('.dtp-grade');
    var colH = painel.querySelector('[data-col="h"]');
    var colM = painel.querySelector('[data-col="m"]');

    var visto = new Date(); visto.setDate(1);
    var sel = null, selH = 8, selM = 0;

    function lerValor() {
      if (!inp.value) return;
      var d = new Date(inp.value);
      if (isNaN(d)) return;
      sel = d; selH = d.getHours(); selM = d.getMinutes();
      visto = new Date(d.getFullYear(), d.getMonth(), 1);
    }

    function escrever() {
      if (!sel) return;
      inp.value = sel.getFullYear() + '-' + pad(sel.getMonth() + 1) + '-' + pad(sel.getDate()) +
                  'T' + pad(selH) + ':' + pad(selM);
      inp.dispatchEvent(new Event('change', { bubbles: true }));
      atualizarGatilho();
    }

    function atualizarGatilho() {
      if (sel) {
        valor.textContent = pad(sel.getDate()) + '/' + pad(sel.getMonth() + 1) + '/' + sel.getFullYear() +
                            '  ·  ' + pad(selH) + ':' + pad(selM);
        valor.classList.remove('dd-vazio');
      } else {
        valor.textContent = 'Escolha data e hora…';
        valor.classList.add('dd-vazio');
      }
    }

    function renderCal() {
      rotuloMes.textContent = visto.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
      grade.innerHTML = '';
      var primeiro = new Date(visto.getFullYear(), visto.getMonth(), 1).getDay();
      var hoje = new Date();
      for (var c = 0; c < 42; c++) {
        var d = new Date(visto.getFullYear(), visto.getMonth(), c - primeiro + 1);
        var cel = document.createElement('div');
        cel.className = 'dtp-dia';
        cel.textContent = d.getDate();
        if (d.getMonth() !== visto.getMonth()) cel.classList.add('fora');
        if (mesmoDia(d, hoje)) cel.classList.add('hoje');
        if (sel && mesmoDia(d, sel)) cel.classList.add('selecionado');
        (function (d) {
          cel.addEventListener('click', function (e) {
            e.stopPropagation();
            sel = d;
            visto = new Date(d.getFullYear(), d.getMonth(), 1);
            escrever();
            renderCal();
          });
        })(d);
        grade.appendChild(cel);
      }
    }

    function itemTempo(col, texto, ativo, aoClicar) {
      var el = document.createElement('div');
      el.className = 'dtp-item' + (ativo ? ' selecionado' : '');
      el.textContent = texto;
      el.addEventListener('click', aoClicar);
      col.appendChild(el);
    }

    function renderTempo() {
      colH.innerHTML = ''; colM.innerHTML = '';
      for (var h = 0; h < 24; h++) {
        (function (h) {
          itemTempo(colH, pad(h), h === selH, function () {
            selH = h;
            if (sel) escrever(); else atualizarGatilho();
            renderTempo();
          });
        })(h);
      }
      var minutos = [];
      for (var m = 0; m < 60; m += 5) minutos.push(m);
      if (minutos.indexOf(selM) < 0) { minutos.push(selM); minutos.sort(function (a, b) { return a - b; }); }
      minutos.forEach(function (m) {
        itemTempo(colM, pad(m), m === selM, function () {
          selM = m;
          if (sel) escrever();
          renderTempo();
        });
      });
    }

    function centralizar() {
      [colH, colM].forEach(function (col) {
        var ativo = col.querySelector('.selecionado');
        if (ativo) col.scrollTop = ativo.offsetTop - col.clientHeight / 2 + ativo.clientHeight / 2;
      });
    }

    function alternar() {
      if (dtp.classList.contains('aberto')) { fecharDtp(dtp); return; }
      if (abertoDtp) fecharDtp(abertoDtp);
      lerValor(); renderCal(); renderTempo(); atualizarGatilho();
      var r = gatilho.getBoundingClientRect();
      dtp.classList.toggle('acima', window.innerHeight - r.bottom < 420 && r.top > 420);
      dtp.classList.add('aberto');
      abertoDtp = dtp;
      centralizar();
    }

    gatilho.addEventListener('click', alternar);

    painel.querySelectorAll('.dtp-nav').forEach(function (btn) {
      btn.addEventListener('click', function () {
        visto.setMonth(visto.getMonth() + parseInt(btn.dataset.passo));
        renderCal();
      });
    });

    painel.querySelectorAll('.dtp-botao').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var acao = btn.dataset.acao;
        if (acao === 'limpar') {
          sel = null; inp.value = '';
          inp.dispatchEvent(new Event('change', { bubbles: true }));
          atualizarGatilho(); renderCal();
        } else if (acao === 'agora') {
          var n = new Date();
          selM = Math.ceil(n.getMinutes() / 5) * 5;
          selH = n.getHours();
          if (selM === 60) { selM = 0; selH = (selH + 1) % 24; if (selH === 0) n.setDate(n.getDate() + 1); }
          sel = n;
          visto = new Date(n.getFullYear(), n.getMonth(), 1);
          escrever(); renderCal(); renderTempo(); centralizar();
        } else if (acao === 'ok') {
          fecharDtp(dtp);
          gatilho.focus();
        }
      });
    });

    gatilho.addEventListener('keydown', function (e) {
      if ((e.key === 'ArrowDown' || e.key === 'Enter' || e.key === ' ') && !dtp.classList.contains('aberto')) {
        e.preventDefault(); alternar();
      } else if (e.key === 'Escape') { fecharDtp(dtp); }
    });

    inp.addEventListener('invalid', function () { gatilho.focus(); });
    lerValor(); atualizarGatilho();
  }

  /* ===== Multi-select premium (checkboxes como dropdown com chips) ===== */
  var X_ICO = '<svg viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12"/></svg>';
  var abertoMs = null;

  function fecharMs(ms) {
    if (!ms) return;
    ms.classList.remove('aberto');
    if (abertoMs === ms) abertoMs = null;
  }

  function melhorarMultiSelect(ms) {
    var placeholder = ms.dataset.placeholder || 'Selecione…';
    var itens = ms.querySelectorAll('.multi-sel-item');

    var gatilho = document.createElement('button');
    gatilho.type = 'button';
    gatilho.className = 'ms-gatilho';
    gatilho.innerHTML = '<span class="ms-valor"></span><span class="dd-seta">' + SETA + '</span>';
    ms.insertBefore(gatilho, ms.firstChild);

    var painel = document.createElement('div');
    painel.className = 'ms-painel';
    painel.addEventListener('click', function (e) { e.stopPropagation(); e.preventDefault(); });
    ms.appendChild(painel);

    var valSpan = gatilho.querySelector('.ms-valor');
    var opcoes = [];

    itens.forEach(function (item, i) {
      var cb = item.querySelector('input[type="checkbox"]');
      var nome = item.querySelector('span').textContent.trim();
      var el = document.createElement('div');
      el.className = 'ms-opcao';
      el.setAttribute('role', 'option');
      el.style.setProperty('--i', i);
      el.innerHTML = '<span class="ms-caixa">' + CHECK + '</span><span>' + esc(nome) + '</span>';
      el.addEventListener('click', function (e) {
        e.stopPropagation();
        cb.checked = !cb.checked;
        el.classList.toggle('marcado', cb.checked);
        sincronizar();
      });
      painel.appendChild(el);
      opcoes.push({ el: el, cb: cb, nome: nome });
    });

    function sincronizar() {
      valSpan.innerHTML = '';
      var selecionados = opcoes.filter(function (o) { return o.cb.checked; });
      if (selecionados.length === 0) {
        valSpan.textContent = placeholder;
        valSpan.classList.add('ms-vazio');
      } else {
        valSpan.classList.remove('ms-vazio');
        selecionados.forEach(function (o) {
          var chip = document.createElement('span');
          chip.className = 'ms-chip';
          chip.innerHTML = '<span>' + esc(o.nome) + '</span><span class="ms-x">' + X_ICO + '</span>';
          chip.querySelector('.ms-x').addEventListener('click', function (e) {
            e.stopPropagation();
            o.cb.checked = false;
            o.el.classList.remove('marcado');
            sincronizar();
          });
          valSpan.appendChild(chip);
        });
      }
    }

    function alternar() {
      if (ms.classList.contains('aberto')) { fecharMs(ms); return; }
      if (abertoMs) fecharMs(abertoMs);
      ms.classList.add('aberto');
      abertoMs = ms;
    }

    gatilho.addEventListener('click', alternar);
    ms.sincronizar = sincronizar;
    sincronizar();
  }

  /* ===== melhorar(raiz): aplica os componentes ao conteúdo renderizado ===== */
  function melhorar(raiz) {
    raiz = raiz || document;
    raiz.querySelectorAll('select').forEach(function (sel) {
      if (!sel.closest('.dd')) melhorarSelect(sel);
    });
    raiz.querySelectorAll('input[type="datetime-local"]').forEach(function (inp) {
      if (!inp.closest('.dtp')) melhorarData(inp);
    });
    raiz.querySelectorAll('.multi-sel').forEach(function (ms) {
      if (!ms.dataset.melhorado) { ms.dataset.melhorado = '1'; melhorarMultiSelect(ms); }
    });
    animarNumeros();
  }

  /* fechar dropdowns abertos ao clicar fora / Escape (registrado uma vez) */
  document.addEventListener('click', function (e) {
    if (abertoAgora && !abertoAgora.contains(e.target)) fecharDd(abertoAgora);
    if (abertoDtp && !abertoDtp.contains(e.target)) fecharDtp(abertoDtp);
    if (abertoMs && !abertoMs.contains(e.target)) fecharMs(abertoMs);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { fecharDd(abertoAgora); fecharDtp(abertoDtp); fecharMs(abertoMs); }
  });

  /* ===== Modal de confirmação premium ===== */
  var fundo = document.createElement('div');
  fundo.className = 'modal-fundo';
  fundo.innerHTML =
    '<div class="modal-caixa" role="alertdialog" aria-modal="true">' +
      '<div class="modal-icone">' +
        '<svg viewBox="0 0 24 24"><path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M10 11v6M14 11v6"/></svg>' +
      '</div>' +
      '<h3></h3>' +
      '<p></p>' +
      '<div class="modal-acoes">' +
        '<button type="button" class="modal-cancelar">Voltar</button>' +
        '<button type="button" class="modal-confirmar"></button>' +
      '</div>' +
    '</div>';
  document.body.appendChild(fundo);

  var modalTitulo = fundo.querySelector('h3');
  var modalMensagem = fundo.querySelector('p');
  var btnCancelar = fundo.querySelector('.modal-cancelar');
  var btnConfirmar = fundo.querySelector('.modal-confirmar');
  var acaoPendente = null;

  function confirmar(opcoes, aoConfirmar) {
    modalTitulo.textContent = opcoes.titulo || 'Tem certeza?';
    modalMensagem.textContent = opcoes.mensagem || '';
    btnConfirmar.textContent = opcoes.botao || 'Confirmar';
    acaoPendente = aoConfirmar;
    fundo.classList.add('aberto');
    setTimeout(function () { btnCancelar.focus(); }, 60);
  }

  function fecharModal() {
    fundo.classList.remove('aberto');
    acaoPendente = null;
  }

  btnConfirmar.addEventListener('click', function () {
    var acao = acaoPendente;
    fecharModal();
    if (acao) acao();
  });
  btnCancelar.addEventListener('click', fecharModal);
  fundo.addEventListener('click', function (e) { if (e.target === fundo) fecharModal(); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && fundo.classList.contains('aberto')) fecharModal();
  });

  return {
    api: api, esc: esc, moeda: moeda, dataHora: dataHora,
    erroTopo: erroTopo, animarNumeros: animarNumeros,
    melhorar: melhorar, confirmar: confirmar
  };
})();
