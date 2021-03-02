function indexInParent(node) {
  var children = node.parentNode.childNodes;
  var num = 0;
  for (var i=0; i<children.length; i++) {
    if (children[i]==node) return num+1;
    if (children[i].nodeType==1) num++;
  }
  return -1;
}


function copy(event) {
  var target = event.target || event.srcElement;
  var copyText = target.innerText || target.textContent;
  navigator.clipboard.writeText(copyText)

  // Seleccionar la celda -> No me interesa por ahora.
  // var range = document.createRange();
  // range.selectNode(target);
  // window.getSelection().removeAllRanges();
  // window.getSelection().addRange(range);
}

function copy2(event) {
  var target = this.parentNode.parentNode.querySelector("span")
  var copyText = target.dataset.direccion;
  console.log(copyText)
  navigator.clipboard.writeText(copyText)

  // Seleccionar la celda -> No me interesa por ahora.
  // var range = document.createRange();
  // range.selectNode(target);
  // window.getSelection().removeAllRanges();
  // window.getSelection().addRange(range);
}

var columnas = document.getElementsByClassName("copiable")

for (var i=0; i < columnas.length; i++) {
  var columna = columnas[i];
  var index = indexInParent(columna);
  document.querySelectorAll("td:nth-child("+index+")")
  .forEach(elem => elem.addEventListener("click", copy));
  document.querySelectorAll("th:nth-child("+index+")")
  .forEach(elem => elem.addEventListener("click", copy));
}

var entregas = document.getElementsByClassName("fa-copy");
Array.from(entregas).forEach(elem => elem.addEventListener("click", copy2));
