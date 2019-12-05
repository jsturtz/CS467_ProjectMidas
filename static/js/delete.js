// only when document fully loaded
$(document).ready( () => {
  $(".dropdown-item.delete-algorithm").on("click", choose_delete_algorithm);
  $("#delete-model-btn").on("click", delete_model);
})

function choose_delete_algorithm(e)
{
  e.preventDefault();
  $("#delete-model").find("p.result").first().text(e.currentTarget.textContent);
  $(".dropdown-item.delete-algorithm").attr("selected", false);
  $(this).attr("selected", true);
}

function delete_model(e)
{
  $.ajax({
    type: 'GET', 
    url: "/?delete-model=" + id, 
    success: res => {
      $("#delete-model").find("p.result").eq(1).text("Executing..."); // FIXME: Make this more dynamic, 
      alert("Successfully deleted model! Reloading page...");
      document.location.reload();
    },
    error: res => {
      alert(res.message)
    }
  });
}

