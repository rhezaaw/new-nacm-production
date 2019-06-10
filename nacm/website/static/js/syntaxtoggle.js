$(document).ready(function() {
    $("#cbp-spmenu-s4").hide();})
			// var menuBottom = document.getElementById( 'cbp-spmenu-s4' ),
        showBottom = document.getElementById('showBottom'),
        closeBottom = document.getElementById('closeBottom',)
			// 	body = document.body;

			showBottom.onclick = function() {
				// classie.toggle( this, 'active' );
				// classie.toggle( menuBottom, 'cbp-spmenu-open' );
        $('#cbp-spmenu-s4').show("slide",{ direction: "up" },1000);
			};
      closeBottom.onclick = function() {
				// classie.toggle( this, 'active' );
        // cbp-spmenu-s4
        // $('#cbp-spmenu-s4').hide("fade",1000);
				// classie.toggle( menuBottom, 'cbp-spmenu-close' );
        $('#cbp-spmenu-s4').hide("slide",{ direction: "down" },1000);
			};

$("#cbp-spmenu-s4").resizable({
    stop: function(event, ui){
      var height_s4 = ui.size.height;
      $("#s4_code").height(height_s4);
      console.log(height_s4);
    },
    handles: 'n, s'
});

hljs.initHighlightingOnLoad();