/* =====================================================================
   base.js — a biblioteca compartilhada do front-end (HTML + JS puro).

   O painel não usa Jinja2: cada página chama as rotas /api/... via
   fetch e monta o HTML no navegador.

     HubUI.api()        → wrapper do fetch (erro da API vira exceção)
     HubUI.ico()        → ícone em traço do sprite — NUNCA emoji
     HubUI.arco()       → o arco de proporção (um por tela)
     HubUI.melhorar()   → menu suspenso, data/hora e multi-seleção
     HubUI.confirmar()  → <dialog> de confirmação
     HubUI.informar()   → <dialog> de aviso (não existe alert() aqui)
     HubUI.toast()      → aviso flutuante
     HubUI.erroTopo()   → erro fixo no topo da página
     HubUI.carregando() → desabilita o botão enquanto a chamada corre
     esc, moeda, dataHora, telefone, cnpj, animarNumeros

   Duas regras que moram no código, não no comentário:
   - NENHUM estilo é escrito por JavaScript. Estado é classe ou
     atributo; a CSP bloqueia element.style e falha calada.
   - NENHUMA cor literal. Tudo vem de token, pelo CSS.
   ===================================================================== */
window.HubUI = (function () {
  'use strict';

  /* ========================= utilitários ========================= */

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

  function dataHora(t) {
    var texto = String(t || '');
    if (!texto) return '—';
    var partes = texto.split('T');
    if (partes.length < 2) return esc(texto);
    var d = partes[0].split('-');
    return esc(d[2] + '/' + d[1] + '/' + d[0] + ' ' + partes[1].slice(0, 5));
  }

  function telefone(v) {
    var n = String(v || '').replace(/\D/g, '');
    if (n.length === 11) return '(' + n.slice(0, 2) + ') ' + n.slice(2, 7) + '-' + n.slice(7);
    if (n.length === 10) return '(' + n.slice(0, 2) + ') ' + n.slice(2, 6) + '-' + n.slice(6);
    return esc(v);
  }

  function cnpj(v) {
    var n = String(v || '').replace(/\D/g, '');
    if (n.length !== 14) return esc(v);
    return n.slice(0, 2) + '.' + n.slice(2, 5) + '.' + n.slice(5, 8) +
           '/' + n.slice(8, 12) + '-' + n.slice(12);
  }

  function cpf(v) {
    var n = String(v || '').replace(/\D/g, '');
    if (n.length !== 11) return esc(v);
    return n.slice(0, 3) + '.' + n.slice(3, 6) + '.' + n.slice(6, 9) + '-' + n.slice(9);
  }

  /* ========================= máscara ao digitar =========================
     O servidor guarda só os dígitos; a pontuação é apresentação, e é aqui
     que ela nasce. O campo declara qual forma quer:

         <input name="cpf" data-mascara="cpf">

     Um padrão por forma, e `0` é onde entra dígito. Assim a máscara
     cresce junto com o que foi digitado — "1234" vira "123.4" — em vez de
     só aparecer quando o campo está completo. */

  var PADROES = {
    cpf: '000.000.000-00',
    cnpj: '00.000.000/0000-00',
    telefone: '(00) 00000-0000',
    telefoneCurto: '(00) 0000-0000'
  };

  function porPadrao(valor, padrao) {
    var cabem = (padrao.match(/0/g) || []).length;
    var digitos = String(valor || '').replace(/\D/g, '').slice(0, cabem);
    var saida = '';
    for (var p = 0, i = 0; p < padrao.length && i < digitos.length; p++) {
      saida += padrao[p] === '0' ? digitos[i++] : padrao[p];
    }
    return saida;
  }

  function mascarar(valor, forma) {
    if (forma === 'telefone') {
      var n = String(valor || '').replace(/\D/g, '');
      // Fixo tem 8 dígitos e celular tem 9: o padrão só troca quando o
      // nono chega, para o campo não embaralhar no meio da digitação.
      return porPadrao(n, n.length > 10 ? PADROES.telefone : PADROES.telefoneCurto);
    }
    return PADROES[forma] ? porPadrao(valor, PADROES[forma]) : String(valor || '');
  }

  function aplicarMascara(inp) {
    var forma = inp.dataset.mascara;
    if (!forma || !(PADROES[forma] || forma === 'telefone')) return;
    if (!inp.getAttribute('inputmode')) inp.setAttribute('inputmode', 'numeric');

    function reformatar() {
      // A distância até o FIM é o que se preserva, não a posição absoluta:
      // a máscara insere pontuação à esquerda do cursor, e medir do começo
      // joga o cursor para trás a cada ponto inserido.
      var daDireita = inp.value.length - (inp.selectionEnd || inp.value.length);
      inp.value = mascarar(inp.value, forma);
      var pos = Math.max(0, inp.value.length - daDireita);
      try { inp.setSelectionRange(pos, pos); } catch (e) { /* campo sem seleção */ }
    }

    inp.addEventListener('input', reformatar);
    inp.addEventListener('blur', reformatar);
    if (inp.value) inp.value = mascarar(inp.value, forma);
  }

  /* ========================= ícones =========================
     Traço, do sprite embutido no HTML. O <use href> externo não
     funciona no Chrome, por isso o sprite mora na própria página. */

  function ico(nome, classe) {
    return '<svg class="' + (classe || 'ico') + '" aria-hidden="true" focusable="false">' +
           '<use href="#' + nome + '"></use></svg>';
  }

  /* O arco de proporção: o valor vai em ATRIBUTO DE APRESENTAÇÃO do
     SVG (não em style), que é o que a CSP permite e o que a transição
     do CSS consegue animar. */
  function arco(fracao, rotulo) {
    var r = 18;
    var volta = 2 * Math.PI * r;
    var cheio = Math.max(0, Math.min(1, Number(fracao) || 0));
    return '<span class="arco-meta" role="img" aria-label="' + esc(rotulo || '') + '">' +
             '<svg viewBox="0 0 44 44">' +
               '<circle class="trilho" cx="22" cy="22" r="' + r + '"></circle>' +
               '<circle class="arco" cx="22" cy="22" r="' + r + '" ' +
                 'stroke-dasharray="' + volta.toFixed(2) + '" ' +
                 'stroke-dashoffset="' + (volta * (1 - cheio)).toFixed(2) + '"></circle>' +
             '</svg>' +
           '</span>';
  }

  /* ========================= avisos ========================= */

  function erroTopo(msg) {
    var antigo = document.querySelector('.erro-topo');
    if (antigo) antigo.remove();
    if (!msg) return;
    var div = document.createElement('div');
    div.className = 'erro-topo';
    div.setAttribute('role', 'alert');
    div.innerHTML = ico('i-alerta') + '<span></span>';
    div.querySelector('span').textContent = msg;
    var main = document.querySelector('main');
    main.insertBefore(div, main.firstChild);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  /* O que deu certo some em 4s; o que deu ERRADO só some no clique,
     porque erro que desaparece sozinho é erro que ninguém leu. */
  function toast(mensagem, tipo) {
    var antigo = document.querySelector('.aviso-flutuante');
    if (antigo) antigo.remove();

    var caixa = document.createElement('div');
    caixa.className = 'aviso-flutuante' + (tipo ? ' ' + tipo : '');
    caixa.setAttribute('role', tipo === 'erro' ? 'alert' : 'status');
    caixa.innerHTML = ico(tipo === 'erro' ? 'i-x-circulo' : 'i-ok-circulo') + '<span></span>';
    caixa.querySelector('span').textContent = mensagem;

    var fechar = document.createElement('button');
    fechar.type = 'button';
    fechar.className = 'botao-menor';
    fechar.innerHTML = ico('i-x');
    fechar.setAttribute('aria-label', 'Fechar aviso');
    fechar.addEventListener('click', function () { caixa.remove(); });
    caixa.appendChild(fechar);

    document.body.appendChild(caixa);
    if (tipo !== 'erro') setTimeout(function () { caixa.remove(); }, 4000);
  }

  function carregando(botao, ligado) {
    if (!botao) return;
    botao.disabled = !!ligado;
    botao.setAttribute('aria-busy', ligado ? 'true' : 'false');
  }

  /* ========================= <dialog> =========================
     Não existe alert() neste projeto. */

  function montarDialogo() {
    var dlg = document.createElement('dialog');
    dlg.className = 'modal';
    dlg.innerHTML =
      '<div class="modal-icone"></div>' +
      '<h3></h3><p></p>' +
      '<div class="modal-acoes">' +
        '<button type="button" class="modal-cancelar">Voltar</button>' +
        '<button type="button" class="modal-confirmar principal"></button>' +
      '</div>';
    document.body.appendChild(dlg);
    return dlg;
  }

  var dialogo = null;
  var acaoPendente = null;

  function garantirDialogo() {
    if (dialogo) return dialogo;
    dialogo = montarDialogo();
    dialogo.querySelector('.modal-cancelar').addEventListener('click', function () {
      acaoPendente = null;
      dialogo.close();
    });
    dialogo.querySelector('.modal-confirmar').addEventListener('click', function () {
      var acao = acaoPendente;
      acaoPendente = null;
      dialogo.close();
      if (acao) acao();
    });
    return dialogo;
  }

  function abrirDialogo(opcoes, aoConfirmar) {
    var dlg = garantirDialogo();
    dlg.classList.toggle('perigo', opcoes.tom === 'perigo');
    dlg.querySelector('.modal-icone').innerHTML =
      ico(opcoes.icone || (opcoes.tom === 'perigo' ? 'i-alerta' : 'i-ok-circulo'), 'ico-grande');
    dlg.querySelector('h3').textContent = opcoes.titulo || 'Tem certeza?';
    dlg.querySelector('p').textContent = opcoes.mensagem || '';
    dlg.querySelector('.modal-confirmar').textContent = opcoes.botao || 'Confirmar';
    dlg.querySelector('.modal-cancelar').hidden = !aoConfirmar;
    acaoPendente = aoConfirmar || null;
    dlg.showModal();
    dlg.querySelector(aoConfirmar ? '.modal-cancelar' : '.modal-confirmar').focus();
  }

  function confirmar(opcoes, aoConfirmar) {
    abrirDialogo(opcoes, aoConfirmar);
  }

  function informar(opcoes) {
    abrirDialogo({
      titulo: opcoes.titulo, mensagem: opcoes.mensagem,
      botao: opcoes.botao || 'Entendi', icone: opcoes.icone, tom: opcoes.tom
    }, null);
  }

  /* ========================= números animados ========================= */

  function animarNumeros() {
    var reduzido = window.matchMedia &&
                   window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    document.querySelectorAll('.numero[data-valor]').forEach(function (el) {
      if (el.dataset.animado) return;
      el.dataset.animado = '1';
      var alvo = parseFloat(el.dataset.valor) || 0;
      var prefixo = el.dataset.prefixo || '';
      var decimais = el.dataset.decimais ? parseInt(el.dataset.decimais, 10) : 0;

      function escrever(v) {
        el.textContent = prefixo + v.toLocaleString('pt-BR', {
          minimumFractionDigits: decimais, maximumFractionDigits: decimais
        });
      }
      if (reduzido) { escrever(alvo); return; }

      var inicio = null, duracao = 720;  /* animação de DADO */
      function passo(ts) {
        if (!inicio) inicio = ts;
        var p = Math.min((ts - inicio) / duracao, 1);
        escrever(alvo * (1 - Math.pow(1 - p, 3)));
        if (p < 1) requestAnimationFrame(passo);
      }
      requestAnimationFrame(passo);
    });
  }

  /* ========================= menu suspenso (.dd) ========================= */

  var abertoDd = null, abertoDtp = null, abertoMs = null;

  function fecharDd(dd) {
    if (!dd) return;
    dd.classList.remove('aberto');
    if (abertoDd === dd) abertoDd = null;
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
    gatilho.innerHTML = '<span class="dd-valor"></span><span class="dd-seta">' + ico('i-seta') + '</span>';
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
      el.innerHTML = '<span></span><span class="dd-check">' + ico('i-ok') + '</span>';
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
      valor.textContent = i >= 0 ? opcoes[i].firstChild.textContent : '';
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
      if (abertoDd) fecharDd(abertoDd);
      var r = gatilho.getBoundingClientRect();
      dd.classList.toggle('acima', window.innerHeight - r.bottom < 300 && r.top > 300);
      dd.classList.add('aberto');
      abertoDd = dd;
      focar(Math.max(sel.selectedIndex, 0));
    }

    gatilho.addEventListener('click', alternar);
    gatilho.addEventListener('keydown', function (e) {
      var aberto = dd.classList.contains('aberto');
      var focada = opcoes.findIndex(function (el) { return el.classList.contains('focada'); });
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        if (!aberto) { alternar(); return; }
        focar(Math.min(Math.max(focada + (e.key === 'ArrowDown' ? 1 : -1), 0), opcoes.length - 1));
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

  /* ========================= data e hora (.dtp) ========================= */

  var DIAS_SEMANA = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S'];

  function pad(n) { return String(n).padStart(2, '0'); }
  function mesmoDia(a, b) {
    return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() &&
           a.getDate() === b.getDate();
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
    /* o campo real continua no DOM, reduzido a 1px pelo CSS — e NÃO
       com hidden: um campo required escondido não é focável, e o
       navegador recusa o envio com "not focusable" sem dizer onde. */

    var gatilho = document.createElement('button');
    gatilho.type = 'button';
    gatilho.className = 'dd-gatilho';
    gatilho.innerHTML = '<span class="dd-valor"></span><span class="dd-icone">' + ico('i-agenda') + '</span>';
    dtp.appendChild(gatilho);

    var painel = document.createElement('div');
    painel.className = 'dd-painel dtp-painel';
    painel.innerHTML =
      '<div class="dtp-cal">' +
        '<div class="dtp-topo">' +
          '<button type="button" class="dtp-nav anterior" aria-label="Mês anterior">' + ico('i-seta') + '</button>' +
          '<span class="dtp-mes"></span>' +
          '<button type="button" class="dtp-nav proximo" aria-label="Próximo mês">' + ico('i-seta') + '</button>' +
        '</div>' +
        '<div class="dtp-semana">' +
          DIAS_SEMANA.map(function (d) { return '<span>' + d + '</span>'; }).join('') +
        '</div>' +
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
      if (!inp.value) { sel = null; return; }
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
        valor.textContent = pad(sel.getDate()) + '/' + pad(sel.getMonth() + 1) + '/' +
                            sel.getFullYear() + '  ·  ' + pad(selH) + ':' + pad(selM);
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
        (function (dia) {
          cel.addEventListener('click', function (e) {
            e.stopPropagation();
            sel = dia;
            visto = new Date(dia.getFullYear(), dia.getMonth(), 1);
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
        (function (hora) {
          itemTempo(colH, pad(hora), hora === selH, function () {
            selH = hora;
            if (sel) escrever(); else atualizarGatilho();
            renderTempo();
          });
        })(h);
      }
      var minutos = [];
      for (var m = 0; m < 60; m += 5) minutos.push(m);
      if (minutos.indexOf(selM) < 0) { minutos.push(selM); minutos.sort(function (a, b) { return a - b; }); }
      minutos.forEach(function (min) {
        itemTempo(colM, pad(min), min === selM, function () {
          selM = min;
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
    painel.querySelector('.anterior').addEventListener('click', function () {
      visto.setMonth(visto.getMonth() - 1); renderCal();
    });
    painel.querySelector('.proximo').addEventListener('click', function () {
      visto.setMonth(visto.getMonth() + 1); renderCal();
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
          if (selM === 60) { selM = 0; selH = (selH + 1) % 24; }
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
      if ((e.key === 'ArrowDown' || e.key === 'Enter' || e.key === ' ') &&
          !dtp.classList.contains('aberto')) {
        e.preventDefault(); alternar();
      } else if (e.key === 'Escape') { fecharDtp(dtp); }
    });

    inp.addEventListener('invalid', function () { gatilho.focus(); });
    inp.addEventListener('reiniciado', function () { lerValor(); atualizarGatilho(); });
    lerValor(); atualizarGatilho();
  }

  /* ========================= multi-seleção ========================= */

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
    gatilho.innerHTML = '<span class="ms-valor"></span><span class="dd-seta">' + ico('i-seta') + '</span>';
    ms.insertBefore(gatilho, ms.firstChild);

    var painel = document.createElement('div');
    painel.className = 'ms-painel';
    painel.addEventListener('click', function (e) { e.stopPropagation(); });
    ms.appendChild(painel);

    var valSpan = gatilho.querySelector('.ms-valor');
    var opcoes = [];

    itens.forEach(function (item) {
      var cb = item.querySelector('input[type="checkbox"]');
      var nome = item.querySelector('span').textContent.trim();
      var el = document.createElement('div');
      el.className = 'ms-opcao';
      el.setAttribute('role', 'option');
      el.innerHTML = '<span class="ms-caixa">' + ico('i-ok') + '</span><span></span>';
      el.lastChild.textContent = nome;
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
      var marcados = opcoes.filter(function (o) { return o.cb.checked; });
      if (!marcados.length) {
        valSpan.textContent = placeholder;
        valSpan.classList.add('ms-vazio');
        return;
      }
      valSpan.classList.remove('ms-vazio');
      marcados.forEach(function (o) {
        var chip = document.createElement('span');
        chip.className = 'ms-chip';
        chip.innerHTML = '<span></span><span class="ms-x">' + ico('i-x') + '</span>';
        chip.firstChild.textContent = o.nome;
        chip.querySelector('.ms-x').addEventListener('click', function (e) {
          e.stopPropagation();
          o.cb.checked = false;
          o.el.classList.remove('marcado');
          sincronizar();
        });
        valSpan.appendChild(chip);
      });
    }

    gatilho.addEventListener('click', function () {
      if (ms.classList.contains('aberto')) { fecharMs(ms); return; }
      if (abertoMs) fecharMs(abertoMs);
      ms.classList.add('aberto');
      abertoMs = ms;
    });

    ms.sincronizar = function () {
      opcoes.forEach(function (o) { o.el.classList.toggle('marcado', o.cb.checked); });
      sincronizar();
    };
    sincronizar();
  }

  /* ========================= melhorar(raiz) ========================= */

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
    raiz.querySelectorAll('input[data-mascara]').forEach(function (inp) {
      if (!inp.dataset.mascarado) { inp.dataset.mascarado = '1'; aplicarMascara(inp); }
    });
    animarNumeros();
  }

  /* fecha o que estiver aberto ao clicar fora, ou no Esc */
  document.addEventListener('click', function (e) {
    if (abertoDd && !abertoDd.contains(e.target)) fecharDd(abertoDd);
    if (abertoDtp && !abertoDtp.contains(e.target)) fecharDtp(abertoDtp);
    if (abertoMs && !abertoMs.contains(e.target)) fecharMs(abertoMs);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { fecharDd(abertoDd); fecharDtp(abertoDtp); fecharMs(abertoMs); }
  });

  /* ========================= cabeçalho: o tema ========================= */

  function ligarPreferencias() {
    var btnTema = document.querySelector('.botao-tema');

    function pintarTema() {
      if (!btnTema || !window.HubTema) return;
      var escuro = window.HubTema.atual() === 'escuro';
      btnTema.innerHTML = ico(escuro ? 'i-sol' : 'i-lua');
      btnTema.setAttribute('aria-label', escuro ? 'Usar tema claro' : 'Usar tema escuro');
      btnTema.setAttribute('title', btnTema.getAttribute('aria-label'));
    }
    if (btnTema) {
      btnTema.addEventListener('click', function () {
        window.HubTema.alternar();
        pintarTema();
      });
    }
    pintarTema();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ligarPreferencias);
  } else {
    ligarPreferencias();
  }

  return {
    api: api, esc: esc, moeda: moeda, dataHora: dataHora,
    telefone: telefone, cnpj: cnpj, cpf: cpf, mascarar: mascarar,
    ico: ico, arco: arco,
    erroTopo: erroTopo, toast: toast, carregando: carregando,
    confirmar: confirmar, informar: informar,
    melhorar: melhorar, animarNumeros: animarNumeros
  };
})();
