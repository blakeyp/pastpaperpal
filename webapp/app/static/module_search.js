console.log(modules);

$(document).click(function(e) {
	e.stopPropagation();
	var container = $("#search_area");
	if (container.has(e.target).length === 0) {
		$('#search_dropdown').removeClass('open');
		$('#module_search').val('');
	}
});

// regex to validate module code input
var valid_code = new RegExp("^[A-Z]{1,2}[0-9]{0,3}$");

// validate input on key up of module code search box
// call to update results
$('#module_search').keyup(function() {
	console.log('yay');
	$('#search_dropdown').addClass('open');
	$("#dropdown_results").html("");   // clear current results
	var input = this.value.toUpperCase();
	if (input.length == 0)  {
		$('#search_dropdown').removeClass('open');
		return;
	}
	if (!valid_code.test(input)) {
		$("#dropdown_results").html("<li><a>Not a valid module code!</a></li>"); return; }
	var found_results = updateResults(input);
	if (input.length == 5 && !found_results)
		$("#dropdown_results").html("<li><a>No results found. <a style='color:#337ab7;' href='/upload'>Upload new paper?</a></a></li>");
	else if (!found_results)
		$("#dropdown_results").html("<li><a>No results found.</a></li>");
});

// updates module search results using list of module codes
function updateResults(input) {
	var found_results = false;
	for (i=0; i<modules.length; i++) {
		if (modules[i].startsWith(input)) {
			// concatenate to existing results
			var paper = (counts[i]==1 ? " paper" : " papers")
			$("#dropdown_results").html($("#dropdown_results").html() + 
			"<li><a href='/"+modules[i].toLowerCase()+"'><span style='color:#6b6b6b;'>"+input+"</span>"+modules[i].split(input)[1]+" &bull; \
			<span style='font-size:16px'> "+counts[i]+paper+"</span></a></li>");
			found_results = true;
		}
	}
	return found_results;
}