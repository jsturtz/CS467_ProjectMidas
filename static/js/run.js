// only when document fully loaded
$(document).ready( () => {
  $(".dropdown-item.run-algorithm").on("click", choose_run_algorithm);
  $("#run-model-btn").on("click", run_model);
})

function choose_run_algorithm(e)
{
  e.preventDefault();
  $("#run-model").find("p.result").first().text(e.currentTarget.textContent);
  $(".dropdown-item.run-algorithm").attr("selected", false);
  $(this).attr("selected", true);
}

function run_model(e)
{
  if ($("#run-model").find(".upload-result").attr("success") == "true")
  {
    var id = $(".dropdown-item.run-algorithm[selected]").attr("name")
    $("#run-model").find("p.result").eq(1).text("Executing..."); // FIXME: Make this more dynamic, 
    $.ajax({
      type: 'GET', 
      url: "/?run-model=" + id, 
      success: res => {
        $("#execution-results-display").html(res);
        $("#results-jumbotron").show(res);
      },
      error: res => {
        alert(res.message)
      }
    });
  }
  else 
  {
    alert("You must first upload a file before executing a model")
  }
}

