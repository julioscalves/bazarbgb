/*
 *   Thanks to rmed
 *   https://www.rmedgar.com/blog/dynamic-fields-flask-wtf/
 */

const ID_RE = /(-)_(-)/;

/**
 * Replace the template index of an element (-_-) with the
 * given index.
 */
function replaceTemplateIndex(value, index) {
  return value.replace(ID_RE, "$1" + index + "$2");
}

/**
 * Adjust the indices of form fields when removing items.
 */
function adjustIndices(removedIndex) {
  var $forms = $(".subform");

  $forms.each(function (i) {
    var $form = $(this);
    var index = parseInt($form.data("index"));
    var newIndex = index - 1;

    if (index < removedIndex) {
      // Skip
      return true;
    }

    // This will replace the original index with the new one
    // only if it is found in the format -num-, preventing
    // accidental replacing of fields that may have numbers
    // intheir names.
    var regex = new RegExp("(-)" + index + "(-)");
    var repVal = "$1" + newIndex + "$2";

    // Change ID in form itself
    $form.attr("id", $form.attr("id").replace(index, newIndex));
    $form.data("index", newIndex);

    // Change IDs in form fields
    $form.find("label, input, select, textarea").each(function (j) {
      var $item = $(this);

      if ($item.is("label")) {
        // Update labels
        $item.attr("for", $item.attr("for").replace(regex, repVal));
        return;
      }

      // Update other fields
      $item.attr("id", $item.attr("id").replace(regex, repVal));
      $item.attr("name", $item.attr("name").replace(regex, repVal));
    });
  });
}

/**
 * Remove a form.
 */
function removeForm() {
  var confirmation = confirm("Quer remover este item?");

  if (confirmation == true) {
    var $removedForm = $(this).closest(".subform");
    var removedIndex = parseInt($removedForm.data("index"));

    $removedForm.remove();

    // Update indices
    adjustIndices(removedIndex);
  }
}

/**
 * Add a new form.
 */
function addBoardGameForm() {
  var $templateForm = $("#boardgame-_-form");

  if ($templateForm.length === 0) {
    console.log("[ERROR] Cannot find template");
    return;
  }

  // Get Last index
  var $lastForm = $(".boardgame_subform").last();

  var newIndex = 0;

  if ($lastForm.length > 0) {
    newIndex = parseInt($lastForm.data("index")) + 1;
  }

  // Maximum of 20 subforms
  if (newIndex >= 50) {
    console.log("[WARNING] Reached maximum number of elements");
    return;
  }

  // Add elements
  var $newForm = $templateForm.clone();

  $newForm.attr("id", replaceTemplateIndex($newForm.attr("id"), newIndex));
  $newForm.data("index", newIndex);

  $newForm.find("label, input, select, textarea").each(function (idx) {
    var $item = $(this);

    if ($item.is("label")) {
      // Update labels
      $item.attr("for", replaceTemplateIndex($item.attr("for"), newIndex));
      return;
    }

    // Update other fields
    $item.attr("id", replaceTemplateIndex($item.attr("id"), newIndex));
    $item.attr("name", replaceTemplateIndex($item.attr("name"), newIndex));
  });

  // Append
  $("#boardgame-subforms-container").append($newForm);
  $newForm.addClass("boardgame_subform");
  $newForm.removeClass("is-hidden");

  $newForm.find(".remove").click(removeForm);
}

function addAuctionForm() {
  var $templateForm = $("#auction-_-form");

  if ($templateForm.length === 0) {
    console.log("[ERROR] Cannot find template");
    return;
  }

  // Get Last index
  var $lastForm = $(".auction_subform").last();

  var newIndex = 0;

  if ($lastForm.length > 0) {
    newIndex = parseInt($lastForm.data("index")) + 1;
  }

  // Maximum of 50 subforms
  if (newIndex >= 50) {
    console.log("[WARNING] Reached maximum number of elements");
    return;
  }

  // Add elements
  var $newForm = $templateForm.clone();

  $newForm.attr("id", replaceTemplateIndex($newForm.attr("id"), newIndex));
  $newForm.data("index", newIndex);

  $newForm.find("label, input, select, textarea").each(function (idx) {
    var $item = $(this);

    if ($item.is("label")) {
      // Update labels
      $item.attr("for", replaceTemplateIndex($item.attr("for"), newIndex));
      return;
    }

    // Update other fields
    $item.attr("id", replaceTemplateIndex($item.attr("id"), newIndex));
    $item.attr("name", replaceTemplateIndex($item.attr("name"), newIndex));
  });

  // Append
  $("#auction-subforms-container").append($newForm);
  $newForm.addClass("auction_subform");
  $newForm.removeClass("is-hidden");

  $newForm.find(".remove").click(removeForm);
}

