$(document).ready(function(){
	$('#commentForm').submit(function(){
        $('#commentForm').ajaxSubmit({success:after_comment,dataType:'json',resetForm:true});
        $('#submitBT').hide();
        $('#loading').show();
        return false;
    });
    getValidateCode();
    $(".entry_comment").corner();
    $("fieldset").corner();
});
function getValidateCode(){
    $.get("/validate_code/",null,function(text){$('#validate_code').html(text)});
}
after_comment = function(data){
    if(data.result == 'fail'){
        alert(data.message);
    }else{
        var comment = data.comment;
        var cmt = '<div class="entry_comment"><a name="' + comment.id + '"/>';
        if(comment.link)
            cmt += '<div class="metadata"><a href="' + comment.link + '"> ' + comment.author + ' </a>';
        else
            cmt += '<a href="#">' + comment.author + '</a>'
        cmt += '在' + comment.time + '说：' + comment.title + '</div>';
        cmt += '<div>'+ comment.content + '</div>';
        cmt_j = $(cmt);
        cmt_j.hide();
        $('.comment_list').append(cmt_j);
        cmt_j.corner();
        cmt_j.fadeIn(1000);
        
        $('.comment_list h3').html('评论（' + comment.count + '条）');
    }
    getValidateCode();
    $('#loading').hide();
    $('#submitBT').show();
}
