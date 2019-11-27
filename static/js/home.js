// only when document fully loaded
$(document).ready( () => {
  $(".dropdown-item.training-type").click(toggleTrainOrRun);
})

// controls which page is displayed when user selects dropdown
function toggleTrainOrRun(e) 
{
  $("#screen-title").text(e.currentTarget.textContent);
  $(".container.training-type").hide();
  $("#" + e.currentTarget.name).show();
}
