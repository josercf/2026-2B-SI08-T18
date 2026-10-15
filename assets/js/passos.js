/* Passos das animacoes do deck de planning (ADR-004).

   Cada slide animado por passos tem fragments do Reveal (a legenda numerada)
   e um SVG que reage a classes p1, p2, ... na <section>. Este script conta os
   fragments visiveis e escreve essas classes de forma cumulativa: no passo 3
   a section tem p1 p2 p3. O CSS em planning-anim.css posiciona o SVG por
   essas classes, e as transicoes fazem o movimento.

   Estado final: com prefers-reduced-motion ou no PDF (?print-pdf), toda
   section recebe todas as classes de passo e html recebe anim-final, que
   desliga keyframes e transicoes. O slide mostra direto o resultado. */
(function () {
  var MAX_PASSOS = 12;

  function modoFinal() {
    var reduzido = window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    return reduzido || /print-pdf/.test(window.location.search);
  }

  function aplicar(sec, n) {
    if (!sec) return;
    for (var k = 1; k <= MAX_PASSOS; k++) {
      sec.classList.toggle("p" + k, k <= n);
    }
    sec.setAttribute("data-passo", String(n));
  }

  function contar(sec) {
    if (!sec) return;
    aplicar(sec, sec.querySelectorAll(".fragment.visible").length);
  }

  function finalizarTudo() {
    document.documentElement.classList.add("anim-final");
    var secoes = document.querySelectorAll(".reveal .slides > section");
    for (var i = 0; i < secoes.length; i++) {
      aplicar(secoes[i], secoes[i].querySelectorAll(".fragment").length);
    }
  }

  window.SI08Passos = {
    iniciar: function (reveal) {
      if (modoFinal()) {
        finalizarTudo();
        return;
      }
      var secao = function (ev) {
        return ev.fragment ? ev.fragment.closest("section") : null;
      };
      reveal.on("fragmentshown", function (ev) { contar(secao(ev)); });
      reveal.on("fragmenthidden", function (ev) { contar(secao(ev)); });
      reveal.on("slidechanged", function (ev) { contar(ev.currentSlide); });
      reveal.on("ready", function (ev) { contar(ev.currentSlide); });
    },
    finalizarTudo: finalizarTudo
  };
})();
