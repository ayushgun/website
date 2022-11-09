function switchTheme() {
	const body = document.body;
	body.classList.toggle("light-mode");
}

function changeIcon(iconID) {
	if (document.getElementById(iconID).className == "fa-regular fa-lightbulb") {
		document.getElementById(iconID).className = "fa-solid fa-lightbulb";
	} else {
		document.getElementById(iconID).className = "fa-regular fa-lightbulb";
	}
}
