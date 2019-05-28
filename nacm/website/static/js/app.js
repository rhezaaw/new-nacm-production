var s = $("#status").val();
if (s=='success'){
    $('#myModal').modal('show');
}

function sendData(id){
    console.log(id);
    $("#btn-delete").attr("href", "/setting/delete/"+id);
}
