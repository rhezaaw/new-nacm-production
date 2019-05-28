// Hide submenus
$('#body-row .collapse').collapse('hide');

// Collapse/Expand icon
$('#collapse-icon').addClass('fa-angle-double-left');

// Collapse click
$('[data-toggle=sidebar-colapse]').click(function() {
    SidebarCollapse();
});

function SidebarCollapse () {
    $('.menu-collapsed').toggleClass('d-none');
    $('.sidebar-submenu').toggleClass('d-none');
    $('.submenu-icon').toggleClass('d-none');
    $('#sidebar-container').toggleClass('sidebar-expanded sidebar-collapsed');

    // Treating d-flex/d-none on separators with title
    var SeparatorTitle = $('.sidebar-separator-title');
    if ( SeparatorTitle.hasClass('d-flex') ) {
        SeparatorTitle.removeClass('d-flex');
    } else {
        SeparatorTitle.addClass('d-flex');
    }

    // Collapse/Expand icon
    $('#collapse-icon').toggleClass('fa-angle-double-left fa-angle-double-right');
}

$("#submenu2").hover(function() {
    $("#sub-dropdown-content").toggleClass("show","hide");
});

// function subDropdown(){
//     document.getElementById("sub-dropdown-content").classList.toggle("show-submenu");
// }

// function loadPage(){
//     var x = document.getElementById("menu-name");
//     if (x.value="Config"){
//       document.getElementById("loadPage").innerHTML = "{% include 'konfig_form.html' %}";
//       document.getElementById("title-menu").innerHTML = "Menu Konfigurasi";
//     }
//     else if (x.value="Backup") {
//       document.getElementById("loadPage").innerHTML = "{% include 'backup_form.html' %}";
//       document.getElementById("title-menu").innerHTML = "Menu Backup";
//     }
//     else if (x.value="Import") {
//       document.getElementById("loadPage").innerHTML = "{% include 'restore_form.html' %}";
//       document.getElementById("title-menu").innerHTML = "Menu Import";
//     }
//     else {
//       document.getElementById("loadPage").innerHTML = "{% include 'konfig_form.html' %}";
//       document.getElementById("title-menu").innerHTML = "Menu Konfigurasi";
//     }
//
//
// this.location.reload()
// }