function toTitleCase(string) {
  var titleCase = string.toLowerCase().split(" ");

  for (var i = 0; i < titleCase.length; i++) {
    titleCase[i] = titleCase[i].charAt(0).toUpperCase() + titleCase[i].substring(1);
  }

  return titleCase.join(" ");
}

function validate_boardgame(
  autocomplete_list,
  user_input,
  boardgame_input_element
) {
  if (autocomplete_list.includes(user_input) && autocomplete_list.length > 0) {
    boardgame_input_element.removeClass("border border-danger");
    $("#form-submit").removeAttr("disabled");
  } else {
    boardgame_input_element.addClass("border border-danger");
    $("#form-submit").attr("disabled", true);
  }
}

$(document).ready(function () {
  $("#add_boardgame").click(addBoardGameForm);
  $("#add_auction").click(addAuctionForm);
  $(".remove").click(removeForm);
  $("body").css("display", "none");
  $("body").fadeIn(400);

  $("body").on("keyup change", ".detail-area", function () {
    const DESCRIPTION_MAX = 80;
    $(this)
      .parent()
      .parent()
      .find("span")
      .text(DESCRIPTION_MAX - $(this).val().length + " caracteres restantes.");
  });

  $("body").on("keyup change", "#general_details", function () {
    const DESCRIPTION_MAX = 600;
    $("#general_details_chars").text(
      DESCRIPTION_MAX - $(this).val().length + " caracteres restantes."
    );
  });

  $(document).on("change click", ".offer-type", function () {
    var selectValue = $(this).val();
    var priceArea = $(this)
      .parent("div")
      .parent("div")
      .find(".price-input")
      .parent();
    var priceInput = $(this).parent("div").parent("div").find(".price-input");
    var placeholder =
    "(Opcional) Aceito Shopee, MercadoLivre e retirada em mãos.";
    var placeholder_auction =
    "(Obrigatório) Link e demais informações sobre o leilão. Informações sobre os demais itens.";
    var general_details = $("#general_details");

    if (selectValue == "Apenas Venda" || selectValue == "Venda ou Troca") {
      priceInput.attr("required", true);
      priceArea.fadeIn(200);
    } else {
      priceInput.removeAttr("required");
      priceArea.fadeOut(200);
    }

    if (selectValue == "Leilão Externo") {
        general_details.attr("required", true);
        general_details.attr("placeholder", placeholder_auction);
    } else {
        general_details.removeAttr("required");
        general_details.attr("placeholder", placeholder);
    }
  });

  $(document).on("keypress", ".bg-autocomplete", function () {
    var boardgame_input_text = $(this).val();
    var boardgame_input_element = $(this);
    var bglist;

    $(".bg-autocomplete").autocomplete({
      delay: 300,
      source: function (request, response) {
        $.getJSON(
          "/bgsearch",
          {
            bgquery: request.term,
          },
          function (data) {
            bglist = data.bglist;
            validate_boardgame(
              bglist,
              boardgame_input_text,
              boardgame_input_element
            );
            response(bglist);
          }
        );
      },
      select: function (event, ui) {
        boardgame_input_text = ui.item.value;
        validate_boardgame(
          bglist,
          boardgame_input_text,
          boardgame_input_element
        );
      },
      minLength: 2,
    });
  });

  const url =
    "https://gist.githubusercontent.com/letanure/3012978/raw/2e43be5f86eef95b915c1c804ccc86dc9790a50a/estados-cidades.json";
  let cities = [];

  fetch(url)
    .then(function (response) {
      return response.json();
    })
    .then(function (data) {
      data.estados.forEach((element) => cities.push(element.cidades));
      cities = [...new Set(cities.flat())];
      cities = cities.map(function(city) {
        return toTitleCase(city);
      })
    });

  $(document).on("keypress", ".city", function () {
    var city = $(this).val()
    $(".city").autocomplete({
      delay: 300,
      source: function (request, response) {
        typing = toTitleCase(city);
        let results = cities.filter((word) => word.startsWith(typing));
        response(results.slice(0, 10));
      },
      minLength: 2,
    });
  });
});
