/* Slide de grupos. Os nomes vem de dados/grupos.js (gerado por
   tools/extrair_lbl.py). Se o arquivo faltar, o slide e o item da agenda sao
   removidos antes de o Reveal iniciar; a numeracao dos demais slides nao muda
   porque o slide de grupos e o ultimo antes do encerramento. Roda sincrono, no fim do body, antes do Reveal.initialize. */
(function () {
  var grupos = window.SI08_GRUPOS;
  var marcados = document.querySelectorAll('[data-local="grupos"]');

  if (!grupos || !Object.keys(grupos).length) {
    for (var i = 0; i < marcados.length; i++) marcados[i].remove();
    return;
  }

  var grade = document.querySelector('section[data-local="grupos"] .grupos-grid');
  Object.keys(grupos).sort().forEach(function (nome) {
    var col = document.createElement("div");
    col.className = "grupo-col";
    var h = document.createElement("h3");
    h.textContent = nome;
    var qtd = document.createElement("span");
    qtd.className = "grupo-qtd";
    qtd.textContent = grupos[nome].length;
    h.appendChild(qtd);
    var ul = document.createElement("ul");
    grupos[nome].forEach(function (aluno) {
      var li = document.createElement("li");
      li.textContent = aluno;
      ul.appendChild(li);
    });
    col.appendChild(h);
    col.appendChild(ul);
    grade.appendChild(col);
  });
})();
