function switchTheme() {
	// Load DOM data
	const body = document.body;
	const icon = document.getElementById("toggle");
	var isLightEnabled = body.classList.toggle("light-mode");

	// Store theme data and switch icon
	if (isLightEnabled) {
		localStorage.setItem("selectedTheme", "light");
		icon.className = "fa-solid fa-moon";
	} else {
		localStorage.setItem("selectedTheme", "dark");
		icon.className = "fa-solid fa-sun";
	}
}

function loadTheme() {
	// Access stored theme
	const theme = localStorage.getItem("selectedTheme");

	// Show theme on page load
	if (theme == "light") {
		switchTheme();
	}
}
