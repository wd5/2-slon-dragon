$(function(){

// fancybox

    $('.fancybox').fancybox();

    function OpenFancyLoading(){
        $.fancybox.showLoading();
        $.fancybox.helpers.overlay.open({closeClick : false,css: {'background' : 'rgba(0, 0, 0, 0.45)'}});
    }

    function CloseFancyLoading(){
        $.fancybox.hideLoading();
        $.fancybox.helpers.overlay.close();
    }

    $('.fancybox-modal').fancybox({
        padding: '0px',
        scrolling: 'true',
        openEffect : 'elastic',
        closeEffect : 'elastic',
        fitToView: false,
        helpers: {overlay: {css: {'background' : 'rgba(0, 0, 0, 0.45)'}}}
    });

    $('.fancybox-media').fancybox({
        padding:0,
        helpers : {
            media : {}
        }
    });

});

// вычисления по EMS
function EmsPrice(city){
    $.ajax({
        url: "/cart/ems_calculate/",
        data: {
            city: city
        },
        type: "POST",
        beforeSend: function ( xhr ) {
            if ($('.ems_div').is(':hidden')) {
            } else {
                $('.ems_price').html('<img src="/media/img/ajax-loader.gif">');
            }
        },
        success: function(data)
        {
            if (data=="NotFound"){
                $('.ems_div').html('Неверно выбран город').show();
                $('input[name="cart_submit"]').attr('disabled', 'disabled');
            } else {
                $('.ems_div').html('Доставка: <span class="ems_price"></span> руб.').show();
                $('.ems_price').html(data);
                $('input[name="delivery_price"]').val(data);
                $('input[name="cart_submit"]').removeAttr('disabled');
            }
        },
        error:function(jqXHR,textStatus,errorThrown){
            $('.ems_div').hide();
            $('input[name="cart_submit"]').attr('disabled', 'disabled');
        }
    });
}