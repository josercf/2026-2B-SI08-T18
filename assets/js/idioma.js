/* Seletor de idioma dos decks de orientacao (ADR-001).
   Ordem de precedencia: ?lang= na URL, escolha salva no navegador, ingles.
   Carregado no <head> para o idioma valer antes da primeira pintura.
   Atalho de teclado: L alterna EN -> PT -> FR. */
(function () {
  var IDIOMAS = ["en", "pt", "fr"];
  var ROTULOS = { en: "EN", pt: "PT", fr: "FR" };
  var HTML_LANG = { en: "en", pt: "pt-BR", fr: "fr" };
  var CHAVE = "si08t18-lang";

  function lerSalvo() {
    try { return localStorage.getItem(CHAVE); } catch (e) { return null; }
  }

  function salvar(lang) {
    try { localStorage.setItem(CHAVE, lang); } catch (e) { /* modo privado */ }
  }

  function inicial() {
    var url = new URLSearchParams(window.location.search).get("lang");
    if (IDIOMAS.indexOf(url) !== -1) return url;
    var salvo = lerSalvo();
    if (IDIOMAS.indexOf(salvo) !== -1) return salvo;
    return "en";
  }

  function aplicar(lang) {
    var html = document.documentElement;
    html.setAttribute("data-lang", lang);
    html.setAttribute("lang", HTML_LANG[lang]);
    var botoes = document.querySelectorAll(".lang-switch button");
    for (var i = 0; i < botoes.length; i++) {
      botoes[i].setAttribute("aria-pressed", String(botoes[i].dataset.lang === lang));
    }
    if (window.Reveal && typeof window.Reveal.layout === "function") {
      try { window.Reveal.layout(); } catch (e) { /* Reveal ainda nao iniciou */ }
    }
  }

  function trocar(lang) {
    salvar(lang);
    aplicar(lang);
  }

  aplicar(inicial());

  document.addEventListener("DOMContentLoaded", function () {
    var barra = document.createElement("div");
    barra.className = "lang-switch";
    barra.setAttribute("role", "group");
    barra.setAttribute("aria-label", "Language");
    IDIOMAS.forEach(function (lang) {
      var b = document.createElement("button");
      b.type = "button";
      b.dataset.lang = lang;
      b.textContent = ROTULOS[lang];
      b.addEventListener("click", function () { trocar(lang); });
      barra.appendChild(b);
    });
    document.body.appendChild(barra);
    aplicar(document.documentElement.getAttribute("data-lang"));

    document.addEventListener("keydown", function (ev) {
      if (ev.key !== "l" && ev.key !== "L") return;
      if (ev.ctrlKey || ev.metaKey || ev.altKey) return;
      var atual = document.documentElement.getAttribute("data-lang");
      trocar(IDIOMAS[(IDIOMAS.indexOf(atual) + 1) % IDIOMAS.length]);
    });
  });

  window.SI08Idioma = { trocar: trocar, idiomas: IDIOMAS.slice() };
})();
