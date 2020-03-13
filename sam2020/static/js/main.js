function openNav() {
  document.getElementById("sideNav").style.width = "14%";
  document.getElementById("main").style.marginLeft = "14%";
  document.getElementById("open").style.display = "none";
  document.getElementById("sideNavMenu").style.display = "inline";
}

function closeNav() {
  document.getElementById("sideNav").style.width = "35px";
  document.getElementById("main").style.marginLeft= "35px";
  document.getElementById("open").style.display = "block";
  document.getElementById("sideNavMenu").style.display = "none";
}


function user_open() {
  document.getElementById("userSide").style.display = "block";
  document.getElementById("userOverlay").style.display = "block";
}

function user_close() {
  document.getElementById("userSide").style.display = "none";
  document.getElementById("userOverlay").style.display = "none";
}