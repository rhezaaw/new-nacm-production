  function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+)');
    console.log(prefix+'prefixs');
    var replacement = prefix + '-' + ndx;
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}
function cloneMore(selector, prefix) {
    var newElement = $(selector).clone(true);
    var total = $('#id_' + prefix + '-TOTAL_FORMS').val();
    console.log(total+'add');
    newElement.find(' :input').each(function() {
        var name = $(this).attr('name');
        if(name) {
            name = name.replace('-' + (total-1) + '-', '-' + total + '-');
            var id = 'id_' + name;
            $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
        }
    });
    newElement.find('#verif-koneksi-' + (total - 1)).each(function() {
      $(this).text('');
      this.id ='verif-koneksi-' + total;
    });
    total++;
    $('#id_' + prefix + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
    var conditionRow = $('.form-row:not(:last)');
    conditionRow.find('.btn.add-form-row')
    .removeClass('btn-success').addClass('btn-danger')
    .removeClass('add-form-row').addClass('remove-form-row')
    .html('-');
    return false;
}
function deleteForm(prefix, btn, selector) {
    var countBox = 0;
    countBox -= 1;
    var total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    console.log(total+'delete');
    var newElement = $(selector).clone(true);
    // var verif_koneksi = document.getElementsByClassName("verif_koneksi");
    // verif_koneksi.parentNode.removeChild(verif_koneksi);
    // document.querySelectorAll('.verif_koneksi').forEach(function(p) {
    //   p.remove()
    // })
    // var elems = document.getElementsByClassName("verif_koneksi");
    // console.log(elems.length)
    // var k = elems.length-1;
    // var parent = elems[k].parentNode;
    // parent.removeChild(elems[k]);
    // for (var k = elems.length - 1; k >= 0; k--) {
    //   var parent = elems[k].parentNode;
    //   parent.removeChild(elems[k]);
    // }

    // newElement.find('#verif-koneksi-' + (total - 1)).each(function() {
    //   $(this).text('');
    //   this.id ='verif-koneksi-' + total;
    // });
    // total--;

    if (total > 1){
        btn.closest('.form-row').remove();
        var forms = $('.form-row');
        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
        // console.log(prefix);
        var i = 0;
        for (var i=0, formCount=forms.length; i<formCount; i++) {
          // console.log(i);
            $(forms.get(i)).find(':input').each(function() {
                // console.log(i+'atas');
                updateElementIndex(this, prefix, i);
                // console.log(prefix);
                // console.log(i);
            });
        }
        console.log(i+'asdas');
        console.log(total+'cek total bawah');
        var delVerif = document.getElementById('verif-koneksi-' + (total-1));
        delVerif.parentNode.removeChild(delVerif);

        var addVerif = document.createElement("P");
        numberOfVerifClass = document.getElementsByClassName("verif_koneksi").length
        console.log(total+'verif')
        addVerif.setAttribute("id", "verif-koneksi-" + (i-1));
        document.getElementsByClassName("verif_koneksi")[numberOfVerifClass-1].appendChild(addVerif);
    }
    return false;
}

function testF(){
  var e = $('id_ipaddr')
  var x = document.getElementById('test2');
  x.style.background="black"
}

var count = 0;
function countplus(){
    count += 1;
}

$(document).on('click', '.add-form-row', function(e){
    e.preventDefault();
    cloneMore('.form-row:last', 'form');
    countplus();
    return false;
});


$(document).on('click', '.remove-form-row', function(e){
    e.preventDefault();
    deleteForm('form', $(this));
    return false;
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});



$(document).ready(function() {
  var zxc = []
  for (i=0;i<9;i++){
    zxc[i]='input#id_form-'+i.toString()+'-ipaddr'
    // console.log(zxc[i]);
    // var _this = $(this).val();
    var timer = null;
    $(zxc[i]).focusout(function() {
        var iplist = $(this);
        var self = this;
        clearTimeout(timer);
        timer = setTimeout(function() {
          console.log(iplist.val());
          $.ajax({
            url : '/ip_validation',
            type : 'POST',
            data : {
            'iplist' : iplist.val()},
            beforeSend : function(xhr, settings) {
              console.log("Before Send");
              $.ajaxSettings.beforeSend(xhr, settings);
            },
            dataType : 'json',
            success : function(data){
              // data = JSON.parse(data);
              console.log("success");
              // var id = Number.parseInt(self.id.charAt(8));
              var id = self.id
              var id_number = id.split('-');
              // console.log(self.id.charAt(8));
              // console.log(self.id);
              // console.log(id3[1]);
              var concolor = document.getElementById("verif-koneksi-"+(id_number[1]));
              if(data['respon_koneksi'].match(/up/i)){
                concolor.style.color = "green";
              }else if(data['respon_koneksi'].match(/down/i)){
                concolor.style.color = "red";
              }
              document.getElementById("verif-koneksi-"+(id_number[1])).innerHTML = data['respon_koneksi'];
            }
          });
        });

    });

  }
});

$('#files').change(function (e) {
  var files = [];
  for (var i = 0; i < $(this)[0].files.length; i++) {
      files.push($(this)[0].files[i].name);
  }
  $(this).next('.custom-file-label').html(files.join(', '));
});


