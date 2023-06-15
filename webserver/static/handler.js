/**
 * 预加载屏幕
 */
$(window).on('load', 
    function() {
        $('#status').fadeOut();                     // 首先淡出加载动画
        $('#preloader').delay(500).fadeOut('slow'); // 淡出覆盖网站的白色 DIV 
        checkTouchScreen();                         // 检查设备是否具有触摸屏
    }
);

$(document).ready(function() {

    /**
     * 单击播放按钮
     */
    $("#player").click(function(){
        // 创建一个将发送到服务器的 JSON 文件，指示已单击播放箭头
        var action = {"button":"player"};
        // 发送变量
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/_post_data',
            dataType : 'json',
            data : JSON.stringify(action),
            success : function(result) {
                // 根据状态更改符号
                changeSong(result['data']);
                $("#player").text( ((result['data'][0]['playing'] == true) ? "pause":"play_arrow") );
                console.log('Well received signal'); 
            },error : function(result){
                console.log(result);
            }
        });
    });

    /**
     * 单击下一首或上一首歌曲
     */
    $("#prev, #next").click(function(){
        // 创建一个将发送到服务器的 JSON 文件，指示单击了哪个按钮
        if($(this).attr("id") == "prev"){
            var simb = "prev";
        } else{
            var simb = "next";
        }
        var action = {"button":simb};
        // 发送变量
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/_post_data',
            dataType : 'json',
            data : JSON.stringify(action),
            success : function(result) {
                changeSong(result['data']);
                console.log('Well received signal'); 
            },error : function(result){
                console.log(result);
            }
        });
    });

    /**
     * 通过列表选择新歌曲
     */
    $(".song").click(function(){
        var action = {
            "button":"new_song",
            "song":$(".list-info",this).attr("id")
        };
        console.log(action);
        // 发送变量
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/_post_data',
            dataType : 'json',
            data : JSON.stringify(action),
            success : function(result) {
                changeSong(result['data']);
                console.log('Well received signal'); 
            },error : function(result){
                console.log(result);
            }
        });
    });

    /**
     * 更改当前歌曲的可视化信息。
     *@param {dict} result : 服务器返回的数据。它包含正在播放的新歌曲的信息
     */
    function changeSong(result){
        var current_song = result[0]['current_song'];
        if ( ($(".main_cover").attr("id")) != current_song ){
            // 新歌曲，新ID
            $(".main_cover").attr("id",current_song)
            // 更改图像
            $(".main_cover").attr("style", newCover(current_song, true));
            // 更改歌曲标题
            $(".current-info h1").text(result[1][current_song]['title'])
            // 更改歌曲艺术家
            $(".current-info p").text(result[1][current_song]['artist'])
            $("#player").text("pause");
        }
    }

    /**
     * 获取新的封面
     * @param {int} index : 要使用的封面的索引
     * @param {bool} main_cover : 是否更改当前歌曲的封面。在我们的应用中，它始终为true
     */
    function newCover(index, main_cover){
        var new_cover_style = "";
        if (main_cover == true){
            new_cover_style = (
                "background: url('static/covers/"+ index + ".jpg');\n" + 
                "background-size: cover;\n" +
				"position: relative;\n" +
				"z-index: 2;\n" +
				"width: 132px;\n" +
				"height: 132px;\n"+
				"border-radius: 4px;"
            );
        } else{
			new_cover_style = (
                "background: url('static/covers/{{ i }}.jpg');\n" +
                "background-size: cover;\n" +
				"position: relative;\n" +
				"z-index: 2;\n" +
				"width: 132px;\n" +
				"height: 132px;\n"+
				"border-radius: 4px;"
            );
        }
        return new_cover_style;
    }
});

function checkTouchScreen() {
    if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
        $('body').addClass('touch-screen');
        return true;
    } else {
        $('body').removeClass('touch-screen');
        return false;
    }
}


$(document).ready(function() {


    /**
     * 修改音量
     */
    $("#volume").change(function() {
        var volume = $(this).val();
        var action = {
            "button": "volume",
            "volume": volume
        };

        // 发送请求给服务器，更新音量
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            url: '/set_volume',
            dataType: 'json',
            data: JSON.stringify(action),
            success: function(result) {
                console.log('Volume set to: ' + volume);
            },
            error: function(result) {
                console.log(result);
            }
        });
    });
});

