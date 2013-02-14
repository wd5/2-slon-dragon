$(function(){
    // fancybox

    $('.fancybox').fancybox();
    $('.sels select').live('change', function(){
        EmsPrice($(this).val());
    });
    $('.sels select').selectbox();
    $('.auth_lnk').live('click', function(){
        $('.overlay').height(Math.max($('body').height(),$('.wrapper-out').height()));
        $('.window-out').offset({'top':$('.window-out').offset().top + (document.body.scrollTop || document.pageYOffset )});
        $('.overlay').fadeIn(200);
        return false;
    });
    $('.window-close').live('click', function(){
        $('.overlay').fadeOut(200, function(){
            $('.window-out').offset({'top':0});
        });
        return false;
    });

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

	$('.accord-lnk').live('click', function() {
		el=$(this);
		if (!el.is('.current')) {
			$($('.current.accord-lnk').attr('href')).slideUp(200, function(){
				$('.current.accord-lnk').removeClass('current');
				el.addClass('current');
				$(el.attr('href')).slideDown(200);
			});
		};
		return false;
	});
	function slider_initCallback(carousel) {
	    jQuery('.ctrl').bind('click', function() {
	        carousel.scroll(jQuery.jcarousel.intval($(this).index('.slider-ctrls span')+1));
			$('.ctrl').removeClass('current');
	        $(this).addClass('current');
	        return false;
	    });
	};
	function slider_animationStepCallback(carousel, li, index) {
		$('.ctrl').removeClass('current');
		$('.ctrl').eq(index-1).addClass('current');
	}
	$('.slider ul').jcarousel({
		initCallback: slider_initCallback,
		itemVisibleInCallback:slider_animationStepCallback
	});
	$('.items-slider ul').jcarousel();
	$('input:checkbox').each(function(index,el){
		$(el).hide();
		var cls = 'i-checkbox';
		var dv;
		if ($(el).is(':checked')) {
			cls += ' i-on';
		}
		$(el).after('<div class="'+cls+'" data-id="'+$(el).attr('id')+'""><a href="#"></a></div>');
		$(el).parent().find('div a').bind('click', function(){
			el.checked=!el.checked;
			if (el.checked) {
				$(this).parent().addClass('i-on');
			} else {
				$(this).parent().removeClass('i-on');
			}
			return false;
		});
	});
	$('input:radio').each(function(index,el){
		$(el).hide();
		var cls = 'i-radio';
		var dv;
		if ($(el).is(':checked')) {
			cls += ' i-on';
		}
		dv = $(el).after('<div class="'+cls+'" data-id="'+$(el).attr('name')+'""><a href="#"></a></div>');
		$(el).parent().find('div a').bind('click', function(){
			$('input[name='+$(el).attr('name')+']').parent().find('div').removeClass('i-on');
			el.checked = true;
			$(this).parent().addClass('i-on');
			return false;
		});
	});
	$('.up-cart a').live('mouseover', function(){
		el = $(this);
		$('.up-cart-pl-out').show();
		$(this).parent().parent().addClass('submit-hover');
		$('html').bind('mousemove', function(e){
			var x=e.pageX-$('.up-cart-pl').offset().left;
			var y=e.pageY-$('.up-cart-pl').offset().top-$('.up-cart-pl').height()-40;
			if (x<0 || y>0) {
				$('.up-cart-pl-out').css({'opacity':Math.min((100+x)/100,(100-y)/100)});
				if (x<-100 || y>100) {
					$('html').unbind('mousemove');
					$('.up-cart-pl-out').css({'opacity':1});
					$('.up-cart-pl-out').hide();
					el.parent().parent().removeClass('submit-hover');
				}
			} else {
				$('.up-cart-pl-out').css({'opacity':1});
			}
		});
		return false;
	});
	$('.up-help a').live('click', function(){
		$('.up-dropdown-out1').slideToggle();
		if ($(this).parent().parent().is('.submit-hover')) {
			$(this).parent().parent().removeClass('submit-hover');
		} else {
			$(this).parent().parent().addClass('submit-hover');
		}
		return false;
	});
	$('.cats-curr i').live('click', function(){
		el = $(this);
		if (el.parent().parent().is('.focused')){
			el.parent().parent().removeClass('focused');
		} else {
			el.parent().parent().addClass('focused');
		}
		return false;
	});


    function create_img_fly(el)
    {
        var img = el.html();
        var offset = el.find('img').offset();
        element = "<div class='img_fly'>"+img+"</div>";
        $('body').append(element);
        $('.img_fly').css({
            'position': "absolute",
            'z-index': "1000",
            'left': offset.left,
            'top': offset.top
        });

    }

    //Добавление товара в корзину

    $('.add_product_to_cart').live('click', function(){
        var el = $(this);
        var product_id = el.find('.product_id').val();
        var product_count = el.parent().parent().parent().find('.item_count_curr').val();
        if (!product_count) {
            product_count = el.parent().parent().parent().find('.item_count_curr').text();
        }
        _tocart = el.is('._tocart')
        if (_tocart) {
            product_count = parseInt(el.parent().parent().parent().find('input').val());
        }

        if (product_id && product_count){
            $.ajax({
                type:'post',
                url:'/add_product_to_cart/',
                data:{
                    'product_id':product_id,
                    'product_count':product_count,
                    'tocart':_tocart
                },
                success:function(data){
                    $('.img_fly').remove();
                    if (_tocart){
                        create_img_fly(el.parent().parent().parent().parent().parent().find('.product_img'));
                        bt = el.parent().parent().parent().find('.product_count input')
                        bt.parent().append('<input type="button" value="'+parseInt(bt.val())+' шт." class="count" />')
                        bt.remove();
                    } else {
                        create_img_fly(el.parent().parent().parent().parent().parent().find('.item_img'));
                    }



                    var fly = $('.img_fly');
                    var left_end = $('.blk_cart').offset().left;
                    var top_end = $('.blk_cart').offset().top;

                    fly.animate(
                        {
                            left: left_end,
                            top: top_end
                        },
                        {
                            queue: false,
                            duration: 600,
                            easing: "swing"
                        }
                    ).fadeOut(600);

                    setTimeout(function(){
                        animate_cart(data);
                    } ,600);

                },
                error:function(data){

                }
            });
        }

    });
    $('#buy_submit').live('click', function(){
        el = $(this);
        $.ajax({
            type:'post',
            url:'/cart/add_product_to_cart/',
            data:{
                product_id:el.attr('data-num')
            },
            success:function(data){
                //TODO: ajax на подгрузку блока корзины сверху
                $('.img_fly').remove();
                create_img_fly($('.item-img-zl'));


                var fly = $('.img_fly');
                var left_end = $('.up-cart').offset().left;
                var top_end = $('.up-cart').offset().top;

                fly.animate(
                    {
                        left: left_end,
                        top: top_end
                    },
                    {
                        queue: false,
                        duration: 600,
                        easing: "swing"
                    }
                ).fadeOut(600);
                CartBlockLoad();

//                    setTimeout(function(){
//                        animate_cart(data);
//                    } ,600);
            }
        });
        return false;
    });

    $('.cart-del-lnk').live('click', function(){
        el = $(this);
        $.ajax({
            type:'post',
            url:'/cart/delete_product_from_cart/',
            data:{
                cart_product_id:el.attr('data-num')
            },
            success:function(data){
                el.parent().parent().addClass('cart_deleted');
                CartBlockLoad();
            },
            error: function(){

            }
        })
        return false;
    });

    $('.cart-cost .submit a').live('click',function(){
        el = $(this);
        $('.cart-cost .submit a.current').removeClass('current');
        el.addClass('current');
        input = $('.cart_change_cnt').find('input');
        price = $('.cart_change_cnt').find('.price_cnt');
        total = $('.cart_change_cnt').find('.total_cnt');
        $('.cart_change_cnt').show().offset({top:el.offset().top-20,left:el.offset().left-$('.cart_change_cnt').width()/2});
        input.val(el.text());
        price.text(el.parent().parent().parent().parent().find('.cart-price').text());
        total.text(price_to_str(parseInt(price.text().replace(' ',''))*parseInt(el.text()))+' ₷');
        input.focus();
        return false;
    });

    $('.cnt_cancel').live('click', function(){
        $('.cart_change_cnt').hide();
        $('.cart-cost .submit a.current').removeClass('current');
        return false;
    });

    $('.cnt_save').live('click', function(){
        el = $('.cart-cost .submit a.current');
        input = $('.cart_change_cnt').find('input');
        total = $('.cart_change_cnt').find('.total_cnt');
        $.ajax({
            type:'post',
            url:'/cart/change_cart_product_count/',
            data:{
                cart_product_id:el.attr('data-num'),
                new_count:input.val()
            },
            success:function(data){
                el.text(input.val());
                el.parent().parent().parent().parent().find('.cart-total').text(total.text());
                $('.cart_change_cnt').hide();
                $('.cart-cost .submit a.current').removeClass('current');
                CartBlockLoad();
            }
        });
        return false;
    });

    $('.cart_change_cnt').find('input').live('change', function(){
        input = $('.cart_change_cnt').find('input');
        if (isNaN(+input.val())||(input.val()<0)) {
            input.val(0);
        }
        price = $('.cart_change_cnt').find('.price_cnt');
        total = $('.cart_change_cnt').find('.total_cnt');
        total.text(price_to_str(parseInt(price.text().replace(' ',''))*parseInt(input.val()))+' ₷');
    });

    $('.min_cnt, .add_cnt').live('click', function(){
        input = $('.cart_change_cnt').find('input');
        if ($(this).is('.add_cnt')) {
            input.val(parseInt(input.val())+1);
        } else {
            if (input.val() > 0) {
                input.val(parseInt(input.val())-1);
            }
        }
        price = $('.cart_change_cnt').find('.price_cnt');
        total = $('.cart_change_cnt').find('.total_cnt');
        total.text(price_to_str(parseInt(price.text().replace(' ',''))*parseInt(input.val()))+' ₷');
    });

    $('.cart_overlay a').live('click', function(){
        el = $(this);
        $.ajax({
            type:'post',
            url:'/cart/restore_product_to_cart/',
            data:{
                cart_product_id:el.attr('data-num')
            },
            success:function(data){
                el.parent().parent().parent().parent().removeClass('cart_deleted');
                CartBlockLoad();
            }
        });
        return false;
    });

    $('#order_form_submit').live('click', function(){
        $('.order_form').submit();
        return false;
    })

    $('.check-post').live('click', function(){
        el = $(this);
        $('.check-post').removeClass('current');
        el.addClass('current');
        el.parent().find('input').val(el.attr('data-num'));
        $('.check-col.current').removeClass('current');
        $('.col_'+el.attr('data-num')).addClass('current');
        if (el.attr('data-num') == 'carting') {
            $('.only_carting .radio_overlay').hide();
        } else {
            $('.only_carting input')[0].checked = false;
            $('.only_carting .i-on').removeClass('i-on');
            $('.only_carting .radio_overlay').show();
        }
        return false;
    })
});


// обновление корзины
function CartBlockLoad(){
    $.ajax({
        type:'post',
        url:'/cart/refresh_cart/',
        data:{
            type:'short'
        },
        success:function(data){
            $('.up-cart').html(data);
            if ($('.tocheck-cost').size()) {
                $('.tocheck-cost').text($('.up-cart-cnt span').text());
            }
        }
    });
    $.ajax({
        type:'post',
        url:'/cart/refresh_cart/',
        data:{
            type:'drop'
        },
        success:function(data){
            $('.up-cart-pl-out').html(data);
        }
    });
}


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
                $('.col_country input[name="delivery_price"]').val(data);
                $('.col_country input[name="delivery_price"]').show().parent().find('b').remove();
            }
        },
        error:function(jqXHR,textStatus,errorThrown){
            $('.ems_div').hide();
            $('input[name="cart_submit"]').attr('disabled', 'disabled');
        }
    });
}


function price_to_str(price){
    return String(price).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ');
}