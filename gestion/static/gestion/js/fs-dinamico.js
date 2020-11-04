// funcion obtener numero de formularios
// funcion actualizar numero de formularios
// funcion añadir
// funcion eliminar

function numeroForms() {
  var nFs = $('#id_form-TOTAL_FORMS').val();
  console.log(nFs);
}

function reemplazar(form, total) {

}

function actualizar(total) {

}

function añadir() {
  var total = numeroForms();
  var pre_form = $('empty-form').clone().attrs('id', null);
  // Reemplazar(form, total)
  var post_form = reemplazar(pre_form, total);
  $('#dinamico').append(post_form);
  actualizar(total);
  $('.django-select2').djangoSelect2();
}

function eliminar() {

}

$(document).ready(function () {
  $('#añadir-form').click(añadir());
  $('#eliminar-form').click(eliminar());
});



/*
Funciones:
  - Obtener num de formularios (A) -> a
  - Modificar prefijo formulario. (B(a))
  - Actualizar total-forms (C(a))
  - Añadir formulario
  - Eliminar formulario

Pasos:
   1 - Añadir evento onclick a id "añadir".
        - Obtener numero de formularios (A)
        - Obtener copia de #empty-form
        - Modificar prefijo formulario según numero total de formularios (a) y
        eliminar etiqueta #empty-form
        - Añadir formulario al final
        - Inicializar django-select2
        - Actualizar total-forms (a + 1)

   2 - Añadir evento onclick a id "eliminar".
        - Seleccionar formulario padre del boton que se ha clicado.
        - Eliminar formulario.
        - ¿Reasignar ids a cada formulario?
        - Actualizar total-forms.

*/
