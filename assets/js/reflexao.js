/* Quadro de post-its da Sprint Planning 3 (ADR-006).

   Modos, pela URL de aulas/reflexao-sprint2.html:
     ?g=G01&t=TOKEN   quadro do grupo: cada integrante escreve no próprio bloco
     ?painel=1        painel do professor: links, prazo, participação e leitura
     &demo=1          sem banco, tudo em memória (ensaio e testes)

   O banco é o projeto Supabase m08-quiz (supabase/reflexao.sql). Toda leitura e
   escrita passa por funções refl_*; o token do grupo vem do link e a chave do
   professor fica só no navegador dele (localStorage 'inteli-quiz-chave'). */
(function () {
  'use strict';

  var SESSAO = 'si08t18-sp3-2026-11-09';
  var INTERVALO_MS = 2500;
  var GRUPOS = ['G01', 'G02', 'G03', 'G04', 'G05'];
  var CHAVE_PROFESSOR = 'inteli-quiz-chave';

  var PERGUNTAS = [
    {
      en: 'What was the goal of Sprint 2, in one sentence? Write it without asking your teammates.',
      pt: 'Qual era o objetivo da Sprint 2, em uma frase? Escreva sem consultar os colegas.',
      fr: 'Quel était l’objectif du sprint 2, en une phrase ? Écrivez-le sans consulter vos collègues.'
    },
    {
      en: 'What did you personally deliver in Sprint 2? Cite the issue or merge request in GitLab.',
      pt: 'O que você entregou na Sprint 2? Cite a issue ou o merge request no GitLab.',
      fr: 'Qu’avez-vous livré personnellement au sprint 2 ? Citez l’issue ou la merge request dans GitLab.'
    },
    {
      en: 'Who decided to make a single presentation for Sprint Review 2, when, and were you consulted?',
      pt: 'Quem decidiu fazer uma apresentação única na Sprint Review 2, quando, e você foi consultado?',
      fr: 'Qui a décidé de faire une présentation unique à la Sprint Review 2, quand, et avez-vous été consulté ?'
    },
    {
      en: 'Were the risks of that decision (delay, long presentation, failed demo) in the risk matrix? What was the mitigation?',
      pt: 'Os riscos dessa decisão (atraso, apresentação longa, falha na demonstração) estavam na matriz de risco? Qual era a mitigação?',
      fr: 'Les risques de cette décision (retard, présentation longue, démo ratée) figuraient-ils dans la matrice des risques ? Quelle était la mitigation ?'
    },
    {
      en: 'What will you do differently in Sprint 3, starting tomorrow? Write one commitment someone can check.',
      pt: 'O que você vai fazer diferente na Sprint 3, a partir de amanhã? Escreva um compromisso que alguém possa verificar.',
      fr: 'Que ferez-vous différemment au sprint 3, dès demain ? Écrivez un engagement vérifiable.'
    }
  ];

  var TEXTOS = {
    quemEVoce: { en: 'Who are you?', pt: 'Quem é você?', fr: 'Qui êtes-vous ?' },
    escolha: {
      en: 'Pick your name. Your post-its are signed with it.',
      pt: 'Escolha o seu nome. Os seus post-its saem assinados com ele.',
      fr: 'Choisissez votre nom. Vos post-it sont signés avec lui.'
    },
    trocar: { en: 'Not you?', pt: 'Não é você?', fr: 'Ce n’est pas vous ?' },
    escrever: { en: 'Write a post-it', pt: 'Escreva um post-it', fr: 'Écrivez un post-it' },
    colar: { en: 'Stick', pt: 'Colar', fr: 'Coller' },
    vazio: { en: 'No post-it yet', pt: 'Nenhum post-it ainda', fr: 'Aucun post-it' },
    encerrado: { en: 'Time is up', pt: 'Tempo encerrado', fr: 'Temps écoulé' },
    semLink: {
      en: 'This link has no access. Use the link your group received on Slack.',
      pt: 'Este link não tem acesso. Use o link que o grupo recebeu no Slack.',
      fr: 'Ce lien n’a pas d’accès. Utilisez le lien reçu par le groupe sur Slack.'
    },
    pergunta: { en: 'Question', pt: 'Pergunta', fr: 'Question' },
    apagar: { en: 'Delete', pt: 'Apagar', fr: 'Supprimer' },
    editar: { en: 'Edit', pt: 'Editar', fr: 'Modifier' }
  };

  function lang() {
    var l = document.documentElement.getAttribute('data-lang');
    return l === 'pt' || l === 'fr' ? l : 'en';
  }
  function t(obj) { return obj[lang()] || obj.en; }

  function el(tag, cls, texto) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (texto !== undefined && texto !== null) e.textContent = texto;
    return e;
  }

  function iniciais(nome) {
    var p = nome.trim().split(/\s+/);
    return ((p[0] || '')[0] + ((p.length > 1 ? p[p.length - 1] : '')[0] || '')).toUpperCase();
  }

  // ------------------------------------------------------------ dados
  // Interface comum ao banco real e ao modo de ensaio em memória.
  function dadosSupabase() {
    var cfg = window.SI08ReflexaoConfig;
    var cli = window.supabase.createClient(cfg.url, cfg.chave, { auth: { persistSession: false } });
    function rpc(nome, args) {
      return cli.rpc(nome, args).then(function (r) {
        if (r.error) throw new Error(r.error.message);
        return r.data;
      });
    }
    return {
      quadro: function (g, tk) { return rpc('refl_quadro', { p_sessao: SESSAO, p_grupo: g, p_token: tk }); },
      postar: function (g, tk, autor, perg, texto) {
        return rpc('refl_postar', { p_sessao: SESSAO, p_grupo: g, p_token: tk, p_autor: autor, p_pergunta: perg, p_texto: texto });
      },
      editar: function (g, tk, autor, id, texto) {
        return rpc('refl_editar', { p_sessao: SESSAO, p_grupo: g, p_token: tk, p_autor: autor, p_id: id, p_texto: texto });
      },
      apagar: function (g, tk, autor, id) {
        return rpc('refl_apagar', { p_sessao: SESSAO, p_grupo: g, p_token: tk, p_autor: autor, p_id: id });
      },
      links: function (chave) { return rpc('refl_links', { p_chave: chave, p_sessao: SESSAO }); },
      prazo: function (chave, min) { return rpc('refl_prazo', { p_chave: chave, p_sessao: SESSAO, p_minutos: min }); },
      painel: function (chave) { return rpc('refl_painel', { p_chave: chave, p_sessao: SESSAO }); }
    };
  }

  function dadosDemo() {
    var grupos = window.SI08_GRUPOS || {};
    var postits = [];
    var fim = null;
    var seq = 0;
    function membros(g) {
      return (grupos[g] || []).map(function (n) { return { nome: curto(n), foto: null }; });
    }
    function exigeMembro(g, autor) {
      if (!membros(g).some(function (m) { return m.nome === autor; })) throw new Error('autor não pertence ao grupo');
      if (fim && Date.now() > fim) throw new Error('prazo encerrado');
    }
    return {
      quadro: function (g, tk) {
        if (GRUPOS.indexOf(g) === -1 || !tk) return Promise.reject(new Error('link sem permissão de leitura'));
        return Promise.resolve({
          agora: new Date().toISOString(),
          fim: fim ? new Date(fim).toISOString() : null,
          membros: membros(g),
          postits: postits.filter(function (p) { return p.grupo === g; })
        });
      },
      postar: function (g, tk, autor, perg, texto) {
        try { exigeMembro(g, autor); } catch (e) { return Promise.reject(e); }
        var p = { id: 'demo-' + (++seq), grupo: g, pergunta: perg, autor: autor, texto: texto.trim(), em: new Date().toISOString() };
        postits.push(p);
        return Promise.resolve(p.id);
      },
      editar: function (g, tk, autor, id, texto) {
        var p = postits.filter(function (x) { return x.id === id && x.autor === autor; })[0];
        if (!p) return Promise.reject(new Error('post-it de outro autor'));
        p.texto = texto.trim();
        return Promise.resolve();
      },
      apagar: function (g, tk, autor, id) {
        var n = postits.length;
        postits = postits.filter(function (x) { return !(x.id === id && x.autor === autor); });
        return n === postits.length ? Promise.reject(new Error('post-it de outro autor')) : Promise.resolve();
      },
      links: function () { return Promise.resolve(GRUPOS.map(function (g) { return { grupo: g, token: 'demo' }; })); },
      prazo: function (chave, min) { fim = Date.now() + min * 60000; return Promise.resolve(new Date(fim).toISOString()); },
      painel: function () {
        var ms = [];
        GRUPOS.forEach(function (g) { membros(g).forEach(function (m) { ms.push({ grupo: g, nome: m.nome, foto: null }); }); });
        return Promise.resolve({ agora: new Date().toISOString(), fim: fim ? new Date(fim).toISOString() : null, membros: ms, postits: postits.slice() });
      }
    };
  }

  // Nome exibido: primeiro e último nome do cadastro (o mesmo do seed no banco).
  function curto(nome) {
    var p = nome.trim().split(/\s+/);
    return p.length > 1 ? p[0] + ' ' + p[p.length - 1] : p[0];
  }

  // ------------------------------------------------------------ relógio
  function relogio(alvo) {
    var desvio = 0, fim = null;
    function pintar() {
      if (!fim) { alvo.textContent = ''; alvo.classList.remove('acabou'); return; }
      var rest = Math.max(0, Math.round((fim - (Date.now() + desvio)) / 1000));
      if (rest === 0) { alvo.textContent = t(TEXTOS.encerrado); alvo.classList.add('acabou'); return; }
      alvo.classList.remove('acabou');
      var m = Math.floor(rest / 60), s = rest % 60;
      alvo.textContent = m + ':' + (s < 10 ? '0' : '') + s;
    }
    setInterval(pintar, 500);
    return function (agoraServidor, fimServidor) {
      if (agoraServidor) desvio = new Date(agoraServidor).getTime() - Date.now();
      fim = fimServidor ? new Date(fimServidor).getTime() : null;
      pintar();
    };
  }

  // ------------------------------------------------------------ quadro do grupo
  function quadroGrupo(raiz, dados, grupo, token) {
    var CHAVE_EU = 'refl-eu-' + SESSAO + '-' + grupo;
    var estado = { membros: [], postits: [], pergunta: 1, eu: null, editando: null };
    try { estado.eu = localStorage.getItem(CHAVE_EU); } catch (e) { /* aba privada */ }

    raiz.innerHTML = '';
    var topo = el('header', 'refl-topo');
    var titulo = el('p', 'refl-grupo', grupo);
    var quem = el('button', 'refl-quem');
    quem.type = 'button';
    var tempo = el('p', 'refl-tempo');
    topo.appendChild(titulo); topo.appendChild(quem); topo.appendChild(tempo);
    var abas = el('nav', 'refl-abas');
    abas.setAttribute('aria-label', 'Perguntas');
    var enunciado = el('h1', 'refl-pergunta');
    var grade = el('div', 'refl-grade');
    var erro = el('p', 'refl-erro');
    erro.setAttribute('role', 'alert');
    raiz.appendChild(topo); raiz.appendChild(abas); raiz.appendChild(enunciado);
    raiz.appendChild(erro); raiz.appendChild(grade);
    var acertarRelogio = relogio(tempo);

    function mostrarErro(e) {
      erro.textContent = e ? String(e.message || e) : '';
    }

    function escolherNome() {
      var fundo = el('div', 'refl-modal-fundo');
      var caixa = el('div', 'refl-modal');
      caixa.setAttribute('role', 'dialog');
      caixa.setAttribute('aria-modal', 'true');
      caixa.appendChild(el('h2', null, t(TEXTOS.quemEVoce)));
      caixa.appendChild(el('p', null, t(TEXTOS.escolha)));
      var lista = el('div', 'refl-nomes');
      estado.membros.forEach(function (m) {
        var b = el('button', 'refl-nome');
        b.type = 'button';
        b.appendChild(avatar(m));
        b.appendChild(el('span', null, m.nome));
        b.addEventListener('click', function () {
          estado.eu = m.nome;
          try { localStorage.setItem(CHAVE_EU, m.nome); } catch (e) { /* aba privada */ }
          document.body.removeChild(fundo);
          pintar();
        });
        lista.appendChild(b);
      });
      caixa.appendChild(lista);
      fundo.appendChild(caixa);
      document.body.appendChild(fundo);
    }
    quem.addEventListener('click', escolherNome);

    function avatar(m) {
      var a = el('span', 'refl-avatar');
      if (m.foto) {
        var img = el('img');
        img.src = m.foto;
        img.alt = '';
        img.addEventListener('error', function () { a.textContent = iniciais(m.nome); });
        a.appendChild(img);
      } else {
        a.textContent = iniciais(m.nome);
      }
      return a;
    }

    function postit(p, meu) {
      var nota = el('div', 'refl-postit' + (meu ? ' meu' : ''));
      if (estado.editando === p.id) {
        var ta = el('textarea');
        ta.maxLength = 280;
        ta.value = p.texto;
        nota.appendChild(ta);
        var ok = el('button', 'refl-mini', t(TEXTOS.colar));
        ok.type = 'button';
        ok.addEventListener('click', function () {
          dados.editar(grupo, token, estado.eu, p.id, ta.value).then(function () {
            estado.editando = null; mostrarErro(null); atualizar();
          }).catch(mostrarErro);
        });
        nota.appendChild(ok);
        setTimeout(function () { ta.focus(); }, 0);
        return nota;
      }
      nota.appendChild(el('p', 'refl-texto', p.texto));
      if (meu) {
        var acoes = el('div', 'refl-acoes');
        var ed = el('button', 'refl-mini', t(TEXTOS.editar));
        ed.type = 'button';
        ed.addEventListener('click', function () { estado.editando = p.id; pintar(); });
        var ap = el('button', 'refl-mini', t(TEXTOS.apagar));
        ap.type = 'button';
        ap.addEventListener('click', function () {
          dados.apagar(grupo, token, estado.eu, p.id).then(function () { mostrarErro(null); atualizar(); }).catch(mostrarErro);
        });
        acoes.appendChild(ed); acoes.appendChild(ap);
        nota.appendChild(acoes);
      }
      return nota;
    }

    function bloco(m) {
      var meu = m.nome === estado.eu;
      var b = el('section', 'refl-bloco' + (meu ? ' meu' : ''));
      var cab = el('div', 'refl-bloco-cab');
      cab.appendChild(avatar(m));
      cab.appendChild(el('p', 'refl-bloco-nome', m.nome));
      b.appendChild(cab);
      var notas = estado.postits.filter(function (p) { return p.autor === m.nome && p.pergunta === estado.pergunta; });
      var pilha = el('div', 'refl-pilha');
      if (!notas.length && !meu) pilha.appendChild(el('p', 'refl-vazio', t(TEXTOS.vazio)));
      notas.forEach(function (p) { pilha.appendChild(postit(p, meu)); });
      b.appendChild(pilha);
      if (meu) {
        var form = el('form', 'refl-novo');
        var ta = el('textarea');
        ta.maxLength = 280;
        ta.placeholder = t(TEXTOS.escrever);
        ta.rows = 3;
        ta.setAttribute('aria-label', t(TEXTOS.escrever));
        var bt = el('button', 'refl-colar', t(TEXTOS.colar));
        bt.type = 'submit';
        form.appendChild(ta); form.appendChild(bt);
        ta.addEventListener('keydown', function (ev) {
          if (ev.key === 'Enter' && (ev.metaKey || ev.ctrlKey)) { ev.preventDefault(); form.requestSubmit(); }
        });
        form.addEventListener('submit', function (ev) {
          ev.preventDefault();
          var texto = ta.value.trim();
          if (!texto) return;
          bt.disabled = true;
          dados.postar(grupo, token, estado.eu, estado.pergunta, texto).then(function () {
            ta.value = ''; mostrarErro(null); return atualizar();
          }).catch(mostrarErro).then(function () { bt.disabled = false; ta.focus(); });
        });
        b.appendChild(form);
      }
      return b;
    }

    function pintar() {
      quem.textContent = estado.eu ? estado.eu + ' · ' + t(TEXTOS.trocar) : t(TEXTOS.quemEVoce);
      abas.innerHTML = '';
      PERGUNTAS.forEach(function (q, i) {
        var n = i + 1;
        var qtd = estado.postits.filter(function (p) { return p.pergunta === n; }).length;
        var a = el('button', 'refl-aba' + (n === estado.pergunta ? ' ativa' : ''));
        a.type = 'button';
        a.setAttribute('aria-pressed', String(n === estado.pergunta));
        a.appendChild(el('span', 'refl-aba-num', String(n)));
        a.appendChild(el('span', 'refl-aba-qtd', String(qtd)));
        a.addEventListener('click', function () { estado.pergunta = n; estado.editando = null; pintar(); });
        abas.appendChild(a);
      });
      enunciado.textContent = t(TEXTOS.pergunta) + ' ' + estado.pergunta + '. ' + t(PERGUNTAS[estado.pergunta - 1]);
      // Preserva o rascunho do próprio bloco entre as atualizações automáticas.
      var rascunho = grade.querySelector('.refl-bloco.meu .refl-novo textarea');
      var texto = rascunho ? rascunho.value : '';
      var focado = rascunho && document.activeElement === rascunho;
      if (estado.editando && grade.querySelector('.refl-postit textarea')) return;
      grade.innerHTML = '';
      var ordem = estado.membros.slice().sort(function (a, b) {
        return (b.nome === estado.eu) - (a.nome === estado.eu);
      });
      ordem.forEach(function (m) { grade.appendChild(bloco(m)); });
      var novo = grade.querySelector('.refl-bloco.meu .refl-novo textarea');
      if (novo) { novo.value = texto; if (focado) novo.focus(); }
    }

    function atualizar() {
      return dados.quadro(grupo, token).then(function (q) {
        estado.membros = q.membros || [];
        estado.postits = q.postits || [];
        acertarRelogio(q.agora, q.fim);
        mostrarErro(null);
        if (estado.eu && !estado.membros.some(function (m) { return m.nome === estado.eu; })) estado.eu = null;
        pintar();
        if (!estado.eu && !document.querySelector('.refl-modal')) escolherNome();
      });
    }

    document.addEventListener('si08-idioma', pintar);
    atualizar().catch(function (e) {
      raiz.innerHTML = '';
      raiz.appendChild(el('p', 'refl-erro grande', t(TEXTOS.semLink)));
      console.error('[reflexao]', e);
    }).then(function () {
      setInterval(function () { atualizar().catch(mostrarErro); }, INTERVALO_MS);
    });
    return { estado: estado, atualizar: atualizar };
  }

  // ------------------------------------------------------------ painel do professor
  function painelProfessor(raiz, dados) {
    var chave = '';
    try {
      var p = new URLSearchParams(window.location.search).get('quiz-chave');
      if (p) localStorage.setItem(CHAVE_PROFESSOR, p);
      chave = localStorage.getItem(CHAVE_PROFESSOR) || '';
    } catch (e) { /* aba privada */ }
    var demo = /[?&]demo=1/.test(window.location.search);
    if (demo) chave = chave || 'demo';

    raiz.innerHTML = '';
    var topo = el('header', 'refl-topo');
    topo.appendChild(el('p', 'refl-grupo', 'Painel'));
    var tempo = el('p', 'refl-tempo');
    var controles = el('div', 'refl-controles');
    [20, 5, 0].forEach(function (min) {
      var b = el('button', 'refl-mini', min ? '+' + min + ' min' : 'Encerrar');
      b.type = 'button';
      b.addEventListener('click', function () { dados.prazo(chave, min).then(atualizar).catch(mostrarErro); });
      controles.appendChild(b);
    });
    topo.appendChild(controles);
    topo.appendChild(tempo);
    var erro = el('p', 'refl-erro');
    var links = el('div', 'refl-links');
    var filtros = el('div', 'refl-filtros');
    var selGrupo = el('select');
    GRUPOS.forEach(function (g) { var o = el('option', null, g); o.value = g; selGrupo.appendChild(o); });
    var selPerg = el('select');
    PERGUNTAS.forEach(function (q, i) { var o = el('option', null, 'Pergunta ' + (i + 1)); o.value = String(i + 1); selPerg.appendChild(o); });
    filtros.appendChild(selGrupo); filtros.appendChild(selPerg);
    var participacao = el('table', 'refl-participacao');
    var leitura = el('div', 'refl-leitura');
    raiz.appendChild(topo); raiz.appendChild(erro); raiz.appendChild(links);
    raiz.appendChild(participacao); raiz.appendChild(filtros); raiz.appendChild(leitura);
    var acertarRelogio = relogio(tempo);
    var ultimo = null;

    function mostrarErro(e) { erro.textContent = e ? String(e.message || e) : ''; }

    if (!chave) { mostrarErro('Falta a chave do professor neste navegador (?quiz-chave=).'); return; }

    dados.links(chave).then(function (ls) {
      ls.forEach(function (l) {
        var u = new URL(window.location.href);
        var url = u.href.split('?')[0] + '?g=' + l.grupo + '&t=' + l.token + (demo ? '&demo=1' : '');
        var a = el('a', 'refl-link', l.grupo);
        a.href = url;
        a.target = '_blank';
        a.rel = 'noopener';
        a.title = 'Abrir o quadro do ' + l.grupo;
        var copiar = el('button', 'refl-mini', 'Copiar link');
        copiar.type = 'button';
        copiar.addEventListener('click', function () {
          if (navigator.clipboard) navigator.clipboard.writeText(url).then(function () { copiar.textContent = 'Copiado'; });
        });
        var linha = el('div', 'refl-link-linha');
        linha.appendChild(a); linha.appendChild(copiar);
        links.appendChild(linha);
      });
    }).catch(mostrarErro);

    function pintar() {
      if (!ultimo) return;
      // Participação: post-its por integrante e por pergunta; zero em destaque.
      participacao.innerHTML = '';
      var cab = el('tr');
      ['Grupo', 'Integrante'].concat(PERGUNTAS.map(function (q, i) { return 'P' + (i + 1); })).forEach(function (h) {
        cab.appendChild(el('th', null, h));
      });
      var thead = el('thead'); thead.appendChild(cab); participacao.appendChild(thead);
      var tbody = el('tbody');
      ultimo.membros.forEach(function (m) {
        var tr = el('tr');
        tr.appendChild(el('td', null, m.grupo));
        tr.appendChild(el('td', null, m.nome));
        PERGUNTAS.forEach(function (q, i) {
          var n = ultimo.postits.filter(function (p) { return p.grupo === m.grupo && p.autor === m.nome && p.pergunta === i + 1; }).length;
          tr.appendChild(el('td', n ? 'n' : 'n zero', String(n)));
        });
        tbody.appendChild(tr);
      });
      participacao.appendChild(tbody);

      leitura.innerHTML = '';
      var g = selGrupo.value, q = Number(selPerg.value);
      leitura.appendChild(el('h2', 'refl-pergunta', 'Pergunta ' + q + '. ' + PERGUNTAS[q - 1].pt));
      var grade = el('div', 'refl-grade');
      ultimo.membros.filter(function (m) { return m.grupo === g; }).forEach(function (m) {
        var b = el('section', 'refl-bloco');
        var c = el('div', 'refl-bloco-cab');
        var av = el('span', 'refl-avatar', iniciais(m.nome));
        c.appendChild(av); c.appendChild(el('p', 'refl-bloco-nome', m.nome));
        b.appendChild(c);
        var pilha = el('div', 'refl-pilha');
        var ns = ultimo.postits.filter(function (p) { return p.grupo === g && p.autor === m.nome && p.pergunta === q; });
        if (!ns.length) pilha.appendChild(el('p', 'refl-vazio', 'Nenhum post-it'));
        ns.forEach(function (p) { var d = el('div', 'refl-postit'); d.appendChild(el('p', 'refl-texto', p.texto)); pilha.appendChild(d); });
        b.appendChild(pilha);
        grade.appendChild(b);
      });
      leitura.appendChild(grade);
    }
    selGrupo.addEventListener('change', pintar);
    selPerg.addEventListener('change', pintar);

    function atualizar() {
      return dados.painel(chave).then(function (d) { ultimo = d; acertarRelogio(d.agora, d.fim); mostrarErro(null); pintar(); });
    }
    atualizar().catch(mostrarErro);
    setInterval(function () { atualizar().catch(mostrarErro); }, INTERVALO_MS * 2);
  }

  // ------------------------------------------------------------ início
  function iniciar() {
    var raiz = document.getElementById('reflexao');
    if (!raiz) return;
    var q = new URLSearchParams(window.location.search);
    var demo = q.get('demo') === '1';
    var dados = demo ? dadosDemo() : dadosSupabase();
    if (q.get('painel') === '1') { painelProfessor(raiz, dados); return; }
    var grupo = (q.get('g') || '').toUpperCase();
    var token = q.get('t') || (demo ? 'demo' : '');
    window.SI08Reflexao = quadroGrupo(raiz, dados, grupo, token);
  }

  window.SI08ReflexaoInterno = { PERGUNTAS: PERGUNTAS, SESSAO: SESSAO, curto: curto, iniciais: iniciais };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
