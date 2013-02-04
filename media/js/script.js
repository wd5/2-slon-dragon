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

});